import appStore.vulnerability_analysis as vulnerability_analysis
import appStore.doc_processing as processing
from utils.uploadAndExample import add_upload
import streamlit as st
from utils.vulnerability_classifier import label_dict
import pandas as pd
import plotly.express as px
import os
import json
import numpy as np
from haystack.schema import Document
import openai


# Get openai API key
openai.api_key = os.environ["OPENAI_API_KEY"]


#_______________________________________________________________________________________________

def create_tabs(uploaded_docs):
    tabs = []
    for doc_name in uploaded_docs:
        tab_title = doc_name  # Assuming doc_name is a string with the file name
        tabs.append(tab_title)
    return tabs

# define a special function for putting the prompt together (as we can't use haystack)
def get_prompt(docs):
  base_prompt=prompt_template
  # Add the meta data for references
  context = ' - '.join([d.content for d in docs])
  prompt = base_prompt+"; Context: "+context+"; Answer:"
  return(prompt)

def run_query(docs):
    # instantiate ChatCompletion as a generator object (stream is set to True)
    # response = openai.ChatCompletion.create(model="gpt-3.5-turbo-1106", messages=[{"role": "user", "content": get_prompt(docs)}], stream=True)
    res = openai.ChatCompletion.create(model="gpt-3.5-turbo-1106", messages=[{"role": "user", "content": get_prompt(docs)}])
    output = res.choices[0].message.content
    st.success(output)
    st.markdown("----")


prompt_template="Provide a single paragraph summary of the documents provided below. \
Formulate your answer in the style of an academic report."


#_______________________________________________________________________________________________


st.set_page_config(page_title = 'Vulnerability Analysis', 
                   initial_sidebar_state='expanded', layout="wide") 

with st.sidebar:
    # upload and example doc
    choice = st.sidebar.radio(label = 'Select the Document',
                            help = 'You can upload the document \
                            or else you can try a example document', 
                            options = ('Upload Document', 'Try Example'), 
                            horizontal = True)
    add_upload(choice)




with st.container():
        st.markdown("<h2 style='text-align: center; color: black;'> Vulnerability Analysis </h2>", unsafe_allow_html=True)
        st.write(' ')

with st.expander("ℹ️ - About this app", expanded=False):
    st.write(
        """
        The Vulnerability Analysis App is an open-source\
        digital tool which aims to assist policy analysts and \
        other users in extracting and filtering references \
        to different vulnerable groups from public documents.
        """)

    st.write("""
        What Happens in background?
        
        - Step 1: Once the document is provided to app, it undergoes *Pre-processing*.\
        In this step the document is broken into smaller paragraphs \
        (based on word/sentence count).
        - Step 2: The paragraphs are then fed to the **Vulnerability Classifier** which detects if
        the paragraph contains any references to vulnerable groups.
        """)
                  
    st.write("")



# Define the apps used
apps = [processing.app, vulnerability_analysis.app]

multiplier_val = 1 / len(apps)
if st.button("Analyze Document"):
    prg = st.progress(0.0)
    for i, func in enumerate(apps):
        func()
        prg.progress((i + 1) * multiplier_val)

if 'combined_files_df' in st.session_state:
    uploaded_docs = [value for key, value in st.session_state.items() if key.startswith('filename_')]
    # uploaded_docs = st.session_state['files_data'].keys() 
    tab_titles = create_tabs(uploaded_docs)

    tabs = st.tabs(tab_titles)

    # Render the results, graphs, tables in indidivual tabs
    for tab, doc in zip(tabs, uploaded_docs):
        with tab:
            # Main app code
            with st.container():
                st.markdown("<h2 style='text-align: center; color: black;'> Vulnerability Analysis </h2>", unsafe_allow_html=True)
                st.write(' ')

                # Assign dataframe a name
            df_vul = st.session_state['combined_files_df']
            df_vul = df_vul[df_vul['filename'] == doc]

            # convert df_vul rows to Document object so we can feed it into the summarizer easily
            # we take a list of each extract
            ls_dict = []
            df_docs = df_vul[df_vul['Vulnerability Label'] != 'Other']
            # Iterate over df and add relevant fields to the dict object
            for index, row in df_docs.iterrows():
                # Create a Document object for each row (we only need the text)
                doc = Document(
                    row['text'],
                    meta={
                    'filename': row['filename']}
                )
                # Append the Document object to the documents list
                ls_dict.append(doc)


            col1, col2 = st.columns([1,1])

            with col1:
                # Header
                st.subheader("Explore references to vulnerable groups:")

                # Text 
                num_paragraphs = len(df_vul['Vulnerability Label'])
                num_references = len(df_vul[df_vul['Vulnerability Label'] != 'Other'])
                
                st.markdown(f"""<div style="text-align: justify;"> The document contains a
                        total of <span style="color: red;">{num_paragraphs}</span> paragraphs.
                        We identified <span style="color: red;">{num_references}</span>
                        references to vulnerable groups.</div>
                        <br>
                        In the pie chart on the right you can see the distribution of the different 
                        groups defined. For a more detailed view in the text, see the paragraphs and 
                        their respective labels in the table below.</div>""", unsafe_allow_html=True)
        
            with col2:
                ### Pie chart
                            
                # Create a df that stores all the labels
                df_labels = pd.DataFrame(list(label_dict.items()), columns=['Label ID', 'Label'])
        
                # Count how often each label appears in the "Vulnerability Labels" column
                label_counts = df_vul['Vulnerability Label'].value_counts().reset_index()
                label_counts.columns = ['Label', 'Count']
        
                # Merge the label counts with the df_label DataFrame
                df_labels = df_labels.merge(label_counts, on='Label', how='left')
        
                # Configure graph
                fig = px.pie(df_labels,
                        names="Label", 
                        values="Count",
                        title='Label Counts',
                        hover_name="Count",
                        color_discrete_sequence=px.colors.qualitative.Plotly
                )
                
                #Show plot
                st.plotly_chart(fig, use_container_width=True)

            ### Summary
            st.markdown("----")
            st.markdown('**DOCUMENT SUMMARY:**')
            res_box = st.empty()
            run_query(ls_dict)
            

            with st.expander("ℹ️ - Document Text Classifications", expanded=False):
                ### Table 
                st.table(df_vul[df_vul['Vulnerability Label'] != 'Other'])


