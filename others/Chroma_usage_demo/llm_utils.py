"""Module to obtain LLM agent for quick evaluation of LLM."""
import dataclasses
import os
import json
import openai
from typing import Any


os.environ["TOKENIZERS_PARALLELISM"] = "false"
config_data = None
with open("config.json", mode="r") as json_file:
    config_data = json.load(json_file)


@dataclasses.dataclass
class FullResp:
  context: str
  question: str
  response: Any


class LLMAgent:
  """LLM agent for simple chat interaction."""

  DEFAULT_RAG_CONTEXT_FORMAT = """
You are a software engineer with less experience in using bttc.
Use the following collected information to answer questions: {}
"""
  DEFAULT_RAG_QUESTION_FORMAT = '{}'

  def __init__(
      self, config_data: dict[str, str] | None = None,
      context: str = 'You are a software engineer.',
      rag_context_format: str | None = None,
      rag_question_format: str | None = None,
      model_name: str = 'gpt-3.5-turbo'):
    if config_data is None:
      with open('config.json', mode='r') as json_file:
        config_data = json.load(json_file)

    self._config_data = config_data
    self._client = openai.OpenAI(
        # This is the default and can be omitted
        api_key=config_data.get('openai-secret-key'))
    self.context = context
    self.model_name = 'gpt-3.5-turbo'
    self.rag_context_format = (
        rag_context_format or self.DEFAULT_RAG_CONTEXT_FORMAT)
    self.rag_question_format = (
        rag_question_format or self.DEFAULT_RAG_QUESTION_FORMAT)

  @property
  def client(self):
    return self._client

  def answer(
      self,
      question: str,
      model_name: str | None = None,
      context: str | None = None,
      temperature: int = 0) -> str:
    """Answers the input question by LLM."""
    model = model_name or self.model_name
    context = context or self.context
    chat_completion = self.client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": question},
        ],
        temperature=temperature,
        n=1)

    return chat_completion.choices[0].message.content

  def answer_with_rag(
      self,
      collection: Any,
      question: str,
      model_name: str | None = None,
      context: str | None = None,
      temperature: int = 0,
      rag_max_doc_count: int = 10,
      return_full: bool = False) -> str:
    """Answer the given question with help of LLM + RAG."""
    related_docs = collection.query(
        query_texts=[question],
        n_results=rag_max_doc_count,
        include=["documents"])

    docs_str = ",".join(related_docs["documents"][0])
    context = self.rag_context_format.format(docs_str)
    question = self.rag_question_format.format(question)
    resp = self.answer(
        question=question,
        context=context,
        model_name=model_name,
        temperature=temperature)

    if return_full:
      return FullResp(
          context=context,
          question=question,
          response=resp)

    return resp
