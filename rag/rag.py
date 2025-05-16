import os
import pandas as pd

from decouple import config

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
)
from langchain_huggingface import HuggingFaceEmbeddings

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')
os.environ['HUGGINGFACE_API_KEY'] = config('HUGGINGFACE_API_KEY')

if __name__ == '__main__':
    folder_path = '/app/rag/data'  # Pasta com os arquivos
    persist_directory = '/app/chroma_data'

    all_docs = []

    # Percorre todos os arquivos da pasta
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.csv'):
            loader = CSVLoader(file_path=file_path, encoding='utf-8')
        elif filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"Formato não suportado: {filename}")
            continue

        docs = loader.load()
        all_docs.extend(docs)

    # Divide os documentos em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(all_docs)

    # Cria o vetor e adiciona os documentos
    embedding = HuggingFaceEmbeddings()
    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
    vector_store.add_documents(chunks)
