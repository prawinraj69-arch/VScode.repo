import sys
import random
from enum import Enum

try:
    import pygame
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False
else:
    PYGAME_AVAILABLE = True

if PYGAME_AVAILABLE:
    # Initialize Pygame
    pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 200, 0)

# Direction Enum
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Use Arrow Keys to Move")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.score = 0
        
        self.reset_game()
    
    def reset_game(self):
        """Initialize or reset game state"""
        # Snake starts in the middle
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self.spawn_food()
        self.game_over = False
        self.score = 0
    
    def spawn_food(self):
        """Spawn food at a random location not occupied by snake"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def handle_events(self):
        """Handle user input and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Handle direction changes
                if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.next_direction = Direction.RIGHT
                
                # Restart on Game Over
                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
        
        return True
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check collision with walls
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over = True
            return
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check collision with food
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(BLACK)
        
        # Draw grid (optional, for visual reference)
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, (30, 30, 30), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, (30, 30, 30), (0, y), (WINDOW_WIDTH, y))
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * GRID_SIZE + 2, y * GRID_SIZE + 2, 
                              GRID_SIZE - 4, GRID_SIZE - 4)
            # Head is brighter green
            color = YELLOW if i == 0 else GREEN
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Draw food
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE + 2, 
                               self.food[1] * GRID_SIZE + 2, 
                               GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.rect(self.screen, RED, food_rect)
        pygame.draw.ellipse(self.screen, RED, food_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER!", True, RED)
            restart_text = self.font.render("Press SPACE to restart", True, YELLOW)
            
            # Center text on screen
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if not PYGAME_AVAILABLE:
    # Provide a simple Tkinter-based fallback so the game can run without pygame.
    try:
        import tkinter as tk
    except Exception:
        sys.stderr.write("Neither pygame nor tkinter is available; cannot run the game.\n")
        sys.exit(1)

    class SnakeGameTK:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Snake Game - Tkinter Fallback")
            self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
            self.canvas.pack()
            self.score = 0
            self.game_over = False

            start_x = GRID_WIDTH // 2
            start_y = GRID_HEIGHT // 2
            self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
            self.direction = Direction.RIGHT
            self.next_direction = Direction.RIGHT
            self.food = self.spawn_food()

            self.root.bind('<KeyPress>', self.on_key)
            self.root.after(1000 // FPS, self.tick)

        def spawn_food(self):
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if (x, y) not in self.snake:
                    return (x, y)

        def on_key(self, event):
            key = event.keysym
            if key == 'Up' and self.direction != Direction.DOWN:
                self.next_direction = Direction.UP
            elif key == 'Down' and self.direction != Direction.UP:
                self.next_direction = Direction.DOWN
            elif key == 'Left' and self.direction != Direction.RIGHT:
                self.next_direction = Direction.LEFT
            elif key == 'Right' and self.direction != Direction.LEFT:
                self.next_direction = Direction.RIGHT
            elif key == 'space' and self.game_over:
                self.reset_game()

        def reset_game(self):
            start_x = GRID_WIDTH // 2
            start_y = GRID_HEIGHT // 2
            self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
            self.direction = Direction.RIGHT
            self.next_direction = Direction.RIGHT
            self.food = self.spawn_food()
            self.score = 0
            self.game_over = False

        def update(self):
            if self.game_over:
                return
            self.direction = self.next_direction
            head_x, head_y = self.snake[0]
            dx, dy = self.direction.value
            new_head = (head_x + dx, head_y + dy)
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                self.game_over = True
                return
            if new_head in self.snake:
                self.game_over = True
                return
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.score += 10
                self.food = self.spawn_food()
            else:
                self.snake.pop()

        def draw(self):
            self.canvas.delete('all')
            # draw grid lightly
            for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                self.canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill='#1e1e1e')
            for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
                self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill='#1e1e1e')

            for i, (x, y) in enumerate(self.snake):
                x1 = x * GRID_SIZE + 2
                y1 = y * GRID_SIZE + 2
                x2 = x1 + GRID_SIZE - 4
                y2 = y1 + GRID_SIZE - 4
                color = 'yellow' if i == 0 else 'green'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white')

            fx1 = self.food[0] * GRID_SIZE + 2
            fy1 = self.food[1] * GRID_SIZE + 2
            fx2 = fx1 + GRID_SIZE - 4
            fy2 = fy1 + GRID_SIZE - 4
            self.canvas.create_oval(fx1, fy1, fx2, fy2, fill='red', outline='')

            self.canvas.create_text(60, 20, text=f"Score: {self.score}", fill='white', font=('TkDefaultFont', 14), anchor='w')

            if self.game_over:
                self.canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20, text='GAME OVER!', fill='red', font=('TkDefaultFont', 24))
                self.canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20, text='Press SPACE to restart', fill='yellow', font=('TkDefaultFont', 14))

        def tick(self):
            self.update()
            self.draw()
            self.root.after(1000 // FPS, self.tick)

        def run(self):
            self.root.mainloop()

if __name__ == "__main__":
    if PYGAME_AVAILABLE:
        game = SnakeGame()
    else:
        game = SnakeGameTK()
    game.run()