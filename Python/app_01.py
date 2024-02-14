import os
import tools_01 as tls
from dotenv import load_dotenv
import requests
import json
from loguru import logger
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()
# Загрузка значений из .env
SYSTEM_DOC_URL = os.environ.get("SYSTEM_DOC_URL") # промпт
logger.debug(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')
sys_url = tls.get_google_url(SYSTEM_DOC_URL)
system_content = tls.load_document_text(sys_url)
logger.debug(f'system_content = {system_content}')

KNOWLEDGE_BASE_URL = os.environ.get("KNOWLEDGE_BASE_URL") # база знаний
logger.debug(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')
knwl_url = sys_url = tls.get_google_url(KNOWLEDGE_BASE_URL)

BA = os.environ.get("BA") # billing account
logger.debug(f'BA={BA}')

def flask_answer_gpt(api_url, system_content, user_content, ba):
    payload = dict({"system_content": system_content, "user_content": user_content, "ba": ba})
    logger.debug(payload)
    url = api_url + '/answer_gpt'
    logger.debug(url)
    headers = {"accept": "application/json", "content-type": "application/json"}
    logger.debug(headers)
    response = requests.post(url, json=payload, headers=headers)
    logger.debug(response.status_code)
    response.raise_for_status()
    if response.status_code == 200:
        result = json.loads(response.text)
        answer = result['answer']
        logger.debug(answer)
    return answer

def create_db(api_url, knowledge_base_url, ba):
    logger.debug('create_db............')
    payload = dict({"knowledge_base_url": knowledge_base_url,  "ba": ba})
    logger.debug(payload)
    url = api_url + '/db_create'
    logger.debug(url)
    headers = {"accept": "application/json", "content-type": "application/json"}
    logger.debug(headers)
    response = requests.post(url, json=payload, headers=headers)
    logger.debug(response.status_code)
    response.raise_for_status()

# app config
st.set_page_config(page_title="Chat with Multi Doc", page_icon="🤖")
st.title("Chat with Multi Doc")

# sidebar
with st.sidebar:
    st.header("Settings")
    API_URL = st.text_input("API URL")

if API_URL is None or API_URL == "":
    st.info("Please enter a API URL")

else:
    with st.sidebar:
        if st.button('Create Db'):
            create_db(API_URL, knwl_url, BA)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Привет! Как я могу тебе помочь?"),
        ]

    # user input
    user_query = st.chat_input("Type your message here...")

    if user_query is not None and user_query != "":
        logger.debug(f'user_query={user_query}')
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        response = flask_answer_gpt(API_URL, system_content, user_query, BA)
        logger.debug(f'responset={response}')
        st.session_state.chat_history.append(AIMessage(content=response))

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    # with st.sidebar:
    #     st.write(st.session_state.chat_history)

