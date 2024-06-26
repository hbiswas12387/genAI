import boto3
import os
import streamlit as st

# -----------------------------------------------------------------------------------------------------------------------
# Reference: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html
# -----------------------------------------------------------------------------------------------------------------------

# Set up berock clients
client_bedrock_agent = boto3.client(service_name='bedrock-agent-runtime', region_name="us-east-1")
# Pass knowledge base id created via AWS Bedrock service from console
kbId = 'CITVTUBCRO' # Note : I have deleted this KBID


# supported models for KB : https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html 
modelArn = 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'

def retrieveAndGenerate(input):
    return client_bedrock_agent.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kbId,
                'modelArn': modelArn,
                'generationConfiguration': {
                    'inferenceConfig': {
                        'textInferenceConfig' : {
                            'maxTokens': 20 ,
                            'temperature': 0.9 
                            }
                        }
                    } 
                }
            }
        )


st.set_page_config(page_title="RAG Q&A AWS Bedrock")
st.title("A simple Q&A Chatbot using RAG with AWS Bedrock....")
    
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Below markdown code to align reverse chat direction for user & assistant
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


# React to user input
if user_prompt := st.chat_input("What's up? Ask something..."):

    # Display user message in chat message container
    st.chat_message("user").markdown(user_prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Get response from RAG function from user prompt(question)
    with st.spinner('Assistant Typing......'):
        response = retrieveAndGenerate(user_prompt)["output"]["text"]
        print(response)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})




