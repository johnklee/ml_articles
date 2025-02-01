# Project language tutor (focused on listening & speaking)
Cockatoo AI is a cutting-edge language tutor project focused on enhancing listening and speaking skills.  Our AI companion engages users in realistic conversations, adapting its speaking style (from direct to philosophical) and difficulty level (A1-C1) to suit individual learning needs. Cockatoo AI can discuss user-provided topics, ask relevant questions, and even express itself with a variety of tones and voices (happy, sad, elderly, adult, male, female, etc.) to provide comprehensive listening practice.  For our team, this project provides valuable experience in LLM development, voice model integration, deep learning, and CI/CD, while also offering opportunities to explore bias mitigation techniques and optimize the balance between fine-tuning and computational resources.  Our architecture utilizes a three-stage pipeline: voice-to-text (Model A), text-to-text processing with LLMs (Model B, potentially managed by LangChain), and text-to-voice (Model C, possibly the same as A). We prioritize open-source models and aim to create a personalized and effective language learning experience.

# Goal towards users:
- Speak as native as possible to users so users can practice listening as well as speaking.
- Can adjust the language tutor’s teaching attitude (e.g., Direct vs Plato)
- Can adjust the language tutor’s speaking/work usage difficulties (e.g., A1, A2, B1, B2, C1 levels) to make learning easier for users.
- Can discuss the topic the user uploaded/raised and can correspondingly ask appropriate questions to the user. 
- Can practice listening to various tones from AI (e.g., expressing the sentence with happiness, sadness, …, from elderly/adult/woman/man …)

# Goal towards team members:
- Improve LLM, voice models, DL, and other framework knowledge/skills. 
- Can use the language tutor to benefit him/herself.
- Learn CI/CD and do research on improving potential product biasedness and relevant skills. 
- Learn the balance between fine-tuning and our computing powers.

# How To (Initiative):
Use models (A-B-C as shown below) to form the pipeline as the final language tutor:
- model A: voice to text
- model B(LLM): text à text , might be managed by [langChain](https://python.langchain.com/docs/get_started/introduction), Andrew Ng provided [2-3 free short courses](https://www.deeplearning.ai/short-courses/).
- model C: text to voice
PS: C might be the same as A, needs more research. But the** Goal towards users** should be the top concern when considering which model to use. Besides, better to use open-source models instead of paying premium APIs.

For model C, one may use LangChain to manage LLM. langChain is a tool that helps build automation pipelines, store vector databases (our own data), and automate the monitoring of LLM with various technical strategies as well as prompt engineering. For example, we may manage the prompt strategy by telling LLM to self-supervise the output text quality, ie, tell LLM to redo it again if the previous output was not good.


# Market Competitors (for language tutoring)
- Langotalk (multi-lan)
- Tutor Lily: AI Language Tutor (multi-lan)

# Good References
## For Model A (Speech to text, STT)
- The library [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/)
  is used for performing speech recognition, with support for several engines and APIs, online and offline.
    - [Notebook - Easy Speech-to-Text with Python](https://github.com/johnklee/ml_articles/blob/master/medium/Easy-speech-to-text-with-python/notebook.ipynb)
- [`Whisper`](https://github.com/openai/whisper) is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a multitasking model that can perform multilingual speech recognition, speech translation, and language identification.
    - [Notebook - Introduction for Whisper in OpenAI](https://github.com/johnklee/ml_articles/blob/master/others/ithome_ithelp_openapi_whisper/notebook.ipynb)
## For Model C (Text to speech, TTS)
- The company [Evelenlabs](https://elevenlabs.io/) has advanced **non-open sourced** TTS model for multi-languages. It performs well in Chinese (no Taiwanese tone) and English from my perspective, which inlcudes happy/sad/... tones as well as male/female/... sounds.


# Misc
