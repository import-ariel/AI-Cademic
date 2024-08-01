
import os
import re
import pandas as pd
import numpy as np
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from pydantic import FieldSerializationInfo, validator
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import RegexParser, PydanticOutputParser
from pprint import pprint
import random
import warnings
warnings.filterwarnings(action = "ignore")
import requests
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
import PyPDF2
import dotenv
from langchain_openai import ChatOpenAI
from transformers import OpenAIGPTTokenizer, OpenAIGPTModel
from langchain_openai import OpenAIEmbeddings
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
from pinecone import Pinecone

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

import pdfplumber
import json

embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL,
                                    openai_api_key=my_OpenAI_key, # specify key here or in secrets
                                    disallowed_special=())

# Assuming chunks is a list of strings
def get_embedding(text, model="text-embedding-3-small"):
    '''
    Generating embeddings for the model using OpenAI's small 
    embedding model (defined in requirements.txt)
    '''
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def split_text(text, max_length=8000):
    '''
    Split data into chunks to parse through the model
    '''
    text = text.replace("\n", " ")
    words = text.split()
    chunks = []
    current_chunk = []

    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def save_dict_to_json(dictionary, file_path):
    '''
    Save data to dictionary to pass to vector DB
    '''
    with open(file_path, 'w') as file:
        json.dump(dictionary, file, indent=4)
save_dict_to_json(dic_embed, "dicembed.json")