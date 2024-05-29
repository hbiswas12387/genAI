import streamlit as st
import requests
import json

# The API endpoint created via AWS API Gateway which calls the lambda function internally...
url = 'https://gjxoxk6j10.execute-api.us-east-1.amazonaws.com/dev/genAiTestBedrock'


# Method: 1 Get API response for end point hosted on aws via api gateway
def apiGatewayRequest(url,prompt):
    payload = json.dumps({"prompt": prompt})
    response = requests.post(url, data = payload)
    print(response.text)
    return response


# Method 2 : Below markdown code to align reverse chat direction for user & assistant
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


# Page titles and configs... 
st.set_page_config(page_title="Q&A Chatbot Ruhaansh")
st.title("I am ChatBot Ruhaansh ! :ghost: ")
st.markdown(":copyright: A Simple Q&A Chatbot created by me using AWS Bedrock (Cohere FM) + Lambda + API Gateway + Steamlit")
# Side bar checks... 
st.sidebar.markdown("![GIF Image](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnBmN2didjdsdmZnMWd3M293aHlmNWlnMWdvMXpjdjA5MjNsNWZqaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H9M7lvORlmeFmvGoqY/giphy.gif)")
st.sidebar.title("About me  :monkey_face:  ")
st.sidebar.markdown("I am from India :flag-in: , Enjoying life in :flag-scotland:")
st.sidebar.markdown("I am :seven: years young :panda_face: ")
st.sidebar.markdown("I play guitar :guitar: , I swim.. :swimmer: , and.... I know everything :imp:  ")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if user_prompt := st.chat_input("What's up? Ask something..."):

    # set chats role directions in reverse for better look & feel
    setChatDirections()

    # Display user message in chat message container
    st.chat_message("user").markdown(user_prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Get response from api gateway for user prompt(question)
    with st.spinner('Ruhaansh typing......'):
        response = apiGatewayRequest( url, user_prompt)
        # parse response to json and then extract text
        response = response.json()['generations'][0]['text']

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
