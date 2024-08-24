"""Module to configure genai."""

import google.generativeai as genai
import os
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv(os.path.expanduser('~/.env'))) # read local .env file
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


def get_model(model_name: str = 'gemini-1.5-flash'):
  """Obtains model by the given name.
  Args:
    model_name: Model name.

  Returns:
    The Genai model object.
  """
  if not model_name.startswith('models/'):
    model_name = f'models/{model_name}'

  return genai.GenerativeModel(model_name)
