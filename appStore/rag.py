import os
# import json
import numpy as np
import pandas as pd
import openai
from haystack.schema import Document
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential


# Get openai API key
openai.api_key = os.environ["OPENAI_API_KEY"]
model_select = "gpt-3.5-turbo-1106"


# define a special function for putting the prompt together (as we can't use haystack)
def get_prompt(docs):
  base_prompt="The following context is comprised of extracted text from climate policy documents. \
  Provide a single paragraph summary of the extracts. \
  Formulate your answer in the style of an academic report."
  
  # Add the meta data for references
  context = ' - '.join([d.content for d in docs])
  prompt = base_prompt+"; Context: "+context+"; Answer:"
  
  return prompt


# convert df rows to Document object so we can feed it into the summarizer easily
def get_document(df):
    # we take a list of each extract
    ls_dict = []
    for index, row in df.iterrows():
        # Create a Document object for each row (we only need the text)
        doc = Document(
            row['text'],
            meta={
            'filename': row['filename']}
        )
        # Append the Document object to the documents list
        ls_dict.append(doc)

    return ls_dict 


# exception handling for issuing multiple API calls to openai (exponential backoff)
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


# construct RAG query, send to openai and process response
def run_query(df):
    docs = get_document(df)

    '''
    For non-streamed completion, enable the following 2 lines and comment out the code below
    '''
    # res = openai.ChatCompletion.create(model=model_select, messages=[{"role": "user", "content": get_prompt(docs)}])
    # result = res.choices[0].message.content

    # instantiate ChatCompletion as a generator object (stream is set to True)
    response = completion_with_backoff(model=model_select, messages=[{"role": "user", "content": get_prompt(docs)}], stream=True)
    # iterate through the streamed output
    report = []
    res_box = st.empty()
    for chunk in response:
        # extract the object containing the text (totally different structure when streaming)
        chunk_message = chunk['choices'][0]['delta']
        # test to make sure there is text in the object (some don't have)
        if 'content' in chunk_message:
            report.append(chunk_message.content) # extract the message
            # add the latest text and merge it with all previous
            result = "".join(report).strip()
            # res_box.success(result) # output to response text box
            res_box.success(result)






