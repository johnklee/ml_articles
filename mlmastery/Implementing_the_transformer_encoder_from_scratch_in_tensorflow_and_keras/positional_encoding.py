import tensorflow as tf
from tensorflow import convert_to_tensor, string
from tensorflow.keras.layers import TextVectorization, Embedding, Layer
from tensorflow.data import Dataset
import numpy as np
import matplotlib.pyplot as plt


class PositionEmbeddingLayer(Layer):
  def __init__(self, sequence_length, vocab_size, output_dim, **kwargs):
    super(PositionEmbeddingLayer, self).__init__(**kwargs)
    self.word_embedding_layer = Embedding(
        input_dim=vocab_size, output_dim=output_dim)
    self.position_embedding_layer = Embedding(
        input_dim=sequence_length, output_dim=output_dim)

  def call(self, inputs):
    position_indices = tf.range(tf.shape(inputs)[-1])
    embedded_words = self.word_embedding_layer(inputs)
    embedded_indices = self.position_embedding_layer(position_indices)
    return embedded_words + embedded_indices


class PositionEmbeddingFixedWeights(Layer):
  def __init__(self, sequence_length, vocab_size, output_dim, **kwargs):
    super(PositionEmbeddingFixedWeights, self).__init__(**kwargs)
    word_embedding_matrix = self._get_position_encoding(vocab_size, output_dim)   
    position_embedding_matrix = self._get_position_encoding(sequence_length, output_dim)                                          
    self.word_embedding_layer = Embedding(
        input_dim=vocab_size, output_dim=output_dim,
        weights=[word_embedding_matrix],
        trainable=False)
    self.position_embedding_layer = Embedding(
        input_dim=sequence_length, output_dim=output_dim,
        weights=[position_embedding_matrix],
        trainable=False)
             
  def _get_position_encoding(self, seq_len, d, n=10000):
    P = np.zeros((seq_len, d))
    for k in range(seq_len):
      for i in np.arange(int(d/2)):
        denominator = np.power(n, 2*i/d)
        P[k, 2*i] = np.sin(k/denominator)
        P[k, 2*i+1] = np.cos(k/denominator)
    return P

  def call(self, inputs):        
    position_indices = tf.range(tf.shape(inputs)[-1])
    embedded_words = self.word_embedding_layer(inputs)
    embedded_indices = self.position_embedding_layer(position_indices)
    return embedded_words + embedded_indices
