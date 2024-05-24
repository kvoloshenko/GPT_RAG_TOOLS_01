from langchain.memory import ConversationBufferMemory
import pprint

HISTORY = {} # Словарь для хранения памяти

# Функция записи истории чата для указанного пользователя
def set_user_history(user_id, question, answer):
  global HISTORY
  memory = ConversationBufferMemory()
  memory.chat_memory.add_user_message(question)
  memory.chat_memory.add_ai_message(answer)
  HISTORY[user_id] = memory

# Функция чтения истории чата для указанного пользователя
def get_user_history(user_id):
  global HISTORY
  m = HISTORY.get(user_id, '*')
  # print(type(m))
  # pprint.pprint(m)
  if m == '*':
    user_id = '*'
    question = '####'
    answer = '####'
    memory = ConversationBufferMemory()
    memory.chat_memory.add_user_message(question)
    memory.chat_memory.add_ai_message(answer)
    c = memory.load_memory_variables({})
  else:
    c = m.load_memory_variables({})
  return c

