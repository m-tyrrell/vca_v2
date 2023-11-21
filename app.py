import appStore.vulnerability_analysis as vulnerability_analysis
import appStore.doc_processing as processing
from appStore.rag import run_query
from utils.uploadAndExample import add_upload, get_tabs
from utils.vulnerability_classifier import label_dict
import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title = 'Vulnerability Analysis', 
                   initial_sidebar_state='expanded', layout="wide") 

with st.sidebar:
    # upload and example doc
    choice = st.sidebar.radio(label = 'Select the Document',
                            help = 'You can upload your own documents \
                            or use the example document', 
                            options = ('Upload Document', 'Try Example'), 
                            horizontal = True)
    add_upload(choice)

with st.container():
        st.markdown("<h2 style='text-align: center;'> Vulnerability Analysis </h2>", unsafe_allow_html=True)
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
if st.button("Analyze Documents"):
    prg = st.progress(0.0)
    for i, func in enumerate(apps):
        func()
        prg.progress((i + 1) * multiplier_val)

if 'combined_files_df' in st.session_state: # check for existence of processed documents
    # get the filenames from the processed docs dataframe so we can use for tab names
    uploaded_docs = [value for key, value in st.session_state.items() if key.startswith('filename_')]
    tab_titles = get_tabs(uploaded_docs)

    if tab_titles:
        tabs = st.tabs(tab_titles)

        # Render the results (Pie chart, Summary and Table) in indidivual tabs for each doc
        for tab, doc in zip(tabs, uploaded_docs):
            with tab:
                # Main app code
                with st.container():
                    st.write(' ')

                    # Assign dataframe a name
                df_vul = st.session_state['combined_files_df']
                df_vul = df_vul[df_vul['filename'] == doc]

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

                ### Document Summary
                st.markdown("----")
                st.markdown('**DOCUMENT FINDINGS SUMMARY:**')
                
                # filter out 'Other' cause we don't want that in the table (and it's way too big for the summary)
                df_docs = df_vul[df_vul['Vulnerability Label'] != 'Other']
                # construct RAG query, send to openai and process response
                run_query(df_docs)
                
                st.markdown("----")
                
                with st.expander("ℹ️ - Document Text Classifications", expanded=False):
                    ### Table 
                    st.table(df_docs)


