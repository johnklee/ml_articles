"""RL learner to solve Bandit problem."""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class KArmsBandit:
  '''
  K-arms bandit machine.

  Args:
    k: number of arms (int)
    mu: set the average rewards for each of the k-arms.
        Set to "random" for the rewards to be selected from
        a normal distribution with mean = 0.
        Set to "sequence" for the means to be ordered from
        0 to k-1.
        Pass a list or array of length = k for user-defined
        values.
  '''

  def __init__(self, k, mu='random'):
    self.k = k
    if type(mu) == list or type(mu).__module__ == np.__name__:
      # User-defined averages
      self.mu = np.array(mu)
    elif mu == 'random':
      # Draw means from probability distribution
      self.mu = np.random.normal(0, 1, k)
    elif mu == 'sequence':
      # Increase the mean for each arm by one
      self.mu = np.linspace(0, k-1, k)

  def pull(self, nth: int) -> float:
    """Pulls `nth` Bandit to get reward.

    Args:
      nth: The n-th bandit to pull. (0 < nth < k)

    Returns:
      Reward.
    """
    return np.random.normal(self.mu[nth], 1)


class EPSBandit:
  '''
  Epsilon-greedy k-bandit problem

  Attributes:
    k: number of arms (int)
    eps: probability of random action 0 < eps < 1 (float)
    iters: number of steps (int)
    karms_bandit_machine: K-arms bandit macihne.
  '''

  def __init__(self, eps: int, iters: int,
               karms_bandit_machine: KArmsBandit):
    # Bandit machine
    self.karms_bandit_machine = karms_bandit_machine
    self.k = self.karms_bandit_machine.k

    # Search probability
    self.eps = eps

    # Number of iterations
    self.iters = iters

    # Step count
    self.n = 0

    # Step count for each arm
    self.k_n = np.zeros(self.k)

    # Total mean reward
    self.mean_reward = 0

    # Reward obtained from each iteration.
    self.reward = np.zeros(iters)

    # Mean reward for each arm
    self.k_reward = np.zeros(self.k)


  def pull(self):
    # Generate random number
    p = np.random.rand()
    if self.eps == 0 and self.n == 0:
      a = np.random.choice(self.k)
    elif p < self.eps:
      # Randomly select an action
      a = np.random.choice(self.k)
    else:
      # Take greedy action
      a = np.argmax(self.k_reward)

    reward = self.karms_bandit_machine.pull(a)

    # Update counts
    self.n += 1
    self.k_n[a] += 1

    # Update total
    self.mean_reward = self.mean_reward + (
        reward - self.mean_reward) / self.n

    # Update results for a_k
    self.k_reward[a] = self.k_reward[a] + (
        reward - self.k_reward[a]) / self.k_n[a]

  def run(self):
    for i in range(self.iters):
      self.pull()
      self.reward[i] = self.mean_reward

  def reset(self):
    # Resets results while keeping settings
    self.n = 0
    self.k_n = np.zeros(self.k)
    self.mean_reward = 0
    self.reward = np.zeros(self.iters)
    self.k_reward = np.zeros(self.k)


class EPSDecayBandit:
  '''
  epsilon-decay k-bandit problem

  Attributes:
    k: number of arms (int)
    iters: number of steps (int)
    karms_bandit_machine: K-arms bandit macihne.
  '''

  def __init__(self, iters, karms_bandit_machine: KArmsBandit):
    # Bandit machine
    self.karms_bandit_machine = karms_bandit_machine
    self.k = self.karms_bandit_machine.k

    # Number of iterations
    self.iters = iters
    # Step count
    self.n = 0
    # Step count for each arm
    self.k_n = np.zeros(self.k)
    # Total mean reward
    self.mean_reward = 0
    self.reward = np.zeros(iters)
    # Mean reward for each arm
    self.k_reward = np.zeros(self.k)

  def pull(self):
    # Generate random number
    p = np.random.rand()
    if p < 1 / (1 + self.n / self.k):
      # Randomly select an action
      a = np.random.choice(self.k)
    else:
      # Take greedy action
      a = np.argmax(self.k_reward)

    reward = self.karms_bandit_machine.pull(a)

    # Update counts
    self.n += 1
    self.k_n[a] += 1

    # Update total
    self.mean_reward = self.mean_reward + (
        reward - self.mean_reward) / self.n

    # Update results for a_k
    self.k_reward[a] = self.k_reward[a] + (
        reward - self.k_reward[a]) / self.k_n[a]

  def run(self):
    for i in range(self.iters):
      self.pull()
      self.reward[i] = self.mean_reward

  def reset(self):
    # Resets results while keeping settings
    self.n = 0
    self.k_n = np.zeros(self.k)
    self.mean_reward = 0
    self.reward = np.zeros(self.iters)
    self.k_reward = np.zeros(self.k)
