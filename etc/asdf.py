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
        vector_store = FAISS.from_documents(documents, embedding_function)

        return vector_store

vector_store = load_vector_store()


# retriever = vector_store.as_retriever(search_kwargs={'k':10, 'fetch_k': 100})

llm = ChatOllama(model="gemma2:9b", temperature=0, base_url="http://127.0.0.1:11434/")
qa_chain = RetrievalQA.from_chain_type(llm,retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={'k':10, 'fetch_k': 100}))
result = qa_chain({"query": "김도영"})
print(result)