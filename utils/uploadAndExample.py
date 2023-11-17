import streamlit as st
import tempfile
import json

# def add_upload(choice):
#     """
#     Provdies the user with choice to either 'Upload Document' or 'Try Example'.
#     Based on user choice runs streamlit processes and save the path and name of
#     the 'file' to streamlit session_state which then can be fetched later.

#     """
    
#     if choice == 'Upload Document':
        
#        # if 'filename' in st.session_state:
#           # Delete all the items in Session state
#         #    for key in st.session_state.keys():
#          #       del st.session_state[key]

#         uploaded_file = st.sidebar.file_uploader('Upload the File',
#                             type=['pdf', 'docx', 'txt'])
#         if uploaded_file is not None:
#             with tempfile.NamedTemporaryFile(mode="wb", delete = False) as temp:
#                 bytes_data = uploaded_file.getvalue()
#                 temp.write(bytes_data)
#                 st.session_state['filename'] = uploaded_file.name
#                 st.session_state['filepath'] = temp.name

                
#     else:
#         # listing the options
#         with open('docStore/sample/files.json','r') as json_file:
#             files = json.load(json_file)

#         option = st.sidebar.selectbox('Select the example document',
#                               list(files.keys()))
#         file_name = file_path  = files[option]
#         st.session_state['filename'] = file_name
#         st.session_state['filepath'] = file_path


def add_upload(choice):
    """
    Provides the user with a choice to either 'Upload Document' or 'Try Example'.
    Based on the user choice, it runs Streamlit processes and saves the path and name of
    the files to Streamlit session_state which then can be fetched later.
    """

    if choice == 'Upload Document':
        uploaded_files = st.sidebar.file_uploader('Upload Files', 
                                                  type=['pdf', 'docx', 'txt'], 
                                                  accept_multiple_files=True)
        
        if uploaded_files is not None:
            # Clear previous session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            # Process each uploaded file
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp:
                    bytes_data = uploaded_file.getvalue()
                    temp.write(bytes_data)
                    # Save file info in session_state using the file name as the key
                    st.session_state[uploaded_file.name] = {
                        'filename': uploaded_file.name,
                        'filepath': temp.name
                    }

    else:
        # Listing the options
        with open('docStore/sample/files.json', 'r') as json_file:
            files = json.load(json_file)

        option = st.sidebar.selectbox('Select the example document', list(files.keys()))
        file_name = file_path = files[option]
        st.session_state['filename'] = file_name
        st.session_state['filepath'] = file_path

