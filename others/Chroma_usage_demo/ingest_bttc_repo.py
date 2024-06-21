#!/bin/env python
import os
import pathlib
import chromadb
from chromadb.utils import embedding_functions


ENV_REPO_PATH = 'BTTC_REPO_ROOT'


def ingestion_of_repo_dataset_gen_with_split(
    default_repo_path: str = None, max_line_num: int = 100,
    context_line_num: int = 5,
    extra_doc_file_paths: list[str] | None = None):
  """Generates dataset of repo for ingestion with split actions."""
  ids = []
  documents = []
  metadatas = []

  id_current_num = 1
  repo_path = os.environ.get(ENV_REPO_PATH, default_repo_path)
  if repo_path is None:
    raise Exception(
        f'Environment variable="{ENV_REPO_PATH}" does not exist!')

  if repo_path is None:
    raise Exception(
        f'Environment variable="{ENV_REPO_PATH}" does not exist!')

  if extra_doc_file_paths:
    for file_path in extra_doc_file_paths:
      file_extension = file_path.split('.')[-1]
      lines = open(file_path).read().split('\n')
      current_doc_lines = []
      for start_line_num in range(0, len(lines), 50):
        if not current_doc_lines:
          current_doc_lines = lines[start_line_num:start_line_num+max_line_num]
        else:
          current_doc_lines = (
              current_doc_lines[-context_line_num:] +
              lines[start_line_num:start_line_num+max_line_num])

        id_current_num += 1
        ids.append(str(id_current_num))
        documents.append('\n'.join(current_doc_lines))
        metadatas.append({
            'file_path': file_path,
            'file_type': file_extension,
        })
        if len(ids) == 10:
          yield {
              "ids": ids,
              "documents": documents,
              "metadatas": metadatas}

          ids = []
          documents = []
          metadatas = []

  for root, dirs, files in os.walk(repo_path):
    for file in files:
      file_extension = file.split('.')[-1]
      if any([
          file_extension not in {'py', 'md', 'txt'},
          file.startswith('.')]):
        continue

      file_path = os.path.join(root, file)
      lines = open(file_path).read().split('\n')
      current_doc_lines = []
      for start_line_num in range(0, len(lines), 50):
        if not current_doc_lines:
          current_doc_lines = lines[start_line_num:start_line_num+max_line_num]
        else:
          current_doc_lines = (
              current_doc_lines[-context_line_num:] +
              lines[start_line_num:start_line_num+max_line_num])

        id_current_num += 1
        ids.append(str(id_current_num))
        documents.append('\n'.join(current_doc_lines))
        metadatas.append({
            'file_path': file_path,
            'file_type': file_extension,
        })
        if len(ids) == 10:
          yield {
              "ids": ids,
              "documents": documents,
              "metadatas": metadatas}

          ids = []
          documents = []
          metadatas = []

      if ids:
        yield {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas}


def ingestion_of_repo_dataset_gen(default_repo_path: str = None):
  """Generates dataset of repo for ingestion."""
  ids = []
  documents = []
  metadatas = []

  id_current_num = 1
  repo_path = os.environ.get(ENV_REPO_PATH, default_repo_path)
  if repo_path is None:
    raise Exception(
        f'Environment variable="{ENV_REPO_PATH}" does not exist!')

  for root, dirs, files in os.walk(repo_path):
    for file in files:
      file_extension = file.split('.')[-1]
      if any([
          file_extension not in {'py', 'md', 'txt'},
          file.startswith('.')]):
        continue

      file_path = os.path.join(root, file)
      ids.append(str(id_current_num))
      id_current_num += 1
      documents.append(open(file_path).read())
      metadatas.append({
          'file_path': file_path,
          'file_type': file_extension,
      })
      if len(ids) == 10:
        yield {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas}

        ids = []
        documents = []
        metadatas = []

  if ids:
    yield {
        "ids": ids,
        "documents": documents,
        "metadatas": metadatas}


def build_chroma_collection(
    chroma_path: pathlib.Path,
    collection_name: str,
    embedding_func_name: str,
    distance_func_name: str = "cosine",
    default_repo_path: str = None,
    extra_doc_file_paths: list[str] | None = None):
  """Create a ChromaDB collection"""
  chroma_client = chromadb.PersistentClient(chroma_path)
  for collection in chroma_client.list_collections():
    if collection.name == collection_name:
      print(f'Collect with name="{collection_name}" has been created!')
      return collection

  embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
      model_name=embedding_func_name)

  collection = chroma_client.create_collection(
      name=collection_name,
      embedding_function=embedding_func,
      metadata={"hnsw:space": distance_func_name})

  ingest_doc_count = 0
  for dataset in ingestion_of_repo_dataset_gen_with_split(
      default_repo_path, extra_doc_file_paths=extra_doc_file_paths):
    collection.add(
        ids=dataset['ids'],
        documents=dataset['documents'],
        metadatas=dataset['metadatas'])

  return collection
