import numpy as np 
from tensorflow.keras.backend import get_value
from model import NN
import time

class Agent:
    def __init__(self, env):
        self.env = env
        self.num_observations = tuple(self.env.observation_space_n)
        self.num_actions = self.env.action_space_n
        self.num_values = 1
        self.gamma = 0.99
        self.epsilon = 0.999
        self.epsilon_limit = 0.001
        self.lr_actor = 1e-3
        self.lr_critic = 5e-3
        self.model = NN(self.num_observations, self.num_actions, self.num_values, self.lr_actor, self.lr_critic)

    def get_action(self, state, game):
        if np.random.rand(1) > self.epsilon:
            policy = self.model.actor(inputs=state, training=False)
            action = np.random.choice(self.num_actions, p=get_value(policy[0]))
        else:
            action = np.random.choice(self.num_actions)
            if self.epsilon > self.epsilon_limit:
                self.epsilon *= 0.9          
        return action

    def get_values(self, state, game, action, reward, next_state, done):
        values = np.zeros((1, self.num_values))
        advantages = np.zeros((1, self.num_actions))

        value = self.model.predict_critic(state, game)
        next_value = self.model.predict_critic(next_state, game)

        if done:
            advantages[0][action] = reward - value
            values[0][0] = reward
        else:
            advantages[0][action] = (reward + self.gamma * next_value) - value
            values[0][0] = reward + self.gamma * next_value

        return advantages, values

    def update_policy(self, states, games, advantages, values):
        self.model.train_actor(states, games, advantages)
        self.model.train_critic(states, games, -values)
