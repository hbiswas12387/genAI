from langchain.chains import LLMChain
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
import boto3
import os
import streamlit as st
from io import StringIO

#os.environ["AWS_PROFILE"] = "<iam_profile_name>"

st.set_page_config(page_title="ESG Quest")
st.title("Hi, I am your ESG Data Analyst chatbot !")
st.markdown("Created using AWS Bedrock and prompt engineering...!")

def summarizePrompt_Claude(context):

    prompt_template = """Human: Please read the text:

    context = <text>{context}</text>

    Summarize the document in 5 bullet points. Don't hallucinate.
    Start the answer with only "Below are key summary points: "
    
    Assistant: """

    prompt = PromptTemplate(
        input_variables=["context"],
        template= prompt_template
    )
    return prompt




def qnaPrompt_Claude(context, question):

    prompt_template = """Human: You will be acting as a Data analyst who specilalises in ESG regulations. Use the following <instructions></instructions> to answer the <question></question>. Follow the <output_format></output_format> given below while responding.

    context = <context>{context}</context>

    question = <question>{question}</question>

    instructions = Use following instructions to answer the question above. 

    <instructions>
    instructions = Use following instructions to answer the question above. 
    - Do not hallucinate and answer the question based on the context provided above.    
    - If you still don't have an answer then ignore the context and try to answer the question asked precisely.
    - Complete all the sentences and create a sense of comfort and understanding.
    </instructions>

    <output_format>
    output_format = Provide your output as a text based paragraph that follows the instructions below
    - Each and every sentence is complete, ending with a full stop.
    - All attributes are contained in the answer.
    - Give the answer with the emotion of care and concern for your user.
    - Don't include <paragraph> tags
    </output_format>

    Assistant: """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template= prompt_template
    )
    return prompt





#bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

modelID = "anthropic.claude-v2"
# modelID = "cohere.command-text-v14"


def summarizeFile(context):

    summary_prompt = summarizePrompt_Claude(context)

    llm = Bedrock(
        model_id=modelID,
        client=bedrock_client,
        model_kwargs={"max_tokens_to_sample": 200,"temperature":0.1, "prompt": summary_prompt }
    )

    bedrock_chain = LLMChain(llm=llm, prompt=summary_prompt)

    response=bedrock_chain({'context': context})
    return response




# Upload the ESG Directive document for summarization :

st.sidebar.header('Document Summarizer !')
uploaded_file = st.sidebar.file_uploader("Choose files for getting key summary pointers :")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    stringio = StringIO(uploaded_file.getvalue().decode("latin-1"))
    # To read file as string:
    file_string_data = uploaded_file.read()
    # st.write(file_string_data)
    response = summarizeFile(file_string_data)
    st.sidebar.header('Summary')
    st.sidebar.markdown( response['text'])




# Read the metadata file
metaDataFilePath = '/Users/himanshubiswas/Downloads/esg_metadata.json'
with open(metaDataFilePath, 'rb') as file:
    context = file.read()


question = st.text_area(label="what is your question?", max_chars=100)


def conversationalBot(context, question):

    chat_prompt = qnaPrompt_Claude(context, question)

    llm = Bedrock(
        model_id=modelID,
        client=bedrock_client,
        model_kwargs={"max_tokens_to_sample": 200,"temperature":0.1, "prompt": chat_prompt }
    )

    bedrock_chain = LLMChain(llm=llm, prompt=chat_prompt)

    response=bedrock_chain({'context': context,'question': question})
    return response





if st.button('Ask Me'):
    response = conversationalBot(context, question)
    st.markdown(':bust_in_silhouette: '+ question)
    st.markdown(':robot_face:'+ response['text'])


if st.sidebar.button('Show Meta Data context'):
    st.sidebar.markdown(context)
