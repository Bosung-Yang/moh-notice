from langchain.pipelines import TextPipeline
import transformers
import torch
from transfomers import AutoTokenizer
from torch import cuda, bfloat16

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.vectorstores import Chroma
from langchain.storage import LocalFileStore
from langchain.chains import RetrievalQA

def load_model():
    model_name = 'microsoft/phi-4'
    device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
    
    bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=bfloat16
    )

    model_config = transformers.AutoConfig.from_pretrained(model_name, trust_remote_code = True)
    model = transformers.AutoModelForCausalLM.from_pretrained(model_name, config=model_config, trust_remote_code = True, bnb_config=bnb_config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code = True)

    model = model.to(device)
    tokenizer = tokenizer.to(device)

    return model, tokenizer

def rag_qa(model, prompt):
    rag_file = 'notice.txt'
    data_loader = UnstructuredFileLoader(rag_file)
    cache_dir = LocalFileStore('./cache/')

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n", 
        chunk_size=500,
        chunk_overlap=50
    )

    docs = data_loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    vectorstore = Chroma.from_documents(docs, cached_embeddings)
    retriever = vectorstore.as_retriever()

    chain = RetrievalQA.from_chain_type(
    llm=model,
    chain_type="map_reduce",
    retriever=retriever,
    )

    return chain.run(prompt)