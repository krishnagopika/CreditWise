import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Security Training - Level Select")

# Colors
DARK_NAVY = (10, 31, 58)
ELECTRIC_CYAN = (0, 212, 255)
SOFT_PURPLE = (108, 99, 255)
MINT_GREEN = (0, 255, 157)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 40, 80)
PURPLE = (40, 20, 80)

# Fonts
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 36, bold=True)
level_font = pygame.font.SysFont('Arial', 18)

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.color = random.choice([ELECTRIC_CYAN, SOFT_PURPLE, MINT_GREEN])
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.glow = 0
        
    def draw(self, surface):
        # Animated glow effect
        self.glow = (self.glow + 0.1) % (2 * math.pi)
        glow_intensity = int(50 + 30 * math.sin(self.glow))
        
        color = self.hover_color if self.is_hovered else self.color
        glow_color = (
            min(255, color[0] + glow_intensity),
            min(255, color[1] + glow_intensity),
            min(255, color[2] + glow_intensity)
        )
        
        # Main button with glow
        pygame.draw.rect(surface, glow_color, self.rect, border_radius=15)
        pygame.draw.rect(surface, color, self.rect.inflate(-8, -8), border_radius=12)
        
        # Text
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def draw_hexagon_grid():
    size = 40
    for x in range(0, WIDTH + size, size):
        for y in range(0, HEIGHT + size, int(size * math.sqrt(3))):
            points = []
            for i in range(6):
                angle = math.pi / 3 * i
                px = x + size * 0.8 * math.cos(angle)
                py = y + size * 0.8 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, (*ELECTRIC_CYAN, 20), points, 1)

def draw_background(particles):
    # Dark gradient background
    for y in range(HEIGHT):
        alpha = y / HEIGHT
        color = (
            int(DARK_NAVY[0] * (1 - alpha) + PURPLE[0] * alpha),
            int(DARK_NAVY[1] * (1 - alpha) + PURPLE[1] * alpha),
            int(DARK_NAVY[2] * (1 - alpha) + PURPLE[2] * alpha)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Hexagon grid
    draw_hexagon_grid()
    
    # Animated particles
    for particle in particles:
        particle.update()
        particle.draw()

def show_level_select():
    particles = [Particle() for _ in range(50)]
    
    # Level data
    levels = [
        {"number": 1, "name": "Credit Card Protection", "description": "Mastercard Identity Check & OTP Security"},
        {"number": 2, "name": "Identity Theft", "description": "Email Security & Phishing Detection"},
        {"number": 3, "name": "Social Media Safety", "description": "Stay safe on social media"}
    ]
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Exit game
            
            # Start button
            start_button = Button(WIDTH//2 - 100, 520, 200, 50, "START LEVEL 1", ELECTRIC_CYAN, SOFT_PURPLE)
            start_button.check_hover(mouse_pos)
            
            if start_button.is_clicked(mouse_pos, event):
                return 1  # Start with level 1
        
        # Draw everything
        draw_background(particles)
        
        # Title
        title = title_font.render("SECURITY TRAINING PROGRAM", True, ELECTRIC_CYAN)
        subtitle = font.render("Complete all 3 levels to become a Security Expert", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 80))
        
        # Draw level cards
        for i, level in enumerate(levels):
            y_pos = 130 + i * 65
            
            # Level card background
            card_rect = pygame.Rect(80, y_pos, WIDTH - 160, 55)
            
            
            card_color = (*ELECTRIC_CYAN, 40)
            border_color = ELECTRIC_CYAN
            
            
            pygame.draw.rect(screen, card_color, card_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)
            
            # Level number and name
            level_text = font.render(f"Level {level['number']}: {level['name']}", True, WHITE)
            desc_text = level_font.render(level['description'], True, WHITE)
            
            screen.blit(level_text, (100, y_pos + 8))
            screen.blit(desc_text, (100, y_pos + 32))
        
        # Start button (only for level 1 for now)
        start_button = Button(WIDTH//2 - 100, 520, 200, 50, "START LEVEL 1", ELECTRIC_CYAN, SOFT_PURPLE)
        start_button.check_hover(mouse_pos)
        start_button.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    return None

if __name__ == "__main__":
    selected_level = show_level_select()
    print(f"Starting level: {selected_level}")