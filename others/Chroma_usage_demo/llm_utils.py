"""Module to obtain LLM agent for quick evaluation of LLM."""
import os
import json
import openai


os.environ["TOKENIZERS_PARALLELISM"] = "false"
config_data = None
with open("config.json", mode="r") as json_file:
    config_data = json.load(json_file)


class LLMAgent:
  """LLM agent for simple chat interaction."""

  def __init__(
      self, config_data: dict[str, str] | None = None,
      context: str = 'You are a software engineer.',
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

  @property
  def client(self):
    return self._client

  def answer(
      self,
      question: str,
      model_name: str | None = None,
      context: str | None = None,
      temperature: int = 0) -> str:
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

