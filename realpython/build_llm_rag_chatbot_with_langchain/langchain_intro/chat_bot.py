"""Chat bot module."""
import dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
from langchain_intro.tools import get_current_wait_time


dotenv.load_dotenv()

REVIEWS_CHROMA_PATH = "chroma_data/"

review_template_str = """Your job is to use patient
reviews to answer questions about their experience at
a hospital. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=review_template_str,
    )
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template="{question}",
    )
)
messages = [review_system_prompt, review_human_prompt]

review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)

output_parser = StrOutputParser()

reviews_vector_db = Chroma(
    persist_directory=REVIEWS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings()
)

reviews_retriever  = reviews_vector_db.as_retriever(k=10)
chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
agent_chat_model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

review_chain = review_prompt_template | chat_model
review_chain_with_stdout = review_chain | StrOutputParser()
review_chain_with_rag = (
    {"context": reviews_retriever, "question": RunnablePassthrough()}  # New here
    | review_prompt_template
    | chat_model
    | StrOutputParser()
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain_with_rag.invoke,
        description="""Useful when you need to answer questions
        about patient reviews or experiences at the hospital.
        Not useful for answering questions about specific visit
        details such as payer, billing, treatment, diagnosis,
        chief complaint, hospital, or physician information.
        Pass the entire question as input to the tool. For instance,
        if the question is "What do patients think about the triage system?",
        the input should be "What do patients think about the triage system?"
        """,
    ),
    Tool(
        name="Waits",
        func=get_current_wait_time,
        description="""Use when asked about current wait times
        at a specific hospital. This tool can only get the current
        wait time at a hospital and does not have any information about
        aggregate or historical wait times. This tool returns wait times in
        minutes. Do not pass the word "hospital" as input,
        only the hospital name itself. For instance, if the question is
        "What is the wait time at hospital A?", the input should be "A".
        """,
    ),
]

hospital_agent_prompt = hub.pull("hwchase17/openai-functions-agent")

hospital_agent = create_openai_functions_agent(
    llm=agent_chat_model,
    prompt=hospital_agent_prompt,
    tools=tools,
)

hospital_agent_executor = AgentExecutor(
    agent=hospital_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)
