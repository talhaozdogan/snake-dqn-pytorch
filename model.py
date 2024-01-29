import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class NeuralNetwork(nn.Module):
    def __init__(self, input_size, output_size, hidden_size=64):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 16),
            nn.ReLU(),
            nn.Linear(16, output_size)
        )

    def forward(self, x):
        return self.model(x)


class Trainer:
    def __init__(self, model, learning_rate, gamma):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr = learning_rate)
        self.criterion = nn.MSELoss()
        self.gamma = gamma

    def train_step(self, state, action, reward, next_state, game_over):
        states = torch.tensor(state, dtype=torch.float)
        actions = torch.tensor(action, dtype=torch.float)
        rewards = torch.tensor(reward, dtype=torch.float)
        next_states = torch.tensor(next_state, dtype=torch.float)

        if len(states.shape) == 1:
            states = torch.unsqueeze(states, 0)
            actions = torch.unsqueeze(actions, 0)
            rewards = torch.unsqueeze(rewards, 0)
            next_states = torch.unsqueeze(next_states, 0)
            game_overs = (game_over, )
        
        outputs = self.model(states)
        targets = outputs.clone()

        for idx in range(len(game_overs)):
            Q_new = rewards[idx]
            if not game_overs[idx]:
                Q_new = rewards[idx] + self.gamma * torch.max(self.model(next_states[idx]))

            targets[idx][torch.argmax(actions[idx]).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(targets, outputs)
        loss.backward()
        self.optimizer.step()