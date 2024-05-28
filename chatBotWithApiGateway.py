import streamlit as st
import requests
import json


def apiRequest(url,prompt):
    payload = json.dumps({"prompt": prompt})
    response = requests.post(url, data = payload)
    print(response.text)
    return response

st.set_page_config(page_title="Q&A Chatbot via API Gateway")
st.title("A simple Q&A Chatbot by Himanshu using AWS Bedrock + API Gateway")

freeform_text = st.text_area(label="what is your question?", max_chars=100)

if freeform_text:
    response = apiRequest( 'https://gjxoxk6j10.execute-api.us-east-1.amazonaws.com/dev/genAiTestBedrock', freeform_text)
    st.write(response.text)
