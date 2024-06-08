from gc import disable
from langchain.chains import LLMChain
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
import boto3
import streamlit as st
from io import StringIO

#bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

modelID = "anthropic.claude-v2"


def summarizePrompt_Claude(context):
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


def qnaPrompt_Claude(context, question):

    prompt_template = """Human: You will be acting as a Data analyst who specilalises in ESG regulations. Use the following <instructions></instructions> to answer the <question></question>. Follow the <output_format></output_format> given below while responding.

    context = <context>{context}</context>

    question = <question>{question}</question>

    instructions = Use following instructions to answer the question above. 

    <instructions>
    instructions = Use following instructions to answer the question above. 
    - Do not hallucinate and answer the question based on the context provided above.    
    - If you still don't have an answer then ignore the context and try to answer the question asked precisely.
    - If the questions are just greetings then ignore context.
    - Complete all the sentences and create a sense of comfort and understanding.
    </instructions>

    <output_format>
    output_format = Provide your output as a text based paragraph that follows the instructions below
    - Each and every sentence is complete, ending with a full stop.
    - All attributes are contained in the answer.
    - Give the answer with the emotion of care and concern for your user.
    - Don't include <paragraph></paragraph> tags
    - Answer in the format as requested.
    </output_format>

    Assistant: """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template= prompt_template
    )
    return prompt


def summarization(context):
    summary_prompt = summarizePrompt_Claude(context)
    llm = Bedrock(
        model_id=modelID,
        client=bedrock_client,
        model_kwargs={"max_tokens_to_sample": 200,"temperature":0.9, "prompt": summary_prompt }
    )
    bedrock_chain = LLMChain(llm=llm, prompt=summary_prompt)
    response=bedrock_chain({'context': context})
    return response


def getDefaultMetaDataContext():
    defaultMetaDataFilePath = '/Users/himanshubiswas/Documents/workspace/GIT/GenAIProjects/AwsBedrock/genAI/learning/awsBedrock/apps/esgQuest/data/esg_metdata_def.json'
    with open(defaultMetaDataFilePath, 'rb') as file:
        return file.read()

def getSummaryContext():
    defaulSummaryFilePath = '/Users/himanshubiswas/Documents/workspace/GIT/GenAIProjects/AwsBedrock/genAI/learning/awsBedrock/apps/esgQuest/data/ESG_Summary_Document.txt'
    with open(defaulSummaryFilePath, 'rb') as file:
        return file.read()


def loadMetadataContext():
    # If default metadata context is not available, then get from the uploaded datapoint metata file
    if 'context' not in st.session_state:
        st.session_state.context = getDefaultMetaDataContext()
    return st.session_state.context


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
        return summarization(getSummaryContext())['text']

# App main page titles & configs ... 
st.set_page_config(page_title="ESG Quest")
st.title("Hi, I am your ESG Data Analyst chatbot!")
st.markdown("Created using AWS Bedrock and prompt engineering...!")

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
        response = conversationalBot(st.session_state.context, question)
        # parse response to extract text
        response = response['text']

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


if st.session_state.messages:
    # Delete chat button should be visible
    st.sidebar.button(':red[Delete Conversations]', on_click=clear_conversation)
