import streamlit as st
import requests
import json
import base64
import sys,os

# Purpose: A simple chatbot created using AWS Bedrock , Lambda, API gateway and Streamlit 

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

# Method 3 : Clear all conversation when called
def clear_conversation():
  st.session_state.messages = []

# Method 4 : Get base64 encoded content of any file
def getEncodedContent(fileName):
    file_ = open(os.getcwd()+fileName, "rb")
    contents = file_.read()
    file_.close()
    return base64.b64encode(contents).decode("utf-8")

# Page titles and configs... 
st.set_page_config(page_title="Q&A Chatbot Ruhaansh")
st.title("I am Ruhaansh, A Chat-Bot ! :ghost: ")
st.markdown("I was created by my dad using AWS Bedrock(Cohere FM),Lambda,API Gateway & Streamlit")

# Side bar controls... 
st.sidebar.markdown(
    f'<img src="data:image/gif;base64,{getEncodedContent("/homePageBot.gif")}" alt="chatbot gif">',
    unsafe_allow_html=True,
)
st.sidebar.title("About me  :monkey_face:  ")
st.sidebar.markdown(" \"I can keep talking the whole day!\" :flag-in: :flag-scotland: :seven: :guitar: :swimmer: :imp:  ")


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

    # Delete chat button should be visible
    st.sidebar.button(':red[Click here to delete our conversations] :man-gesturing-no: ', on_click=clear_conversation)