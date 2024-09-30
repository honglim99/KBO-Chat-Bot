import streamlit as st
import json
import requests
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap



def get_player_data():
    json_file = 'kbo_players_2024_combined.json'
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return None


def main():
    st.set_page_config(page_title="KBO 기록 알리미 챗봇", page_icon="⚾", layout="wide")

    st.title("KBO 기록 알리미 챗봇 ⚾")
    st.write("특정 선수의 기록이나 특정 팀의 선수들 기록을 물어보세요.")

    # 사용자 입력
    user_query = st.text_input("질문을 입력하세요:")

    # 질문 전송 버튼
    if st.button("전송"):
        data = get_player_data()

        documents = []
        for player in data:
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
        embedding_function = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")

        db = FAISS.from_documents(documents, embedding_function)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 5, 'fetch_k': 100})

        if user_query:
            result = db.similarity_search(user_query)
            st.write("DB검색 결과", result[0].page_content)

            llm = ChatOllama(model="gemma2:27b", temperature=0, base_url="http://117.111.249.205:61434/")

            template = """
            특정 선수의 기록을 보여달라고 하면 선수의 모든 기록을 보여주고, 그 선수에 대한 한줄 평을 해줘 한줄 평은 현재 순위를 바탕으로 잘하고 있는지 못하고 있는지 얘기해주면 좋아.
            특정 팀의 선수들의 기록을 물어볼때는 많은 선수들의 기록을 보여주기 위해 기록을 간소화해서 보여줘. 
            그리고 팀에서 선수들의 기록을 보여줄땐 마크다운 테이블 형태로 반드시 보여줘. 투수와 타자 마크다운 테이블은 각각 따로해서 보여줘. 순위가 높은사람으로 5명 보여줘.
            타자는 타율, 경기 수, 홈런, 득점, 타점, OPS만 보여주고 
            투수는 방어율, 경기수, 승, 패, 세이브, 홀드, 이닝, 삼진, WHIP만 보여주면 됨.
            Answer the question as based only on the following context:
            {context}

            Question: {question}
            """

            prompt = ChatPromptTemplate.from_template(template)

            chain = RunnableMap({
            "context": lambda x: retriever.get_relevant_documents(x['question']),
            "question": lambda x: x['question']
            }) | prompt | llm

            question = user_query
            if question:
                response = chain.invoke({'question': question})
                st.markdown(response.content)

if __name__ == "__main__":
    main()