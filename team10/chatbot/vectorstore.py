from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import pandas as pd
from langchain.document_loaders import CSVLoader
import dotenv
import os
dotenv.load_dotenv()
import time
loader = CSVLoader(file_path="complete_team10_faq.csv", encoding='utf-8-sig')
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

persist_directory = './'
embedding = OpenAIEmbeddings()

# load to disk
vectorstore = Chroma.from_documents(documents=all_splits, embedding=embedding, persist_directory = persist_directory) 


