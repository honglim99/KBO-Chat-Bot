import streamlit as st
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.llms.base import LLM
from langchain.schema import Document
import os
import json
import logging
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap



# 임베딩 및 벡터 스토어 로드
def load_vector_store():
    # SentenceTransformer 임베딩 객체 생성
    embedding_function = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    
    # JSON 파일 경로
    json_file = 'kbo_players_2024_combined.json'
    
    # JSON 파일 읽기
    with open(json_file, 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    # LangChain용 문서 리스트 생성
    documents = []
    for player in players_data:
        선수 = player['선수']
        팀명 = player['팀명']
        기록 = player['기록']
        역할 = player['역할']
        
        # 기록을 문자열로 변환
        기록_str = "\n".join([f"{key}: {value}" for key, value in 기록.items()])
        
        # 문서 생성
        document = Document(
            page_content=f"선수: {선수}\n팀명: {팀명}\n기록:\n{기록_str}\n역할: {역할}",
            metadata={"선수": 선수, "팀명": 팀명, "역할": 역할}
        )
        documents.append(document)
    
    # 임베딩 생성 및 벡터 스토어 구축
    vector_store = FAISS.from_documents(documents, embedding_function)
    
    return vector_store

vector_store = load_vector_store()
print(vector_store)

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k':10, 'fetch_k': 100})

# 페이지 설정
st.set_page_config(page_title="KBO 기록 알리미 챗봇", page_icon="⚾", layout="wide")

st.title("KBO 기록 알리미 챗봇 ⚾")
st.write("특정 선수의 기록이나 특정 팀의 선수들 기록을 물어보세요.")
# 사용자 정의 프롬프트 템플릿 정의
template = """
너는 한국 야구 시즌 기록 정보원이야. 모든 대답은 한글로 해야해. 항상 답변 마지막엔 폴리텍 화이팅을 붙여줘
You are an assistant that provides detailed information about KBO players based on the provided records.


Player Information:
{context}

Question: {question}

Answer: """

prompt = ChatPromptTemplate.from_template(template)

# LangChain LLM 및 체인 설정
llm = ChatOllama(model="gemma2:9b", temperature=0, base_url="http://127.0.0.1:11434/") 
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5}),
# )
chain = RunnableMap({
    "context": lambda x: retriever.get_relevant_documents(x['query']),
    "question": lambda x: x['query']
}) | prompt | llm

# 사용자 입력
user_query = st.text_input("질문을 입력하세요:")

# 질문 전송 버튼
if st.button("전송"):
    if user_query:
        with st.spinner("응답 생성 중..."):
            try:
                result = chain.invoke({"query": user_query})
                response = result.content
                st.session_state.history.append({"질문": user_query, "응답": response})
                st.success("응답:")
                st.write(response)
            except Exception as e:
                error_message = f"응답 생성 중 오류 발생: {e}"
                st.error(error_message)
                logging.error(error_message)
    else:
        st.warning("질문을 입력해주세요.")

