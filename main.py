# import streamlit as st
# from llm_chains import load_normal_chain, load_pdf_chat_chain
# from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# from utils import save_chat_history_json, get_timestamp, load_chat_history_json
# from html_templates import get_bot_template, get_user_template, css
# import yaml
# import os

# with open("config.yaml", "r") as f:
#     config = yaml.safe_load(f)

# def load_chain(chat_history):
#     if st.session_state.pdf_chat:
#         print("loading pdf chat chain")
#         return load_pdf_chat_chain(chat_history)
#     return load_normal_chain(chat_history)

# def clear_input_field():
#     if st.session_state.user_question == "":
#         st.session_state.user_question = st.session_state.user_input
#         st.session_state.user_input = ""

# def set_send_input():
#     st.session_state.send_input = True
#     clear_input_field()

# def track_index():
#     st.session_state.session_index_tracker = st.session_state.session_key

# def save_chat_history():
#     if st.session_state.history:
#         if st.session_state.session_key == "new_session":
#             st.session_state.new_session_key = get_timestamp() + ".json"
#             save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"], st.session_state.new_session_key))
#         else:
#             save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"], st.session_state.session_key))

# def toggle_pdf_chat():
#     st.session_state.pdf_chat = True

# def main():
#     # app config
#     st.set_page_config(page_title="Multi-modal Local Chat App", page_icon="🤖")
#     st.title("Multi-modal Local Chat App")
#     st.write(css, unsafe_allow_html=True)

#     # Initialize session state variables if they don't exist
#     if "session_key" not in st.session_state:
#         st.session_state.session_key = "new_session"
#     if "send_input" not in st.session_state:
#         st.session_state.send_input = False
#     if "user_question" not in st.session_state:
#         st.session_state.user_question = ""
#     if "new_session_key" not in st.session_state:
#         st.session_state.new_session_key = None
#     if "session_index_tracker" not in st.session_state:
#         st.session_state.session_index_tracker = "new_session"
#     if "history" not in st.session_state:
#         st.session_state.history = []
#     if "pdf_chat" not in st.session_state:
#         st.session_state.pdf_chat = False

#     # Sidebar setup
#     st.sidebar.title("Chat Sessions")
#     chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

#     if st.session_state.session_key == "new_session" and st.session_state.new_session_key:
#         st.session_state.session_index_tracker = st.session_state.new_session_key
#         st.session_state.new_session_key = None

#     index = chat_sessions.index(st.session_state.session_index_tracker)
#     st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index, on_change=track_index)
#     st.sidebar.checkbox("PDF Chat", key="pdf_chat", value=False)

#     if st.session_state.session_key != "new_session":
#         st.session_state.history = load_chat_history_json(os.path.join(config["chat_history_path"], st.session_state.session_key))
#     else:
#         st.session_state.history = []

#     chat_history = StreamlitChatMessageHistory(key="history")
#     llm_chain = load_chain(chat_history)

#     # Audio handler
#     chat_container = st.container()
#     user_input = st.text_input("Type your message here", key="user_input", on_change=set_send_input)

#     send_button = st.button("Send", key="send_button", on_click=clear_input_field)


#     uploaded_pdf = st.sidebar.file_uploader("Upload a PDF file", accept_multiple_files=True, key="pdf_upload", type=["pdf"], on_change=toggle_pdf_chat)

#     if send_button or st.session_state.send_input:
#         if st.session_state.user_question:
#             llm_response = llm_chain.run(st.session_state.user_question)
#             st.session_state.user_question = ""
#             st.session_state.send_input = False

#     if chat_history.messages:
#         with chat_container:
#             st.write("Chat History:")
#             for message in chat_history.messages:
#                 if message.type == "human":
#                     st.write(get_user_template(message.content), unsafe_allow_html=True)
#                 else:
#                     st.write(get_bot_template(message.content), unsafe_allow_html=True)

#     # Save chat history if needed
#     save_chat_history()

# if __name__ == "__main__":
#     main()


import os
import yaml
import streamlit as st
from dotenv import load_dotenv
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from html_templates import get_bot_template, get_user_template, css

# Load configuration and environment
load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Define helper functions
def load_document(file_path):
    loader = UnstructuredPDFLoader(file_path)
    return loader.load()

def setup_vectorstore(documents):
    embeddings = HuggingFaceEmbeddings()
    text_splitter = CharacterTextSplitter(separator="/n", chunk_size=1000, chunk_overlap=200)
    doc_chunks = text_splitter.split_documents(documents)
    return FAISS.from_documents(doc_chunks, embeddings)

def create_chain(vectorstore):
    llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory(
        llm=llm,
        output_key="answer",
        memory_key="chat_history",
        return_messages=True
    )
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, chain_type="map_reduce", memory=memory, verbose=True)

# Streamlit app configuration
st.set_page_config(page_title="Multi-modal Local Chat App", page_icon="🤖")
st.title("Multi-modal Local Chat App")
st.write(css, unsafe_allow_html=True)

# Session state initialization
if "session_key" not in st.session_state:
    st.session_state.session_key = "new_session"
if "send_input" not in st.session_state:
    st.session_state.send_input = False
if "user_question" not in st.session_state:
    st.session_state.user_question = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "pdf_chat" not in st.session_state:
    st.session_state.pdf_chat = False

# Sidebar for chat sessions
st.sidebar.title("Chat Sessions")
chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])
index = chat_sessions.index(st.session_state.session_key)
st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key")

# PDF Upload handler
uploaded_pdf = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"], on_change=lambda: st.session_state.update({"pdf_chat": True}))

# Handle PDF upload for conversational chat
if uploaded_pdf:
    file_path = os.path.join(os.getcwd(), uploaded_pdf.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_pdf.getbuffer())
    
    documents = load_document(file_path)
    vectorstore = setup_vectorstore(documents)
    st.session_state.conversation_chain = create_chain(vectorstore)

# Chat container and input handling
chat_container = st.container()
user_input = st.text_input("Type your message here", key="user_input")

if user_input and st.session_state.pdf_chat:
    response = st.session_state.conversation_chain({"question": user_input})
    assistant_response = response["answer"]
    
    # Display messages
    st.write(get_user_template(user_input), unsafe_allow_html=True)
    st.write(get_bot_template(assistant_response), unsafe_allow_html=True)
    
    # Append to chat history
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": assistant_response})

# Save chat history if needed
if st.session_state.history:
    save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"], st.session_state.session_key))

