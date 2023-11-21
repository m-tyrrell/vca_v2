import streamlit as st
import tempfile
import json

def add_upload(choice):
    if choice == 'Upload Document':
        uploaded_files = st.sidebar.file_uploader('Upload Files', 
                                                  type=['pdf', 'docx', 'txt'], 
                                                  accept_multiple_files=True)
        
        if uploaded_files is not None:
            # Clear previous uploaded files from session state
            for key in list(st.session_state.keys()):
                if key.startswith('filename') or key.startswith('filepath'):
                    del st.session_state[key]

        # Process and store each uploaded file
        for index, uploaded_file in enumerate(uploaded_files):
            with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp:
                bytes_data = uploaded_file.getvalue()
                temp.write(bytes_data)
                st.session_state[f'filename_{index}'] = uploaded_file.name
                st.session_state[f'filepath_{index}'] = temp.name

    else:  # Handle example document selection
        # listing the options
        with open('docStore/sample/files.json', 'r') as json_file:
            files = json.load(json_file)

        option = st.sidebar.selectbox('Select the example document',
                                      list(files.keys()))
        file_name = file_path = files[option]
        st.session_state['filename_0'] = file_name  # Use 'filename_0' to align with the upload naming convention
        st.session_state['filepath_0'] = file_path  # Use 'filepath_0' for consistency


# get the filenames from the processed docs dataframe so we can use for tab names
def get_tabs(uploaded_docs):
    tabs = []
    for doc_name in uploaded_docs:
        tab_title = doc_name  # Assuming doc_name is a string with the file name
        tabs.append(tab_title)
    return tabs

