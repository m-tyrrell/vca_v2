import appStore.vulnerability_analysis as vulnerability_analysis
import appStore.doc_processing as processing
from utils.uploadAndExample import add_upload
import streamlit as st
from utils.vulnerability_classifier import label_dict
import pandas as pd
import plotly.express as px

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
    # st.write('**Definitions**')

    # st.caption("""
    #         - **Target**: Targets are an intention to achieve a specific result, \
    #         for example, to reduce GHG emissions to a specific level \
    #         (a GHG target) or increase energy efficiency or renewable \
    #         energy to a specific level (a non-GHG target), typically by \ 
    #         a certain date.
    #         - **Economy-wide Target**: Certain Target are applicable \
    #             not at specific Sector level but are applicable at economic \
    #             wide scale.
    #         - **Netzero**: Identifies if its Netzero Target or not.
    #             - 'NET-ZERO': target_labels = ['T_Netzero','T_Netzero_C']
    #             - 'Non Netzero Target': target_labels_neg = ['T_Economy_C',
    #               'T_Economy_Unc','T_Adaptation_C','T_Adaptation_Unc','T_Transport_C',
    #               'T_Transport_O_C','T_Transport_O_Unc','T_Transport_Unc']
    #             - 'Others': Other Targets beside covered above
    #         - **GHG Target**: GHG targets refer to contributions framed as targeted \
    #                           outcomes in GHG terms.
    #             - 'GHG': target_labels_ghg_yes = ['T_Transport_Unc','T_Transport_C']
    #             - 'NON GHG TRANSPORT TARGET': target_labels_ghg_no = ['T_Adaptation_Unc',\
    #                'T_Adaptation_C', 'T_Transport_O_Unc', 'T_Transport_O_C']
    #             - 'OTHERS': Other Targets beside covered above.
    #         - **Conditionality**: An “unconditional contribution” is what countries \
    #          could implement without any conditions and based on their own \
    #          resources and capabilities. A “conditional contribution” is one \
    #          that countries would undertake if international means of support \
    #          are provided, or other conditions are met.
    #         - **Action**: Actions are an intention to implement specific means of \
    #          achieving GHG reductions, usually in forms of concrete projects.
    #         - **Policies and Plans**: Policies are domestic planning documents \
    #           such as policies, regulations or guidlines, and Plans  are broader \
    #          than specific policies or actions, such as a general intention \ 
    #          to ‘improve efficiency’, ‘develop renewable energy’, etc. \
    #         The terms come from the World Bank's NDC platform and WRI's publication.
    #           """)
    
    #c1, c2, c3 =  st.columns([12,1,10])
    #with c1:
    #    image = Image.open('docStore/img/flow.jpg') 
    #    st.image(image)
    #with c3:
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


# If there is data stored
if 'combined_files_df' in st.session_state:
    with st.sidebar:
        topic = st.radio(
                        "Which category you want to explore?",
                        (['Vulnerability']))
    
    if topic == 'Vulnerability':

        # Assign dataframe a name
        df_vul = st.session_state['combined_files_df']

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
    
        ### Table 
        st.table(df_vul[df_vul['Vulnerability Label'] != 'Other'])

       # vulnerability_analysis.vulnerability_display()
    # elif topic == 'Action':
    #     policyaction.action_display()
    # else: 
    #     policyaction.policy_display()
    #st.write(st.session_state.key0)

