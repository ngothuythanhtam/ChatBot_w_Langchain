from prompt_templates import memory_prompt_template
from langchain.chains import StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms import ctransformers
from langchain.llms import CTransformers
from ctransformers import AutoModelForCausalLM
from langchain.vectorstores import chroma
import chromadb
import yaml

with open ("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_llm(model_path=config["model_path"]["large"], model_type=config["model_type"], model_config=None):
    if model_config is None:
        model_config = config["model_config"]
    llm = CTransformers(
        model=model_path,  # Change this line
        model_type=model_type,
        max_new_tokens=model_config['max_new_tokens'],
        temperature=model_config['temperature'],
        context_length=model_config['context_length'],
        gpu_layers=model_config['gpu_layers']
    )
    return llm

def create_embeddings(embeddings_path = config["embeddings_path"]):
    return HuggingFaceInstructEmbeddings(embeddings_path)

def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm = llm, prompt = chat_prompt, memory = memory)

def load_normal_chain(chat_history):
    return chatChain(chat_history)

class chatChain:

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        llm = create_llm()
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)

    def run(self, user_input):
        return self.llm_chain.run(human_input = user_input, history = self.memory.chat_memory.messages, stop = "Human:")