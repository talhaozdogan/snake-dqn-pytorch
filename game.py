from collections import deque
import random, pygame, math, numpy as np

class Apple():
    def __init__(self, board):
        self.board = board
        self.recreate()

    def recreate(self):
        while True:
            self.position = [random.randint(0, Game.SCREEN_SIZE[0] - 1), random.randint(0, Game.SCREEN_SIZE[1] - 1)]
            if self.board[self.position[0]][self.position[1]] == "b":
                self.board[self.position[0]][self.position[1]] = "a"
                break

class Snake():
    def __init__(self, board):
        self.board = board
        self.length = 1
        self.direction = (-1, 0)

        starting_point = (Game.SCREEN_SIZE[0]//2, Game.SCREEN_SIZE[1]//2)

        self.board[starting_point[0]][starting_point[1]] = "s"
        self.board[starting_point[0] + 1][starting_point[1]] = "s"
        self.board[starting_point[0] + 2][starting_point[1]] = "s"

        self.head = starting_point
        self.coordinates = deque()

        self.coordinates.append( (starting_point[0] + 2 , starting_point[1]) )
        self.coordinates.append( (starting_point[0] + 1 , starting_point[1]) )
        self.coordinates.append(starting_point)

    def update_position(self, action):
        if action == "straight" or action == 0: 
            self.direction = self.direction
        elif action == "right" or action == 1: 
            self.direction = (self.direction[1], -self.direction[0])
        elif action == "left" or action == 2: 
            self.direction = (-self.direction[1], self.direction[0])

        self.head = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])
        self.coordinates.append(self.head)
        
        if not self._is_valid(self.head):
            return "die_w"
        
        if self.board[self.head[0]][self.head[1]] == "b":
            self.board[self.head[0]][self.head[1]] = "s"
            temp = self.coordinates.popleft()
            self.board[temp[0]][temp[1]] = "b"
            return "step"
        
        if self.board[self.head[0]][self.head[1]] == "a":
            self.board[self.head[0]][self.head[1]] = "s"
            self.length += 1
            return "grow"
        
        if self.board[self.head[0]][self.head[1]] == "s":
            return "die_s"
        

    def _is_valid(self, position):
        if position[0] < 0 or position[0] >= Game.SCREEN_SIZE[0] or position[1] < 0 or position[1] >= Game.SCREEN_SIZE[1]:
            return False
        return True


class Game():
    #constants
    CELL_SIZE = 20
    SCREEN_SIZE = (30,30)
    FPS = 100

    def __init__(self):
        self.board = [["b" for j in range(Game.SCREEN_SIZE[1])] for i in range(Game.SCREEN_SIZE[0])]
        self.snake = Snake(self.board)
        self.apple = Apple(self.board)
        self.old_distance = math.sqrt((self.snake.head[0] - self.apple.position[0])**2 + (self.snake.head[1] - self.apple.position[1])**2)

        self.score = 0
        self.num_of_moves = 0

        pygame.init()
        pygame.display.set_caption("Snake AI")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((Game.CELL_SIZE*Game.SCREEN_SIZE[0], Game.CELL_SIZE*Game.SCREEN_SIZE[1]))
        self.draw()

    def draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]: Game.FPS /= 5
            if keys[pygame.K_UP]: Game.FPS *= 5

        self.screen.fill("black")
        for row in range(Game.SCREEN_SIZE[0]):
            for column in range(Game.SCREEN_SIZE[1]):
                if self.board[row][column] == "a": pygame.draw.rect(self.screen, "red", pygame.Rect(Game.CELL_SIZE*column, Game.CELL_SIZE*row, Game.CELL_SIZE, Game.CELL_SIZE))
                if self.board[row][column] == "s": pygame.draw.rect(self.screen, "yellow", pygame.Rect(Game.CELL_SIZE*column, Game.CELL_SIZE*row, Game.CELL_SIZE, Game.CELL_SIZE))
        pygame.display.flip()
        self.clock.tick(Game.FPS)

    def get_state(self):
        state = [
            #danger straight, right and left
            self._is_danger( (self.snake.head[0] + self.snake.direction[0], self.snake.head[1] + self.snake.direction[1]) ),
            self._is_danger( (self.snake.head[0] + self.snake.direction[1], self.snake.head[1] + -self.snake.direction[0]) ),
            self._is_danger( (self.snake.head[0] + -self.snake.direction[1], self.snake.head[1] + self.snake.direction[0]) ),

            #apple position
            #right
            (self.snake.direction == (1,0) and self.apple.position[1] < self.snake.head[1]) or
            (self.snake.direction == (-1,0) and self.apple.position[1] > self.snake.head[1]) or
            (self.snake.direction == (0,1) and self.apple.position[0] > self.snake.head[0]) or
            (self.snake.direction == (0,-1) and self.apple.position[0] < self.snake.head[0]),

            #left
            (self.snake.direction == (1,0) and self.apple.position[1] > self.snake.head[1]) or
            (self.snake.direction == (-1,0) and self.apple.position[1] < self.snake.head[1]) or
            (self.snake.direction == (0,1) and self.apple.position[0] < self.snake.head[0]) or
            (self.snake.direction == (0,-1) and self.apple.position[0] > self.snake.head[0]),

            #front
            (self.snake.direction == (1,0) and self.apple.position[0] > self.snake.head[0]) or
            (self.snake.direction == (-1,0) and self.apple.position[0] < self.snake.head[0]) or
            (self.snake.direction == (0,1) and self.apple.position[1] > self.snake.head[1]) or
            (self.snake.direction == (0,-1) and self.apple.position[1] < self.snake.head[1]),
        
        ]
        return np.array(state, dtype=int)

    def update(self, action):
        self.num_of_moves += 1
        reward = 0

        result = self.snake.update_position(action)

        if result.startswith("die"):
            reward = -100
            self.reset()

        elif result == "grow":
            self.apple.recreate()
            reward = 100
        
        elif result == "step":
            new_distance = math.sqrt((self.snake.head[0] - self.apple.position[0])**2 + (self.snake.head[1] - self.apple.position[1])**2)
            distance_difference = self.old_distance - new_distance
            self.old_distance = new_distance
            
            reward = distance_difference / math.sqrt(Game.SCREEN_SIZE[0]**2 + Game.SCREEN_SIZE[1]**2)
            reward *= 500

        self.draw()

        print(reward)
        return reward, result == "die", self.snake.length - 1
    
    def reset(self):
        self.board = [["b" for j in range(Game.SCREEN_SIZE[1])] for i in range(Game.SCREEN_SIZE[0])]
        self.snake = Snake(self.board)
        self.apple = Apple(self.board)
        self.score = 0
        self.num_of_moves = 0
        math.sqrt((self.snake.head[0] - self.apple.position[0])**2 + (self.snake.head[1] - self.apple.position[1])**2)
    
    def _is_danger(self, coordinate):
        if coordinate[0] < 0 or coordinate[0] >= Game.SCREEN_SIZE[0] or coordinate[1] < 0 or coordinate[1] >= Game.SCREEN_SIZE[1]:
            return True
        if self.board[coordinate[0]][coordinate[1]] == "s":
            return True
        return False


if __name__ == "__main__":
    game = Game()

    while True:    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: game.update("left")
            elif keys[pygame.K_RIGHT]: game.update("right")
            elif keys[pygame.K_UP]: game.update("straight")

            state = game.get_state()
            print("danger straight {}\ndanger right {}\ndanger left {}\napple right {}\napple left {}\napple front {}\n\n\n\n\n".format(state[0],state[1],state[2],state[3],state[4],state[5]))