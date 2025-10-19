import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Email Security Scanner - Level 2")

# Colors
DARK_NAVY = (10, 31, 58)
ELECTRIC_CYAN = (0, 212, 255)
SOFT_PURPLE = (108, 99, 255)
MINT_GREEN = (0, 255, 157)
SOFT_RED = (255, 107, 107)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 40, 80)
PURPLE = (40, 20, 80)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)  # ADD THIS LINE
BLACK = (0, 0, 0)


# Fonts
font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 28, bold=True)
email_font = pygame.font.SysFont('Courier New', 16)
score_font = pygame.font.SysFont('Arial', 24, bold=True)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

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

def draw_city_background():
    # Dark gradient background
    for y in range(HEIGHT):
        alpha = y / HEIGHT
        color = (
            int(DARK_NAVY[0] * (1 - alpha) + PURPLE[0] * alpha),
            int(DARK_NAVY[1] * (1 - alpha) + PURPLE[1] * alpha),
            int(DARK_NAVY[2] * (1 - alpha) + PURPLE[2] * alpha)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # City skyline (simple rectangles)
    building_colors = [DARK_BLUE, (30, 30, 60), (40, 40, 80)]
    building_heights = [120, 80, 150, 100, 180, 90, 130]
    building_width = 80
    for i, height in enumerate(building_heights):
        x = i * (building_width + 10)
        color = building_colors[i % len(building_colors)]
        pygame.draw.rect(screen, color, (x, HEIGHT - height, building_width, height))
        
        # Building windows
        window_color = ELECTRIC_CYAN if random.random() > 0.7 else YELLOW
        for floor in range(3):
            for col in range(3):
                wx = x + 15 + col * 20
                wy = HEIGHT - height + 20 + floor * 30
                if random.random() > 0.3:  # Some windows are dark
                    pygame.draw.rect(screen, window_color, (wx, wy, 10, 15))

def draw_email_display(email, current, total, score):
    # Email container
    email_rect = pygame.Rect(50, 80, WIDTH - 100, 350)
    pygame.draw.rect(screen, WHITE, email_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, email_rect, 2, border_radius=15)
    
    # Header
    header_rect = pygame.Rect(60, 90, WIDTH - 120, 40)
    pygame.draw.rect(screen, LIGHT_BLUE, header_rect, border_radius=8)
    
    # Email info
    from_text = email_font.render(f"From: {email['sender']}", True, BLACK)
    subject_text = email_font.render(f"Subject: {email['subject']}", True, BLACK)
    
    screen.blit(from_text, (70, 100))
    screen.blit(subject_text, (70, 130))
    
    # Email body (wrapped)
    body_rect = pygame.Rect(70, 160, WIDTH - 140, 200)
    words = email['body'].split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if email_font.size(test_line)[0] < WIDTH - 180:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    y_offset = 160
    for line in lines:
        if y_offset < 340:  # Don't go beyond email container
            body_text = email_font.render(line, True, BLACK)
            screen.blit(body_text, (70, y_offset))
            y_offset += 20
    
    # Progress and score
    progress_text = font.render(f"Email {current + 1}/{total}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    
    screen.blit(progress_text, (WIDTH//2 - progress_text.get_width()//2, 30))
    screen.blit(score_text, (WIDTH - 120, 30))

def draw_feedback(is_correct, clues, email_type, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Feedback panel
    panel_rect = pygame.Rect(100, 100, WIDTH - 200, 400)
    pygame.draw.rect(screen, WHITE, panel_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=15)
    
    # Result
    color = MINT_GREEN if is_correct else SOFT_RED
    symbol = "✓" if is_correct else "✗"
    result = "CORRECT!" if is_correct else "INCORRECT!"
    
    result_text = title_font.render(f"{symbol} {result}", True, color)
    email_type_text = font.render(f"This email was {email_type.upper()}", True, BLACK)
    
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 130))
    screen.blit(email_type_text, (WIDTH//2 - email_type_text.get_width()//2, 170))
    
    # Clues
    clues_title = font.render("Key Security Clues:", True, ELECTRIC_CYAN)
    screen.blit(clues_title, (WIDTH//2 - clues_title.get_width()//2, 210))
    
    for i, clue in enumerate(clues):
        clue_text = font.render(clue, True, BLACK)
        screen.blit(clue_text, (WIDTH//2 - clue_text.get_width()//2, 240 + i*30))
    
    # Current score
    score_text = font.render(f"Current Score: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 350))
    
    # Continue button
    continue_button = Button(WIDTH//2 - 80, 400, 160, 40, "CONTINUE", ELECTRIC_CYAN, SOFT_PURPLE)
    return continue_button

def show_email_results(score, total_emails):
    screen.fill(DARK_NAVY)
    
    # Results title
    title = title_font.render("SCANNING COMPLETE!", True, ELECTRIC_CYAN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Final score
    score_text = title_font.render(f"Final Score: {score}/{total_emails * 10}", True, MINT_GREEN)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 160))
    
    # Performance rating
    if score >= 30:
        performance = "🏆 Email Security Expert!"
        color = MINT_GREEN
    elif score >= 20:
        performance = "🌟 Great Job!"
        color = ELECTRIC_CYAN
    else:
        performance = "📚 Keep Learning!"
        color = SOFT_RED
        
    perf_text = font.render(performance, True, color)
    screen.blit(perf_text, (WIDTH//2 - perf_text.get_width()//2, 210))
    
    # Key takeaways
    takeaways = [
        "✓ Always verify sender email addresses",
        "✓ Watch for spelling errors and poor grammar", 
        "✓ Never click suspicious links in emails",
        "✓ Capital One will never ask for passwords via email",
        "✓ Be suspicious of urgent threats and too-good-to-be-true offers"
    ]
    
    for i, takeaway in enumerate(takeaways):
        takeaway_text = font.render(takeaway, True, WHITE)
        screen.blit(takeaway_text, (WIDTH//2 - takeaway_text.get_width()//2, 260 + i*40))
    
    # Continue button
    continue_button = Button(WIDTH//2 - 100, 480, 200, 50, "CONTINUE", ELECTRIC_CYAN, SOFT_PURPLE)
    
    # NEXT LEVEL button
    next_level_button = Button(WIDTH//2 - 100, 535, 200, 50, "NEXT LEVEL →", MINT_GREEN, (0, 200, 0))
    
    waiting = True
    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        continue_button.check_hover(mouse_pos)
        next_level_button.check_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if continue_button.is_clicked(mouse_pos, event):
                waiting = False
            if next_level_button.is_clicked(mouse_pos, event):
                pygame.quit()  # Close current level
                try:
                    import level3_socialmedia  # Import your level3 file
                    level3_socialmedia.main()  # Start level3
                except ImportError:
                    print("Level 3 not found! Make sure level3_instagram.py is in the same folder.")
                return
        
        continue_button.draw(screen)
        next_level_button.draw(screen)
        pygame.display.flip()

def main():
    # Email data
    emails = [
        # LEGITIMATE EMAILS
        {
            "type": "legitimate",
            "sender": "capitalone@emails.capitalone.com",
            "subject": "Your Monthly Statement is Ready",
            "body": "Dear Valued Customer, Your monthly credit card statement is now available for review. Please log in to your secure online account to view your statement details and payment information. You can access your statement through our official mobile app or by visiting our secure website. Thank you for choosing Capital One.",
            "clues": [
                "Official Capital One email domain",
                "Professional, non-urgent language", 
                "No requests for personal information",
                "Encourages secure login to official platforms"
            ]
        },
        {
            "type": "legitimate",
            "sender": "no-reply@alerts.capitalone.com", 
            "subject": "Security Notice: New Login Detected",
            "body": "We noticed a new login to your Capital One account: Device: iPhone 13 Pro Location: New York, NY Time: Today, 2:30 PM EST If this was you, no action is needed. Your account remains secure. If this wasn't you, please contact our security team immediately.",
            "clues": [
                "Provides specific, verifiable details",
                "Informative but not demanding immediate action",
                "Official Capital One alerts domain",
                "No suspicious links"
            ]
        },
        # PHISHING EMAILS  
        {
            "type": "phishing", 
            "sender": "security@capitalone-support.net",
            "subject": "URGENT: Account Suspension Warning!",
            "body": "IMPORTANT SECURITY ALERT: We detected suspicious login attempts on your account. Your account will be SUSPENDED in 24 hours unless you verify your identity immediately. CLICK HERE NOW to verify your account and prevent suspension. Do not ignore this warning!",
            "clues": [
                "Suspicious domain (not official Capital One)",
                "Creates false urgency and threats", 
                "Contains suspicious link",
                "Pressure tactics to bypass careful thinking"
            ]
        },
        {
            "type": "phishing",
            "sender": "rewards@capitalone-gifts.com",
            "subject": "CONGRATULATIONS! You Won $500 Amazon Gift Card!", 
            "body": "EXCLUSIVE OFFER: You've been selected for our special reward program! You won a $500 Amazon Gift Card! Click here to claim your prize now! HURRY! This offer expires in 2 hours. Limited availability! Just pay $4.99 shipping fee to receive your gift card.",
            "clues": [
                "Too good to be true offer",
                "Asks for payment for 'free' gift",
                "Creates false scarcity and urgency",
                "Unofficial rewards domain"
            ]
        }
    ]
    
    current_email = 0
    score = 0
    shuffled_emails = random.sample(emails, len(emails))
    
    clock = pygame.time.Clock()
    running = True
    show_feedback = False
    feedback_data = None
    
    # Create particles for background
    particles = [Particle() for _ in range(30)]
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if not show_feedback:
                # Check button clicks
                legit_button = Button(WIDTH//2 - 200, 450, 180, 50, "LEGITIMATE", MINT_GREEN, (0, 200, 0))
                phishing_button = Button(WIDTH//2 + 20, 450, 180, 50, "PHISHING", SOFT_RED, (200, 0, 0))
                
                if legit_button.is_clicked(mouse_pos, event):
                    is_correct = (shuffled_emails[current_email]["type"] == "legitimate")
                    if is_correct:
                        score += 10
                    feedback_data = (is_correct, shuffled_emails[current_email]["clues"], shuffled_emails[current_email]["type"], score)
                    show_feedback = True
                elif phishing_button.is_clicked(mouse_pos, event):
                    is_correct = (shuffled_emails[current_email]["type"] == "phishing")
                    if is_correct:
                        score += 10
                    feedback_data = (is_correct, shuffled_emails[current_email]["clues"], shuffled_emails[current_email]["type"], score)
                    show_feedback = True
            else:
                # Continue button in feedback
                continue_button = draw_feedback(feedback_data[0], feedback_data[1], feedback_data[2], feedback_data[3])
                if continue_button.is_clicked(mouse_pos, event):
                    show_feedback = False
                    current_email += 1
                    if current_email >= len(shuffled_emails):
                        show_email_results(score, len(shuffled_emails))
                        running = False
        
        # Draw everything
        draw_city_background()
        
        # Update and draw particles
        for particle in particles:
            particle.update()
            particle.draw()
        
        if not show_feedback and current_email < len(shuffled_emails):
            draw_email_display(shuffled_emails[current_email], current_email, len(shuffled_emails), score)
            
            # Draw buttons
            legit_button = Button(WIDTH//2 - 200, 450, 180, 50, "LEGITIMATE", MINT_GREEN, (0, 200, 0))
            phishing_button = Button(WIDTH//2 + 20, 450, 180, 50, "PHISHING", SOFT_RED, (200, 0, 0))
            
            legit_button.check_hover(mouse_pos)
            phishing_button.check_hover(mouse_pos)
            
            legit_button.draw(screen)
            phishing_button.draw(screen)
        elif show_feedback and feedback_data:
            continue_button = draw_feedback(feedback_data[0], feedback_data[1], feedback_data[2], feedback_data[3])
            continue_button.check_hover(mouse_pos)
            continue_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()