# -*- coding: utf-8 -*-
"""Lucky Project Milestone 2.1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NEh2pO_b8XxK3wbUSF-8Rrbz4QVg6yK-
"""

import streamlit as st
import openai
import os
# Set up your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')
# Initialize Streamlit
st.title("Legal Alexi")
# Create a text input field for user queries
user_input = st.text_input("Ask a question:")
# Send the user's query to OpenAI GPT-3
if user_input:
    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=user_input,
    max_tokens=50
    )
    st.write(response['choices'][0]['text'].strip())


!pip install streamlit -q
!pip install langchain -q
!pip install pypdf -q
!pip install openai==0.28 -q
!pip install tiktoken -q
!pip install faiss-cpu -q
!pip install nltk -q
!pip install pandas -q

import nltk
nltk.download('punkt')

from google.colab import drive
drive.mount('/content/drive/')

config_ini_location = '/content/drive/MyDrive/Colab Notebooks/config.ini' # Change this to point to the location of your config.ini file.

import configparser

config = configparser.ConfigParser()
config.read(config_ini_location)
openai_api_key = config['OpenAI']['API_KEY']

model_name="gpt-3.5-turbo-0613" # Do Not change this!

# syllabus_corpus_path = "/content/drive/MyDrive/Colab Notebooks/testdata"

from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Path to your PDF directory
syllabus_corpus_path = "/content/drive/MyDrive/Colab Notebooks/testdata"

# Initialize the PDF loader
pdf_loader = PyPDFDirectoryLoader(syllabus_corpus_path)

# Load documents
documents = pdf_loader.load()

# Check if any documents are loaded
print(f"Number of documents loaded: {len(documents)}")

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 750,
    chunk_overlap = 100
)

chunks = pdf_loader.load_and_split(text_splitter)

import faiss
from langchain.vectorstores import FAISS

import faiss
from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

db = FAISS.from_documents(chunks,embeddings)

from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

chain = load_qa_chain(OpenAI(openai_api_key=openai_api_key), chain_type="stuff")

query = "Who published the City code?"
docs = db.similarity_search(query, k =2)

result = chain.run(input_documents = docs, question = query)

print(result)

# query = "What is the limitation on campaign spending in city preliminary elections and city elections?"

docs = db.similarity_search(query)

print(docs[0].page_content)

import faiss
import openai
import numpy as np
import configparser

# Location of your config.ini file
config_ini_location = '/content/drive/MyDrive/Colab Notebooks/config.ini'

# Read the API key from the config file
config = configparser.ConfigParser()
config.read(config_ini_location)
openai_api_key = config['OpenAI']['API_KEY']

# Set the OpenAI API key
openai.api_key = openai_api_key

# Function to get embeddings using OpenAI
def get_openai_embedding(text):
    response = openai.Embedding.create(input=text, engine="text-similarity-babbage-001")
    return np.array(response['data'][0]['embedding'])

# Assuming 'chunks' is a list of text chunks from your previous step

# Calculate embeddings for each chunk
embeddings = [get_openai_embedding(chunk) for chunk in chunks]

# Create a FAISS index
dimension = len(embeddings[0])  # Dimension of the embeddings
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(np.array(embeddings))

# Function to search in the index
def search(query):
    query_embedding = get_openai_embedding(query)
    distances, indices = index.search(np.array([query_embedding]), k=1)  # k is the number of nearest neighbors
    return chunks[indices[0][0]]

# Example usage
query = "What is Councilor Worrell's first name?"
answer_chunk = search(query)
print(answer_chunk)

"""**Function to Summarize**"""

# Function to summarize a given text chunk
def summarize_chunk(chunk):
    if len(chunk) > 1000:  # Trimming if too long
        chunk = chunk[:1000] + '...'

    prompt = f"Summarize the following text:\n{chunk}\n\nSummary:"
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            temperature=0.8,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

# Example of using the summarization function on each chunk
if chunks:
    for chunk in chunks:
        summarized_text = summarize_chunk(chunk)
        if summarized_text:
            print("Summarized Text:", summarized_text)
        else:
            print("No summary generated.")
else:
    print("No chunks found.")

# Function to summarize user-provided text
def summarize_user_input(input_text):
    if len(input_text) > 1000:  # Trimming if too long
        input_text = input_text[:1000] + '...'

    prompt = f"Please provide a brief and concise summary of the following text:\n\n'{input_text}'\n\nSummary:"
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            temperature=0.7,
            max_tokens=30 # Reduced max tokens to focus on conciseness
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

