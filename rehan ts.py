"""
Flappy Bird NEA - Pygame Version
Candidate number: 4113
Centre number: 12262

RUN THIS FILE TO START THE GAME
"""

# First, check if pygame is installed and install if needed
import subprocess
import sys
import importlib.util

def check_and_install_pygame():
    """Check if pygame is installed, if not, install it"""
    if importlib.util.find_spec("pygame") is None:
        print("Pygame not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("Pygame installed successfully!")
        except:
            print("Failed to install pygame. Please install manually:")
            print("pip install pygame")
            return False
    return True

# Install pygame if needed
if not check_and_install_pygame():
    input("Press Enter to exit...")
    sys.exit(1)

# Now import pygame
import pygame
import random
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_WIDTH = 80
INITIAL_PIPE_GAP = 200
PIPE_SPEED = 4
GROUND_HEIGHT = 100
MAX_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
LIGHT_BLUE = (135, 206, 235)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

class GameState(Enum):
    """Game states enum"""
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SCOREBOARD = 5
    CONTROLS = 6

class Bird:
    """Bird class with animation"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.width = 40
        self.height = 30
        self.animation_timer = 0
        self.wing_up = False
        self.dead = False
        
    def flap(self):
        """Make the bird jump"""
        if not self.dead:
            self.velocity = FLAP_STRENGTH
            return True
        return False
        
    def update(self):
        """Update bird physics"""
        if not self.dead:
            self.velocity += GRAVITY
            self.y += self.velocity
            
            # Animation
            self.animation_timer += 1
            if self.animation_timer > 10:
                self.animation_timer = 0
                self.wing_up = not self.wing_up
                
    def draw(self, screen):
        """Draw the bird"""
        # Bird body
        if self.dead:
            color = GRAY
        else:
            color = YELLOW
            
        pygame.draw.ellipse(screen, color, (self.x, self.y, self.width, self.height))
        
        # Eye
        pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 10), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 27, self.y + 8), 2)
        
        # Beak
        if not self.dead:
            pygame.draw.polygon(screen, ORANGE, [
                (self.x + 38, self.y + 12),
                (self.x + 45, self.y + 15),
                (self.x + 38, self.y + 18)
            ])
            
        # Wing animation
        if self.wing_up and not self.dead:
            pygame.draw.ellipse(screen, BROWN, (self.x + 10, self.y - 5, 15, 10))
        elif not self.dead:
            pygame.draw.ellipse(screen, BROWN, (self.x + 10, self.y + 15, 15, 10))
            
        # Dead eyes X
        if self.dead:
            pygame.draw.line(screen, RED, (self.x + 20, self.y + 8), (self.x + 30, self.y + 15), 3)
            pygame.draw.line(screen, RED, (self.x + 30, self.y + 8), (self.x + 20, self.y + 15), 3)
            
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Pipe:
    """Pipe obstacle class"""
    def __init__(self, x, gap_size):
        self.x = x
        self.gap_position = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150)
        self.gap_size = gap_size
        self.passed = False
        self.width = PIPE_WIDTH
        
    def update(self, speed):
        """Move pipe left"""
        self.x -= speed
        
    def draw(self, screen):
        """Draw the pipe"""
        # Top pipe
        pygame.draw.rect(screen, DARK_GREEN, 
                        (self.x, 0, self.width, self.gap_position - self.gap_size//2))
        pygame.draw.rect(screen, GREEN, 
                        (self.x - 5, self.gap_position - self.gap_size//2 - 20, self.width + 10, 20))
        
        # Bottom pipe
        pygame.draw.rect(screen, DARK_GREEN, 
                        (self.x, self.gap_position + self.gap_size//2, 
                         self.width, SCREEN_HEIGHT - GROUND_HEIGHT - (self.gap_position + self.gap_size//2)))
        pygame.draw.rect(screen, GREEN, 
                        (self.x - 5, self.gap_position + self.gap_size//2, self.width + 10, 20))
        
    def get_rects(self):
        """Get collision rectangles"""
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_position - self.gap_size//2)
        bottom_rect = pygame.Rect(self.x, self.gap_position + self.gap_size//2, 
                                 self.width, SCREEN_HEIGHT - GROUND_HEIGHT - (self.gap_position + self.gap_size//2))
        return top_rect, bottom_rect
    
    def is_off_screen(self):
        """Check if pipe is off screen"""
        return self.x + self.width < 0

class PowerUp:
    """Power-up class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(["enlarge", "double"])
        self.width = 30
        self.height = 30
        self.collected = False
        self.active = False
        self.duration = 300
        self.timer = 0
        
    def update(self):
        """Update power-up"""
        if not self.collected:
            self.x -= PIPE_SPEED
            
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False
                self.timer = 0
                
    def collect(self):
        """Collect the power-up"""
        self.collected = True
        self.active = True
        
    def draw(self, screen):
        """Draw the power-up"""
        if not self.collected:
            if self.type == "enlarge":
                color = BLUE
                text = "E"
            else:
                color = YELLOW
                text = "2x"
                
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            
            font = pygame.font.Font(None, 24)
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (self.x + 8, self.y + 5))
            
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Scoreboard:
    """High score manager"""
    def __init__(self):
        self.scores = []
        self.filename = "high_scores.json"
        self.load_scores()
        
    def load_scores(self):
        """Load scores from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
        except:
            self.scores = []
            
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores[:10], f)
        except:
            pass
            
    def add_score(self, name, score):
        """Add new score"""
        if len(name) < 2 or len(name) > 12:
            return False
            
        self.scores.append({"name": name, "score": score})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.save_scores()
        return True
        
    def get_top_scores(self):
        """Get top scores"""
        return self.scores[:10]
        
    def is_high_score(self, score):
        """Check if score qualifies for leaderboard"""
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]["score"]

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
        self.reset_game()
        self.scoreboard = Scoreboard()
        
    def reset_game(self):
        """Reset game state"""
        self.bird = Bird(100, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.powerups = []
        self.score = 0
        self.high_score = 0
        self.state = GameState.MENU
        self.pipe_timer = 0
        self.powerup_timer = 0
        self.pipe_gap = INITIAL_PIPE_GAP
        self.current_speed = PIPE_SPEED
        self.powerup_available = False
        self.current_powerup = None
        self.double_points = False
        self.player_name = ""
        self.name_input_active = False
        
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.MENU:
                        return False
                    else:
                        self.state = GameState.MENU
                        
                elif event.key == pygame.K_p and self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                    
                elif event.key == pygame.K_q and self.powerup_available and self.state == GameState.PLAYING:
                    self.activate_powerup()
                    
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:
                        self.start_game()
                    elif self.state == GameState.GAME_OVER and self.name_input_active:
                        if self.scoreboard.add_score(self.player_name, self.score):
                            self.name_input_active = False
                            self.state = GameState.SCOREBOARD
                            
                elif event.key == pygame.K_BACKSPACE and self.name_input_active:
                    self.player_name = self.player_name[:-1]
                    
                elif self.name_input_active:
                    if len(self.player_name) < 12 and event.unicode.isalnum():
                        self.player_name += event.unicode
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.PLAYING:
                    self.bird.flap()
                    
                elif self.state == GameState.MENU:
                    mouse_pos = pygame.mouse.get_pos()
                    if 150 <= mouse_pos[0] <= 350 and 300 <= mouse_pos[1] <= 350:
                        self.start_game()
                    elif 150 <= mouse_pos[0] <= 350 and 400 <= mouse_pos[1] <= 450:
                        self.state = GameState.SCOREBOARD
                    elif 150 <= mouse_pos[0] <= 350 and 500 <= mouse_pos[1] <= 550:
                        self.state = GameState.CONTROLS
                        
                elif self.state == GameState.GAME_OVER and not self.name_input_active:
                    mouse_pos = pygame.mouse.get_pos()
                    if 150 <= mouse_pos[0] <= 350 and 400 <= mouse_pos[1] <= 450:
                        self.start_game()
                    elif 150 <= mouse_pos[0] <= 350 and 500 <= mouse_pos[1] <= 550:
                        self.state = GameState.MENU
                        
                elif self.state in [GameState.SCOREBOARD, GameState.CONTROLS, GameState.PAUSED]:
                    mouse_pos = pygame.mouse.get_pos()
                    if 150 <= mouse_pos[0] <= 350 and 600 <= mouse_pos[1] <= 650:
                        self.state = GameState.MENU
                        
        return True
        
    def start_game(self):
        """Start a new game"""
        self.reset_game()
        self.state = GameState.PLAYING
        
    def activate_powerup(self):
        """Activate collected power-up"""
        if self.current_powerup and self.powerup_available:
            self.current_powerup.active = True
            self.powerup_available = False
            if self.current_powerup.type == "double":
                self.double_points = True
                
    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
            
        # Update bird
        self.bird.update()
        
        # Update timers
        self.pipe_timer += 1
        self.powerup_timer += 1
        
        # Spawn pipes
        if self.pipe_timer > 90:
            self.pipes.append(Pipe(SCREEN_WIDTH, self.pipe_gap))
            self.pipe_timer = 0
            
        # Spawn power-ups
        if self.powerup_timer > 300 and len(self.powerups) < 2:
            power_y = random.randint(100, SCREEN_HEIGHT - GROUND_HEIGHT - 100)
            self.powerups.append(PowerUp(SCREEN_WIDTH, power_y))
            self.powerup_timer = 0
            
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update(self.current_speed)
            
            # Check collision
            bird_rect = self.bird.get_rect()
            top_rect, bottom_rect = pipe.get_rects()
            
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                self.bird.dead = True
                self.state = GameState.GAME_OVER
                if self.scoreboard.is_high_score(self.score):
                    self.name_input_active = True
                    
            # Score point
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                if self.double_points:
                    self.score += 2
                else:
                    self.score += 1
                    
                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    
            # Remove off-screen pipes
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
                
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            
            # Check collection
            if not powerup.collected and self.bird.get_rect().colliderect(powerup.get_rect()):
                powerup.collect()
                self.powerup_available = True
                self.current_powerup = powerup
                self.powerups.remove(powerup)
                
            # Remove off-screen power-ups
            if powerup.x + powerup.width < 0:
                self.powerups.remove(powerup)
                
        # Check boundaries
        if self.bird.y < 0:
            self.bird.y = 0
            self.bird.velocity = 0
        elif self.bird.y + self.bird.height > SCREEN_HEIGHT - GROUND_HEIGHT:
            self.bird.dead = True
            self.state = GameState.GAME_OVER
            if self.scoreboard.is_high_score(self.score):
                self.name_input_active = True
                
        # Update active power-up
        if self.current_powerup and self.current_powerup.active:
            if self.current_powerup.type == "enlarge":
                self.pipe_gap = 300
            self.current_powerup.timer += 1
            if self.current_powerup.timer >= self.current_powerup.duration:
                self.current_powerup = None
                self.pipe_gap = INITIAL_PIPE_GAP
                self.double_points = False
                
        # Difficulty increase
        if self.score > 0 and self.score % 10 == 0:
            self.current_speed = min(PIPE_SPEED + (self.score // 20), MAX_SPEED)
            
    def draw(self):
        """Draw everything"""
        # Background
        if self.score >= 40:
            bg_color = PURPLE
        elif self.score >= 30:
            bg_color = GOLD
        elif self.score >= 20:
            bg_color = SILVER
        elif self.score >= 10:
            bg_color = BRONZE
        else:
            bg_color = LIGHT_BLUE
            
        self.screen.fill(bg_color)
        
        # Draw ground
        pygame.draw.rect(self.screen, BROWN, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.SCOREBOARD:
            self.draw_scoreboard()
        elif self.state == GameState.CONTROLS:
            self.draw_controls()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Draw menu screen"""
        # Title
        title = self.font_large.render("FLAPPY BIRD", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Start button
        color = GREEN if 150 <= mouse_pos[0] <= 350 and 300 <= mouse_pos[1] <= 350 else DARK_GREEN
        pygame.draw.rect(self.screen, color, (150, 300, 200, 50))
        text = self.font_medium.render("START GAME", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 310))
        
        # Scoreboard button
        color = BLUE if 150 <= mouse_pos[0] <= 350 and 400 <= mouse_pos[1] <= 450 else (0, 0, 200)
        pygame.draw.rect(self.screen, color, (150, 400, 200, 50))
        text = self.font_medium.render("HIGH SCORES", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 410))
        
        # Controls button
        color = ORANGE if 150 <= mouse_pos[0] <= 350 and 500 <= mouse_pos[1] <= 550 else (200, 100, 0)
        pygame.draw.rect(self.screen, color, (150, 500, 200, 50))
        text = self.font_medium.render("CONTROLS", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 510))
        
    def draw_game(self):
        """Draw game screen"""
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score
        score_text = self.font_large.render(str(self.score), True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - 20, 50))
        
        # Draw high score
        high_text = self.font_small.render(f"Best: {self.high_score}", True, WHITE)
        self.screen.blit(high_text, (SCREEN_WIDTH - 100, 20))
        
        # Draw pause indicator
        pause_text = self.font_small.render("P: Pause", True, WHITE)
        self.screen.blit(pause_text, (10, 20))
        
        # Draw power-up indicator
        if self.powerup_available:
            power_text = self.font_small.render("Q: Activate Power-up!", True, YELLOW)
            self.screen.blit(power_text, (SCREEN_WIDTH//2 - 100, 100))
            
        # Draw medal
        if self.score >= 40:
            medal = "PLATINUM"
            color = PURPLE
        elif self.score >= 30:
            medal = "GOLD"
            color = GOLD
        elif self.score >= 20:
            medal = "SILVER"
            color = SILVER
        elif self.score >= 10:
            medal = "BRONZE"
            color = BRONZE
        else:
            medal = None
            
        if medal:
            medal_text = self.font_small.render(medal, True, color)
            self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 30, 80))
            
    def draw_paused(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font_large.render("PAUSED", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300))
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        color = RED if 150 <= mouse_pos[0] <= 350 and 600 <= mouse_pos[1] <= 650 else (200, 0, 0)
        pygame.draw.rect(self.screen, color, (150, 600, 200, 50))
        text = self.font_medium.render("BACK TO MENU", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 610))
        
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 150))
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - 60, 250))
        
        # Medal
        if self.score >= 40:
            medal_text = self.font_medium.render("Platinum Medal!", True, PURPLE)
            self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 80, 300))
        elif self.score >= 30:
            medal_text = self.font_medium.render("Gold Medal!", True, GOLD)
            self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 70, 300))
        elif self.score >= 20:
            medal_text = self.font_medium.render("Silver Medal!", True, SILVER)
            self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 70, 300))
        elif self.score >= 10:
            medal_text = self.font_medium.render("Bronze Medal!", True, BRONZE)
            self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 70, 300))
            
        if self.name_input_active:
            prompt = self.font_small.render("New High Score! Enter name:", True, YELLOW)
            self.screen.blit(prompt, (SCREEN_WIDTH//2 - 120, 350))
            name_text = self.font_medium.render(self.player_name + "_", True, WHITE)
            self.screen.blit(name_text, (SCREEN_WIDTH//2 - 50, 380))
        else:
            # Buttons
            mouse_pos = pygame.mouse.get_pos()
            
            # Play again
            color = GREEN if 150 <= mouse_pos[0] <= 350 and 400 <= mouse_pos[1] <= 450 else DARK_GREEN
            pygame.draw.rect(self.screen, color, (150, 400, 200, 50))
            text = self.font_medium.render("PLAY AGAIN", True, BLACK)
            self.screen.blit(text, (250 - text.get_width()//2, 410))
            
            # Menu
            color = BLUE if 150 <= mouse_pos[0] <= 350 and 500 <= mouse_pos[1] <= 550 else (0, 0, 200)
            pygame.draw.rect(self.screen, color, (150, 500, 200, 50))
            text = self.font_medium.render("MAIN MENU", True, BLACK)
            self.screen.blit(text, (250 - text.get_width()//2, 510))
            
    def draw_scoreboard(self):
        """Draw scoreboard screen"""
        title = self.font_large.render("HIGH SCORES", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        scores = self.scoreboard.get_top_scores()
        y = 150
        for i, score_data in enumerate(scores, 1):
            if i == 1:
                color = GOLD
                prefix = "🥇 "
            elif i == 2:
                color = SILVER
                prefix = "🥈 "
            elif i == 3:
                color = BRONZE
                prefix = "🥉 "
            else:
                color = WHITE
                prefix = f"{i}. "
                
            score_text = self.font_medium.render(
                f"{prefix}{score_data['name']} - {score_data['score']}", 
                True, color
            )
            self.screen.blit(score_text, (100, y))
            y += 40
            
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        color = RED if 150 <= mouse_pos[0] <= 350 and 600 <= mouse_pos[1] <= 650 else (200, 0, 0)
        pygame.draw.rect(self.screen, color, (150, 600, 200, 50))
        text = self.font_medium.render("BACK", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 610))
        
    def draw_controls(self):
        """Draw controls screen"""
        title = self.font_large.render("CONTROLS", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        controls = [
            "🖱️  Mouse Click - Fly upward",
            "⚡  Q - Activate power-up",
            "⏸️  P - Pause game",
            "⎋  ESC - Back to menu",
            "",
            "POWER-UPS:",
            "🔵 Blue (E) - Enlarge pipe gaps",
            "🟡 Yellow (2x) - Double points"
        ]
        
        y = 150
        for control in controls:
            if control == "":
                y += 20
                continue
            text = self.font_small.render(control, True, WHITE)
            self.screen.blit(text, (50, y))
            y += 40
            
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        color = RED if 150 <= mouse_pos[0] <= 350 and 600 <= mouse_pos[1] <= 650 else (200, 0, 0)
        pygame.draw.rect(self.screen, color, (150, 600, 200, 50))
        text = self.font_medium.render("BACK", True, BLACK)
        self.screen.blit(text, (250 - text.get_width()//2, 610))
        
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

if __name__ == "__main__":
    game = Game()
    game.run()
