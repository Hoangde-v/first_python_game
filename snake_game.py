import pygame
import random
import sys
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)

# Game settings
SNAKE_SPEED = 10

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x) % GRID_WIDTH
        new_y = (head_y + dir_y) % GRID_HEIGHT
        
        # Check if snake hits itself
        if (new_x, new_y) in self.positions[1:]:
            return False  # Game over
        
        self.positions.insert(0, (new_x, new_y))
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True  # Continue game
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
    
    def render(self, surface):
        for i, (x, y) in enumerate(self.positions):
            color = GREEN if i == 0 else DARK_GREEN  # Head is lighter green
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)  # Border

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
    
    def render(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                          self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Bite Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Load sounds (if available)
        try:
            self.eat_sound = mixer.Sound("eat.wav")
        except:
            self.eat_sound = None
            
        try:
            self.game_over_sound = mixer.Sound("game_over.wav")
        except:
            self.game_over_sound = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif not self.game_over and not self.paused:
                    self.handle_movement(event.key)
        return True
    
    def handle_movement(self, key):
        if key == pygame.K_UP and self.snake.direction != (0, 1):
            self.snake.direction = (0, -1)
        elif key == pygame.K_DOWN and self.snake.direction != (0, -1):
            self.snake.direction = (0, 1)
        elif key == pygame.K_LEFT and self.snake.direction != (1, 0):
            self.snake.direction = (-1, 0)
        elif key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
            self.snake.direction = (1, 0)
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Update snake
        if not self.snake.update():
            self.game_over = True
            if self.game_over_sound:
                self.game_over_sound.play()
            return
        
        # Check if snake eats food
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow = True
            self.score += 10
            if self.eat_sound:
                self.eat_sound.play()
            
            # Generate new food position (avoid snake body)
            while True:
                self.food.randomize_position()
                if self.food.position not in self.snake.positions:
                    break
    
    def render(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # Draw snake and food
        self.snake.render(self.screen)
        self.food.render(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause_screen()
        
        pygame.display.flip()
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.big_font.render("GAME OVER!", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # Instructions
        restart_text = self.font.render("Press SPACE to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        quit_text = self.font.render("Press ESC to quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_pause_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.big_font.render("PAUSED", True, BLUE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        # Instructions
        resume_text = self.font.render("Press P to resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def reset_game(self):
        self.snake.reset()
        self.food.randomize_position()
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(SNAKE_SPEED)
        
        pygame.quit()
        sys.exit()

def main():
    print("Snake Bite Game")
    print("Controls:")
    print("- Arrow keys to move")
    print("- P to pause/resume")
    print("- SPACE to restart (when game over)")
    print("- ESC to quit")
    print("\nStarting game...")
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