# Example usage of the function with user input
user_input_text = "The global economy is facing multiple challenges as it navigates the post-pandemic era. Economists are particularly concerned about rising inflation rates, supply chain disruptions, and the potential for a widespread recession. These issues are compounded by geopolitical tensions and environmental crises, including climate change and resource depletion. Policy makers are urged to take coordinated action to mitigate these risks and promote sustainable growth."

summarized_text = summarize_user_input(user_input_text)
if summarized_text:
    print("Summarized Text:", summarized_text)
else:
    print("No summary generated.")

for document in documents:
    print(dir(document))
    break  # Only print for the first document to avoid too much output

import os

source_info = []

for document in documents:
    # Extract text from each document
    extracted_text = document.page_content

    # Extract document name and page number from metadata
    document_name = os.path.basename(document.metadata.get('source', 'Unknown Document'))
    page_number = document.metadata.get('page', 'Unknown Page')

    # Split the extracted text into chunks
    chunks = text_splitter.split_text(extracted_text)

    # Store source information for each chunk
    for chunk in chunks:
        source_info.append((document_name, page_number))

def similarity_search(query):
    query_embedding = get_openai_embedding(query)
    distances, indices = index.search(np.array([query_embedding]), k=1)  # k is the number of nearest neighbors
    best_match_index = indices[0][0]
    return chunks[best_match_index], source_info[best_match_index]

# Example usage
query = "What is Councilor Worrell's first name?"
answer_chunk, source = similarity_search(query)
print("Answer:", answer_chunk)
print("Source:", source)

def similarity_search(query):
    query_embedding = get_openai_embedding(query)
    distances, indices = index.search(np.array([query_embedding]), k=5)  # k=5 for top 5 results

    results = []
    for i in range(5):  # Iterate over top 5 results
        chunk_index = indices[0][i]
        similarity_score = distances[0][i]
        chunk = chunks[chunk_index]
        source = source_info[chunk_index]
        results.append((chunk, similarity_score, source))

    return results

# Example usage
query = "Only using the reference text provided (City of Boston Municipal Code) and only answering the question asked to find an answer: what is the first name of the Councilor with last name ""Worrell""?"
top_matches = similarity_search(query)

print("Top 5 Matches:")
for i, (chunk, score, source) in enumerate(top_matches):
    print(f"Match {i+1}: Score = {score}")
    print(f"Chunk: {chunk}")
    print(f"Source: {source}")
    print("--------------------------------------------------")

# Function to get answer from OpenAI
def get_answer_from_openai(question, context):
    openai.api_key = openai_api_key

    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Question: {question}\n\nContext: {context}\n\nAnswer:",
        temperature = 0.3,
        max_tokens=150
    )

    return response.choices[0].text.strip()

# Example usage
query = "What is the shape of the city seal"
context = top_matches[0][0]  # Most relevant chunk
answer = get_answer_from_openai(query, context)

print("Query:", query)
print("Context:", context)
print("Answer from OpenAI:", answer)

temperature =1

from langchain.chat_models import ChatOpenAI

# Create a reference to the language model
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=temperature, model_name=model_name)

def get_answer_from_openai(question, context):
    # Craft a prompt that guides the model to use only the provided context
    prompt = f"Based on the following text, answer the question:\n\nText: {context}\n\nQuestion: {question}\n\nAnswer (using only the above text):"

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature = 0.1,
        max_tokens=150
    )

    return response.choices[0].text.strip()

# Example usage
query = "Who is the publisher of the Boston municipal code?"
context = top_matches[0][0]  # Most relevant chunk
answer = get_answer_from_openai(query, context)

print("Query:", query)
print("Context:", context)
print("Answer from OpenAI:", answer)


def get_answer_from_openai(question, context):
    # Simplified prompt
    prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )

    return response.choices[0].text.strip()

"""Example of Summery

"""

# Example usage
query = "What is Councilor Worrell's first name?"
context = top_matches[0][0]  # Most relevant chunk
answer = get_answer_from_openai(query, context)

print("Query:", query)
print("Context:", context)
print("Answer from OpenAI:", answer)

user_input_text=answer
summarized_text = summarize_user_input(user_input_text)
if summarized_text:
    print("Summarized Text:", summarized_text)
else:
    print("No summary generated.")
