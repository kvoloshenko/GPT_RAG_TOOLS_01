import os
import re
from langchain_community.document_loaders import WebBaseLoader, TextLoader, Docx2txtLoader, PyPDFLoader, MHTMLLoader, ConfluenceLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from loguru import logger

def load_documents_multi(dir):
    logger.debug(f'lload_documents_multi............: dir={dir}')
    documents = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".pdf"):
                logger.debug(f'root={root} file={file}')
                loader = PyPDFLoader(os.path.join(root, file))
                documents.extend(loader.load())
            elif file.endswith('.docx') or file.endswith('.doc'):
                # https://python.langchain.com/docs/integrations/document_loaders/microsoft_word
                logger.debug(f'root={root} file={file}')
                loader = Docx2txtLoader(os.path.join(root, file))
                documents.extend(loader.load())
            elif file.endswith('.txt'):
                logger.debug(f'root={root} file={file}')
                loader = TextLoader(os.path.join(root, file), encoding = 'UTF-8')
                documents.extend(loader.load())

def load_documents_mhtml(dir):
    logger.debug(f'load_documents_mhtml............: dir={dir}')
    documents = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".mhtml"):
                logger.debug(f'root={root} file={file}')
                # MHTMLLoader https://python.langchain.com/docs/integrations/document_loaders/mhtml
                loader = MHTMLLoader(os.path.join(root, file))
                documents.extend(loader.load())
    logger.debug(type(documents))
    logger.debug(len(documents))
    logger.debug(documents[1].metadata)
    # logger.debug(documents[1].page_content)
    return documents

def load_documents_confluence(url, username, password, space_key):
    logger.debug(f'load_documents_confluence............')
    loader = ConfluenceLoader(url=url, username=username, api_key=password)
    documents = loader.load(space_key=space_key, include_attachments=False, limit=10)
    return documents

def split_documents(documents):
    logger.debug('split_documents............')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    source_chunks = text_splitter.split_documents(documents)
    logger.debug(type(source_chunks))
    logger.debug(len(source_chunks))
    logger.debug(source_chunks[10].metadata)
    # logger.debug(source_chunks[10].page_content)
    return source_chunks

def get_embeddings(type='cpu'):
    logger.debug('get_embeddings............')
    model_id = 'intfloat/multilingual-e5-large'
    if type=='cpu':
        model_kwargs = {'device': 'cpu'}
    else:
        model_kwargs = {'device': 'cuda'}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs=model_kwargs
    )
    return embeddings
def create_db(source_chunks, embeddings, db_file_name):
    logger.debug('create_db............')
    db = FAISS.from_documents(source_chunks, embeddings)
    db.save_local(db_file_name)
    return db
def get_new_db(dir, db_file_name):
    logger.debug('get_new_db............')
    # Create Index Db
    documents = load_documents(dir)
    source_chunks = split_documents(documents)
    embeddings = get_embeddings()
    db = create_db(source_chunks, embeddings, db_file_name)
    return db
def load_db(db_file_name, embeddings):
    logger.debug('load_db............')
    new_db = FAISS.load_local(db_file_name, embeddings)
    return new_db
def get_message_content(topic, db, k):
    logger.debug('search............')
    logger.debug(f'topic={topic}')
    docs = db.similarity_search(topic, k=k)
    message_content = re.sub(r'\n{2}', ' ', '\n '.join(
        [f'\n#### {i + 1} Relevant chunk ####\n' + str(doc.metadata) + '\n' + doc.page_content + '\n' for i, doc in
         enumerate(docs)]))
    logger.debug(f'message_content={message_content}')
    return message_content