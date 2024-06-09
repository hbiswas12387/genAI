import streamlit as st
import json
from io import StringIO

st.set_page_config(page_title="Metadata Uploads")
st.title("Upload the metadata datapoint files!")

uploaded_file = st.file_uploader("Choose files :")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("latin-1"))
    file_content = stringio.read()    
    st.session_state.metadata_context = file_content
    st.success( uploaded_file.name + '  uploaded successfully!')

#View meta data contents : 
if st.sidebar.button('View Uploaded Metadata'):
    st.sidebar.markdown(st.session_state.metadata_context)
    if st.sidebar.button('Hide Metadata Details'):
        st.sidebar.markdown("")


