from langchain.chains import LLMChain
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
import boto3
import os
import streamlit as st

os.environ["AWS_PROFILE"] = "<iam_profile_name>"

#bedrock client

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

#modelID = "anthropic.claude-v2"
modelID = "cohere.command-text-v14"


llm = Bedrock(
    model_id=modelID,
    client=bedrock_client,
    model_kwargs={"max_tokens": 50,"temperature":0.9}
)

def my_chatbot(language,freeform_text):
    prompt = PromptTemplate(
        input_variables=["language", "freeform_text"],
        template="You are a chatbot. You are in {language}.\n\n{freeform_text}"
    )

    bedrock_chain = LLMChain(llm=llm, prompt=prompt)

    response=bedrock_chain({'language':language, 'freeform_text':freeform_text})
    return response

st.set_page_config(page_title="ChatBox Demo Himanshu")
st.title("A simple Chatbot created by Himanshu using AWS Bedrock....")


language = st.sidebar.selectbox("Language", ["english", "spanish"])

if language:
    freeform_text = st.sidebar.text_area(label="what is your question?", max_chars=100)

if st.sidebar.button('Ask Me'):
    response = my_chatbot(language,freeform_text)
    st.write(':bust_in_silhouette: '+ freeform_text)
    st.write(':robot_face:'+ response['text'])
