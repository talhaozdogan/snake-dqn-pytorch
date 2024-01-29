import torch, random, numpy as np
from game import Game
from collections import deque
from model import NeuralNetwork, Trainer

class Agent():
    def __init__(self, input_size, num_of_actions = 3, epsilon_start = 0.90, epsilon_end = 0.01, epsilon_decay = 0.0001, gamma = 0.8, learning_rate = 0.001, MAX_MEMORY = 100000, BATCH_SIZE = 1000):
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.num_of_actions = num_of_actions
        self.BATCH_SIZE = BATCH_SIZE
        
        self.network = NeuralNetwork(input_size, num_of_actions)
        self.trainer = Trainer(self.network, learning_rate, gamma)

        self.memory = deque(maxlen = MAX_MEMORY)

    def act(self, state):
        if np.random.rand() < self.epsilon:
            print("random action")
            action = np.random.randint(self.num_of_actions)
        else:
            print("calculated action")
            state = torch.tensor(state, dtype=torch.float)
            q_values = self.network(state)
            action = torch.argmax(q_values).item()

        self._update_epsilon()

        return action
        
    def _update_epsilon(self): 
        if self.epsilon > self.epsilon_end:
            self.epsilon -= self.epsilon_decay

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long(self):
        if len(self.memory) > self.BATCH_SIZE:
            sample = random.sample(self.memory, self.BATCH_SIZE)
        else:
            sample = self.memory
        
        states, actions, rewards, next_states, game_overs = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)


if __name__ == "__main__":
    game = Game()
    agent = Agent(input_size = 6)

    while True:
        old_state = game.get_state()

        action = agent.act(old_state)
        reward, game_over, score = game.update(action)

        new_state = game.get_state()

        agent.train_short(old_state, action, reward, new_state, game_over)

        agent.remember(old_state, action, reward, new_state, game_over)

        if game_over:
            agent.train_long()
