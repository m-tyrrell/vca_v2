# set path
import glob, os, sys; 
sys.path.append('../utils')
from typing import List, Tuple
from typing_extensions import Literal
from haystack.schema import Document
from utils.config import get_classifier_params
from utils.preprocessing import processingpipeline,paraLengthCheck
import streamlit as st
import logging
import pandas as pd
params  = get_classifier_params("preprocessing")

@st.cache_data
def runPreprocessingPipeline(file_name:str, file_path:str, 
            split_by: Literal["sentence", "word"] = 'sentence',
            split_length:int = 2, split_respect_sentence_boundary:bool = False,
            split_overlap:int = 0,remove_punc:bool = False)->List[Document]:
    """
    creates the pipeline and runs the preprocessing pipeline, 
    the params for pipeline are fetched from paramconfig
    Params
    ------------
    file_name: filename, in case of streamlit application use 
    st.session_state['filename']
    file_path: filepath, in case of streamlit application use st.session_state['filepath']
    split_by: document splitting strategy either as word or sentence
    split_length: when synthetically creating the paragrpahs from document,
                    it defines the length of paragraph.
    split_respect_sentence_boundary: Used when using 'word' strategy for 
    splititng of text.
    split_overlap: Number of words or sentences that overlap when creating
        the paragraphs. This is done as one sentence or 'some words' make sense
        when  read in together with others. Therefore the overlap is used.
    remove_punc: to remove all Punctuation including ',' and '.' or not
    Return
    --------------
    List[Document]: When preprocessing pipeline is run, the output dictionary 
    has four objects. For the Haysatck implementation of SDG classification we, 
    need to use the List of Haystack Document, which can be fetched by 
    key = 'documents' on output.
    """

    processing_pipeline = processingpipeline()

    output_pre = processing_pipeline.run(file_paths = file_path, 
                            params= {"FileConverter": {"file_path": file_path, \
                                        "file_name": file_name}, 
                                     "UdfPreProcessor": {"remove_punc": remove_punc, \
                                            "split_by": split_by, \
                                            "split_length":split_length,\
                                            "split_overlap": split_overlap, \
        "split_respect_sentence_boundary":split_respect_sentence_boundary}})
    
    return output_pre


# def app():
#     with st.container():           
#           if 'filepath' in st.session_state:
#               file_name = st.session_state['filename']
#               file_path = st.session_state['filepath']

              
#               all_documents = runPreprocessingPipeline(file_name= file_name,
#                               file_path= file_path, split_by= params['split_by'],
#                               split_length= params['split_length'],
#               split_respect_sentence_boundary= params['split_respect_sentence_boundary'],
#               split_overlap= params['split_overlap'], remove_punc= params['remove_punc'])
#               paralist = paraLengthCheck(all_documents['documents'], 100)
#               df = pd.DataFrame(paralist,columns = ['text','page'])
#               # saving the dataframe to session state
#               st.session_state['key0'] = df
              
#           else:
#                 st.info("🤔 No document found, please try to upload it at the sidebar!")
#                 logging.warning("Terminated as no document provided")


def app():
    with st.container():
        all_files_df = pd.DataFrame()  # Initialize an empty DataFrame to store data from all files

        for key in st.session_state:
            if key.startswith('filepath_'):
                file_path = st.session_state[key]
                file_name = st.session_state['filename' + key[-2:]]  # Assuming a similar naming convention for filenames

                all_documents = runPreprocessingPipeline(file_name=file_name,
                                                        file_path=file_path, split_by=params['split_by'],
                                                        split_length=params['split_length'],
                                                        split_respect_sentence_boundary=params['split_respect_sentence_boundary'],
                                                        split_overlap=params['split_overlap'], remove_punc=params['remove_punc'])
                paralist = paraLengthCheck(all_documents['documents'], 100)
                file_df = pd.DataFrame(paralist, columns=['text', 'page'])
                file_df['filename'] = file_name  # Add a column for the file name

                all_files_df = pd.concat([all_files_df, file_df], ignore_index=True)

        if not all_files_df.empty:
            st.session_state['combined_files_df'] = all_files_df
        else:
            st.info("🤔 No document found, please try to upload it at the sidebar!")
            logging.warning("Terminated as no document provided")





