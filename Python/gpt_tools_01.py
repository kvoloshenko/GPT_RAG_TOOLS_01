import re
import requests
import codecs
import urllib.request
from bs4 import BeautifulSoup
import tiktoken
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from loguru import logger
import tools_01 as tls
import db_tools_01 as dbt

# Функции для ChatGPT

def get_simple_answer_gpt(system_content, user_content, model, temperature, client):
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return completion  # возвращает ответ

def get_transcript(client, file_name, language="en"):
  logger.debug('get_transcript')
  logger.debug(type(language), f'language={language}')
  # https://platform.openai.com/docs/guides/speech-to-text/transcriptions


  audio_file= open(file_name, "rb")
  transcript = client.audio.transcriptions.create(
    model="whisper-1",
    language=language,
    file=audio_file,
    response_format="text"
  )
  logger.debug(type(transcript),'\n',transcript)
  return transcript

def get_answer_gpt(system_content, user_content, ba, model, temperature, number_relevant_chunks, db_dir_name, client):
  embeddings = OpenAIEmbeddings()
  db = dbt.load_db(ba, embeddings, db_dir_name)
  # Поиск релевантных отрезков из базы знаний
  message_content = dbt.get_message_content(user_content, db, number_relevant_chunks)
  print(f'message_content={message_content}')
  messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Here is the document with information to respond to the client: {message_content}\n\n Here is the client's question: \n{user_content}"}
    ]
  try:
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    answer = completion.choices[0].message.content
    logger.debug(f'answer={answer}')
    return answer
  except Exception as e:  # обработка ошибок openai.error.RateLimitError
      logger.error(f'!!! External error: {str(e)}')
      return f'!!! External error: {str(e)}'


