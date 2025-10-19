import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Security Command Center - Identity Check")

# Colors
DARK_NAVY = (10, 31, 58)
ELECTRIC_CYAN = (0, 212, 255)
SOFT_PURPLE = (108, 99, 255)
MINT_GREEN = (0, 255, 157)
SOFT_RED = (255, 107, 107)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 40, 80)
PURPLE = (40, 20, 80)

# Fonts
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 32, bold=True)
question_font = pygame.font.SysFont('Arial', 20)
score_font = pygame.font.SysFont('Arial', 28, bold=True)

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

class FloatingNumber:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.3, 1.0)
        self.number = str(random.randint(0, 9))
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.02, 0.02)
        
    def update(self):
        self.y += self.speed
        self.angle += self.rotation_speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self):
        alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.001))
        color = (*ELECTRIC_CYAN[:3], alpha)
        
        text_surf = pygame.Surface((20, 30), pygame.SRCALPHA)
        text = font.render(self.number, True, color)
        text_rect = text.get_rect(center=(10, 15))
        text_surf.blit(text, text_rect)
        
        # Rotate the surface
        rotated_surf = pygame.transform.rotate(text_surf, math.degrees(self.angle))
        rotated_rect = rotated_surf.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surf, rotated_rect)

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
            # Create hexagon points
            points = []
            for i in range(6):
                angle = math.pi / 3 * i
                px = x + size * 0.8 * math.cos(angle)
                py = y + size * 0.8 * math.sin(angle)
                points.append((px, py))
            
            # Draw subtle hexagon outlines
            pygame.draw.polygon(screen, (*ELECTRIC_CYAN, 20), points, 1)

def draw_command_center_background(particles, floating_numbers):
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
    
    # Floating OTP numbers
    for number in floating_numbers:
        number.update()
        number.draw()
    
    # Central glow
    center_glow = pygame.Surface((400, 400), pygame.SRCALPHA)
    pygame.draw.circle(center_glow, (*ELECTRIC_CYAN, 30), (200, 200), 200)
    screen.blit(center_glow, (WIDTH//2 - 200, HEIGHT//2 - 200))

def draw_question_panel(question, progress, score):
    # Glass morphism panel
    panel_rect = pygame.Rect(50, 100, WIDTH - 100, 300)
    
    # Background with blur effect (simulated)
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    s.fill((255, 255, 255, 30))  # Semi-transparent white
    pygame.draw.rect(s, (255, 255, 255, 50), s.get_rect(), border_radius=20, width=2)
    screen.blit(s, panel_rect)
    
    # Title
    title = title_font.render("SECURITY VERIFICATION QUIZ", True, ELECTRIC_CYAN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
    
    # Progress
    progress_text = font.render(f"Question {progress[0]}/{progress[1]}", True, WHITE)
    screen.blit(progress_text, (WIDTH//2 - progress_text.get_width()//2, 160))
    
    # Score
    score_text = score_font.render(f"Security Score: {score}", True, MINT_GREEN)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 30, 30))
    
    # Question (wrapped text)
    y_offset = 200
    words = question.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if question_font.size(test_line)[0] < WIDTH - 150:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    for line in lines:
        text = question_font.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 35

def show_feedback(is_correct, explanation):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    color = MINT_GREEN if is_correct else SOFT_RED
    symbol = "✓" if is_correct else "✗"
    
    result_text = title_font.render(f"{symbol} {'CORRECT' if is_correct else 'INCORRECT'}", True, color)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 200))
    
    # Explanation (wrapped)
    y_offset = 250
    words = explanation.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < WIDTH - 100:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    for line in lines:
        text = font.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 30
    
    continue_text = font.render("Click anywhere to continue...", True, WHITE)
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 400))

