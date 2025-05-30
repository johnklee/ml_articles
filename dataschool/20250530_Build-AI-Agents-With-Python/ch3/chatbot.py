import getpass
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

_ = load_dotenv()

DEFAULT_GEMINI_MODEL_NAME = 'gemini-2.0-flash'


def get_model(model_name: str = DEFAULT_GEMINI_MODEL_NAME):
  return ChatGoogleGenerativeAI(
    model=model_name,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
  )


def get_chat_template(system_message: str):
  return ChatPromptTemplate([
      ('system', system_message),
      ("placeholder", "{messages}"),
  ])


def get_chain(
    system_message: str,
    model_name: str = DEFAULT_GEMINI_MODEL_NAME):
  return get_chat_template(system_message) | get_model(model_name)


def get(
    system_message: str,
    model_name: str = DEFAULT_GEMINI_MODEL_NAME,
    by_message: str = 'See you later!'):
  chain = get_chain(system_message, model_name)
  def call_model(state: MessagesState, chain=chain):
    updated_messages = chain.invoke(state)
    return {"messages": updated_messages}

  workflow = StateGraph(MessagesState)
  workflow.add_node("model_node", call_model)
  workflow.add_edge(START, "model_node")

  memory = MemorySaver()
  app = workflow.compile(memory)

  def chatbot(chat_id: int=0, app=app):
    config = {"configurable": {"thread_id": chat_id}}

    while True:
      user_input = input("User:")

      if user_input in ["exit", "quit"]:
        print(f"AI: {by_message}!")
        break

      else:
        print("AI: ", end="")
        for chunk, metadata in app.stream({"messages": user_input}, config, stream_mode="messages"):
          print(chunk.content, end="", flush=True)

        print("\n")

  return chatbot
