import os
from langchain_ollama import ChatOllama
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# model = ChatOllama(model="qwen3:4b", temperature=0, validate_model_on_init=True)
model = init_chat_model(model="openai:gpt-4.1-mini-2025-04-14", temperature=0)