def show_final_score(score, total_questions):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Score result
    if score == total_questions * 10:
        result = "SECURITY EXPERT 🏆"
        color = MINT_GREEN
    elif score >= total_questions * 7:
        result = "SECURITY PRO 🌟"
        color = ELECTRIC_CYAN
    else:
        result = "TRAINING REQUIRED 📚"
        color = SOFT_PURPLE
    
    result_text = title_font.render(result, True, color)
    score_text = title_font.render(f"Final Score: {score}/{total_questions * 10}", True, WHITE)
    
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 150))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))
    
    # Educational information
    info_title = font.render("Mastercard Identity Check Summary:", True, ELECTRIC_CYAN)
    screen.blit(info_title, (WIDTH//2 - info_title.get_width()//2, 260))
    
    key_points = [
        "✓ Free service that automatically protects your credit card",
        "✓ No registration required - your card is already enrolled", 
        "✓ Only works with retailers displaying the Identity Check logo",
        "✓ OTP sent to your phone during checkout for verification",
        "✓ Adds extra security layer against unauthorized online use"
    ]
    
    for i, point in enumerate(key_points):
        point_text = font.render(point, True, WHITE)
        screen.blit(point_text, (WIDTH//2 - point_text.get_width()//2, 300 + i*35))

def main():
    clock = pygame.time.Clock()
    
    # Game data
    questions = [
        {
            "question": "Mastercard Identity Check is a free service that automatically protects your Capital One credit card from unauthorized online use.",
            "answer": True,
            "explanation": "CORRECT! It's a free service that provides automatic protection against unauthorized online transactions."
        },
        {
            "question": "You need to manually register your card to use Mastercard Identity Check protection.",
            "answer": False, 
            "explanation": "FALSE! Your Capital One card is automatically registered for the service - no manual registration needed."
        },
        {
            "question": "All online retailers offer Mastercard Identity Check protection for your payments.",
            "answer": False,
            "explanation": "FALSE! Only retailers displaying the Mastercard Identity Check logo offer this protection service."
        }
    ]
    
    # Visual elements
    particles = [Particle() for _ in range(50)]
    floating_numbers = [FloatingNumber() for _ in range(20)]
    
    # Game state
    current_question = 0
    score = 0
    show_feedback_screen = False
    current_feedback = None
    game_finished = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if not game_finished and not show_feedback_screen:
                # Create buttons for current question
                true_button = Button(WIDTH//2 - 150, 400, 120, 60, "TRUE", MINT_GREEN, (*MINT_GREEN, 150))
                false_button = Button(WIDTH//2 + 30, 400, 120, 60, "FALSE", SOFT_RED, (*SOFT_RED, 150))
                
                true_button.check_hover(mouse_pos)
                false_button.check_hover(mouse_pos)
                
                if true_button.is_clicked(mouse_pos, event):
                    if questions[current_question]["answer"] == True:
                        score += 10
                        show_feedback_screen = True
                        current_feedback = (True, questions[current_question]["explanation"])
                    else:
                        show_feedback_screen = True
                        current_feedback = (False, questions[current_question]["explanation"])
                
                elif false_button.is_clicked(mouse_pos, event):
                    if questions[current_question]["answer"] == False:
                        score += 10
                        show_feedback_screen = True
                        current_feedback = (True, questions[current_question]["explanation"])
                    else:
                        show_feedback_screen = True
                        current_feedback = (False, questions[current_question]["explanation"])
            
            elif show_feedback_screen and event.type == pygame.MOUSEBUTTONDOWN:
                show_feedback_screen = False
                current_question += 1
                if current_question >= len(questions):
                    game_finished = True
            
            #elif game_finished and event.type == pygame.MOUSEBUTTONDOWN:
                # Restart game
                #current_question = 0
                #score = 0
                #game_finished = False
        
        # Draw everything
        draw_command_center_background(particles, floating_numbers)
        
        if not game_finished and not show_feedback_screen:
            draw_question_panel(
                questions[current_question]["question"], 
                (current_question + 1, len(questions)), 
                score
            )
            
            # Draw buttons
            true_button = Button(WIDTH//2 - 150, 400, 120, 60, "TRUE", MINT_GREEN, (*MINT_GREEN, 150))
            false_button = Button(WIDTH//2 + 30, 400, 120, 60, "FALSE", SOFT_RED, (*SOFT_RED, 150))
            
            true_button.check_hover(mouse_pos)
            false_button.check_hover(mouse_pos)
            
            true_button.draw(screen)
            false_button.draw(screen)
        
        elif show_feedback_screen and current_feedback:
            show_feedback(current_feedback[0], current_feedback[1])
        
        elif game_finished:
            show_final_score(score, len(questions))

            # Play Again button
            play_again_button = Button(WIDTH//2 - 100, 480, 200, 50, "PLAY AGAIN", SOFT_PURPLE, ELECTRIC_CYAN)
            play_again_button.check_hover(mouse_pos)
            play_again_button.draw(screen)

            # NEXT LEVEL button
            next_level_button = Button(WIDTH//2 - 100, 540, 200, 50, "NEXT LEVEL", MINT_GREEN, MINT_GREEN)
            next_level_button.check_hover(mouse_pos)
            next_level_button.draw(screen)

            # Handle button clicks INSIDE the game_finished section
            if play_again_button.is_clicked(mouse_pos, event):
                current_question = 0
                score = 0
                game_finished = False
                show_feedback_screen = False
    
            if next_level_button.is_clicked(mouse_pos, event):
                return "level2"  # Signal to main.py to go to level 2

        pygame.display.flip()
        clock.tick(60)
    
