import json
import boto3
from langchain_core.runnables.config import RunnableConfig
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import BedrockChat
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains import RetrievalQA

# ------------------------------------------------------
# Amazon Bedrock - settings

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

modelID = "anthropic.claude-v2"
kbId = "Z79GCJF3Q7"

# ------------------------------------------------------
# LangChain - RAG chain with KB + Prompt engineering ( passing metadata + instructions)

def chatPrompt(context, metadata_context, question):

    prompt_template = """Human: You will be acting as a Data analyst who specilalises in ESG regulations. Use the following <instructions></instructions> to answer the <question></question>. Follow the <output_format></output_format> given below while responding.

    context = <context>{context}</context>
    metadata_context = <metadata_context>{metadata_context}</metadata_context>
    question = <question>{question}</question>

    instructions = Use following instructions to answer the question above. 

    <instructions>
    instructions = Use following instructions to answer the question above. 
    - Do not hallucinate and answer the question based on the context provided above.
    - If the questions are out of context then use your global knowledge to answer.    
    - If the questions are just greetings then ignore context and then greet them.
    - Complete all the sentences and create a sense of comfort and understanding.
    </instructions>

    <output_format>
    - Each and every sentence is complete, ending with a full stop.
    - Give the answer with the emotion of care and concern for your user.
    - Don't include any tags in the response
    - Answer in the format as requested in the question.
    </output_format>

    Assistant: """

    prompt = PromptTemplate(
        input_variables=["context", "metadata_context" "question"],
        template= prompt_template
    )
    return prompt


def summarizePrompt(context):
    prompt_template = """Human: Please read the text:
    context = <text>{context}</text>
    Summarize the text in 3 bullet points in Frequently Asked Questions & Answers format. 
    Each bullet points should be short and precise. 
    Don't hallucinate.
    Start the answer with "Summarizing below key ESG FAQs:"
    Assistant: """

    prompt = PromptTemplate(
        input_variables=["context"],
        template= prompt_template
    )
    return prompt


# Amazon Bedrock - KnowledgeBase Retriever - Get data from S3 KB source
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id= kbId, # Set your Knowledge base ID
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
)

def summarizationResponse(context):
    summary_prompt = summarizePrompt(context)
    model = Bedrock(
        client=bedrock_runtime,
        model_id=modelID,
        model_kwargs={"max_tokens_to_sample": 200,"temperature":0.9 , "prompt": summary_prompt},
    )
    chain = (
        RunnableParallel({"context": lambda x: context})
        .assign(response = summary_prompt | model | StrOutputParser())
        .pick(["response", "context"])
    )
    response = chain.invoke(context)
    return response['response']


def conversationalResponse( question, metadata_context):
    chat_prompt = chatPrompt(retriever, metadata_context, question)
    model = Bedrock(
        client=bedrock_runtime,
        model_id=modelID,
        model_kwargs={"max_tokens_to_sample": 200,"temperature":0.1 , "prompt": chat_prompt},
    )

    # Chain to combine retriever's content and metadata context 
    chain = (
        RunnableParallel({"context": retriever , "metadata_context": lambda x: metadata_context, "question": RunnablePassthrough()})
        .assign(response = chat_prompt | model |  StrOutputParser())
        .pick(["response", "context", "metadata_context"])
    )
    response = chain.invoke(question)
    return response['response']


def getDefaultMetaDataContext():
    defaultMetaDataFilePath = '/Users/himanshubiswas/Documents/workspace/GIT/GenAIProjects/AwsBedrock/genAI/learning/awsBedrock/apps/esgQuestKB/data/metdata.json'
    with open(defaultMetaDataFilePath, 'rb') as file:
        return file.read()

def getSummaryContext():
    defaulSummaryFilePath = '/Users/himanshubiswas/Documents/workspace/GIT/GenAIProjects/AwsBedrock/genAI/learning/awsBedrock/apps/esgQuestKB/data/ESG_Summary_Document.txt'
    with open(defaulSummaryFilePath, 'rb') as file:
        return file.read()


def loadMetadataContext():
    # If default metadata context is not available, then get from the uploaded datapoint metata file
    if 'metadata_context' not in st.session_state:
        st.session_state.metadata_context = getDefaultMetaDataContext()
    return st.session_state.metadata_context


def setChatDirections():
    st.markdown(
            """
        <style>
            .st-emotion-cache-1c7y2kd {
                flex-direction: row-reverse;
                text-align: right;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )


def clear_conversation():
  st.session_state.messages = []

def getSummarizedText():
    with st.spinner('Loading key highlights for you......'):
        setChatDirections()
        return summarizationResponse(getSummaryContext())

# App main page titles & configs ... 
st.set_page_config(page_title="ESG Quest")
st.title("Hi, I am your ESG Data Analyst chatbot!")
st.markdown("Created using AWS Bedrock , KB and some prompt engineering :)!")

# Metadata and chat directions should remain intact..
loadMetadataContext()
setChatDirections()

# Only on page load, summary should be shown and should be shown even when we switch pages
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'page_loaded' not in st.session_state:
    st.session_state.page_loaded = True
    st.session_state.summary = getSummarizedText()
if st.session_state.summary :
    st.sidebar.markdown(st.session_state.summary)

#------------------------------
# Main page controls :
#------------------------------

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if question := st.chat_input("What's up? Ask something..."):

    # set chats role directions in reverse for better look & feel
    setChatDirections()

    # Display user message in chat message container
    st.chat_message("user").markdown(question)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})

    # Get response for user prompt(question)
    with st.spinner('Assistant typing......'):
        response = conversationalResponse( question, st.session_state.metadata_context)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


if st.session_state.messages:
    # Delete chat button should be visible
    st.sidebar.button(':red[Delete Conversations]', on_click=clear_conversation)