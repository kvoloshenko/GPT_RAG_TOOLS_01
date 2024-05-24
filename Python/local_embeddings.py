from langchain_community.embeddings import HuggingFaceEmbeddings

type='cpu'
model_id = 'intfloat/multilingual-e5-large'
if type=='cpu':
    model_kwargs = {'device': 'cpu'}
else:
    model_kwargs = {'device': 'cuda'}
embeddings = HuggingFaceEmbeddings(
    model_name=model_id,
    model_kwargs=model_kwargs
)

model.save_pretrained("Model/multilingual-e5-large", from_pt=True)