import os
import re
import pandas as pd
import numpy as np
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from pydantic import FieldSerializationInfo
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.output_parsers import RegexParser, PydanticOutputParser
from pprint import pprint
import random
import warnings
warnings.filterwarnings(action="ignore")
import requests
import PyPDF2
import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from transformers import OpenAIGPTTokenizer, OpenAIGPTModel
from pinecone import Pinecone
import torch
import ftfy
from tqdm import tqdm
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
# from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
from PIL import Image
import io
from openai import OpenAI
import pdfplumber
import json
from langchain.chains import ConversationalRetrievalChain
import streamlit as st


# Setting up environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
hf_api_key = os.getenv('HUGGING_FACE_API_KEY')
# pinecone_api_key = os.getenv('PINECONE_API_KEY')
# pinecone_api_env = os.getenv('PINECONE_API_ENV')

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', 'd93710f9-1b1a-481d-a30f-ae3578357333')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV', 'gcp-starter')
os.environ['PINECONE_API_ENV'] = PINECONE_API_ENV
os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY

client = OpenAI(api_key=openai_api_key)

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))


myindex=pc.Index('ai-cademic')

with open (r'dicembed.json', 'r') as file:
    dic_embed=json.load(file)


# User question
#user_question="Why does processing multi-model text pose such a challenge for researchers?"

def get_embedding(text, model="text-embedding-3-small"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_llm_answer(question, context, api_key):
    # Validate input parameters
    if not api_key:
        raise ValueError("API key is required")
    if not question:
        raise ValueError("Question is required")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": question + context
            }
        ],
        "max_tokens": 300
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad HTTP status codes

        # Extract the plain text answer from the response
        answer = response.json()['choices'][0]['message']['content'].strip()
        return answer

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


instructions=" Here's some context, only use it if it is relevant to answer the question, if it is not, mention that the information found did not satisfy the need of the user."

#get_llm_answer(question=user_question+instructions,context=answer_context,api_key=openai_api_key)


def process_text(input_text):
    """
    This function takes an input string and then will pass it to another function that actually calls the model.
    :param input_text:
    :return:
    """

    queryresult=myindex.query(
        #namespace="( Default )",
        vector=get_embedding(input_text, model='text-embedding-3-small') ,
        top_k=5,
        include_values=True
    )
    answer_context = dic_embed[queryresult['matches'][0]['id']]

    out_text=get_llm_answer(question=input_text+instructions,context=answer_context,api_key=openai_api_key)
    return out_text


#### Streamlit App
def main():
    st.title("AI-CADEMIC")

    # txt input
    user_input=st.text_input("Hi! I'm AI-CADEMIC! Here to help you learn from Academic Articles. \n What would you like to learn about? ")

    # button to submit text
    if st.button("Submit"):

        with st.spinner("Racking my brain.."):
            response=process_text(user_input)

        # display response
        st.write('Response: ',response)


if __name__=='__main__':
    main()