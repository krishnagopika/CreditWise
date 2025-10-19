import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Social Media Privacy Quiz")

# Colors
INSTAGRAM_PURPLE = (193, 53, 132)
INSTAGRAM_ORANGE = (225, 48, 108)
INSTAGRAM_YELLOW = (245, 166, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (239, 239, 239)
DARK_GRAY = (115, 115, 115)
GREEN = (0, 200, 0)
RED = (255, 80, 80)
BLUE = (0, 120, 255)
# Colors
INSTAGRAM_PURPLE = (193, 53, 132)    # Change this
INSTAGRAM_ORANGE = (225, 48, 108)    # Change this
INSTAGRAM_YELLOW = (245, 166, 35)    # Change this

# Fonts
font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 28, bold=True)
small_font = pygame.font.SysFont('Arial', 16)
post_font = pygame.font.SysFont('Arial', 18)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)
        
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InstagramPost:
    def __init__(self, username, profile_pic_color, post_image_color, caption, options, correct_index, explanation):
        self.username = username
        self.profile_pic_color = profile_pic_color
        self.post_image_color = post_image_color
        self.caption = caption
        self.options = options
        self.correct_index = correct_index
        self.explanation = explanation

def draw_instagram_ui():
    # Instagram gradient background
    for y in range(HEIGHT):
        alpha = y / HEIGHT
        color = (
            int(INSTAGRAM_PURPLE[0] * (1 - alpha) + INSTAGRAM_ORANGE[0] * alpha),
            int(INSTAGRAM_PURPLE[1] * (1 - alpha) + INSTAGRAM_ORANGE[1] * alpha),
            int(INSTAGRAM_PURPLE[2] * (1 - alpha) + INSTAGRAM_ORANGE[2] * alpha)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_instagram_post(post, selected_option=None):
    # Main post container
    post_rect = pygame.Rect(50, 80, WIDTH - 100, 350)
    pygame.draw.rect(screen, WHITE, post_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, post_rect, 2, border_radius=15)
    
    # Profile header
    header_rect = pygame.Rect(60, 90, WIDTH - 120, 60)
    
    # Profile picture
    pygame.draw.circle(screen, post.profile_pic_color, (80, 120), 20)
    
    # Username
    username_text = font.render(post.username, True, BLACK)
    screen.blit(username_text, (110, 105))
    
    # Options button (...)
    options_text = font.render("···", True, BLACK)
    screen.blit(options_text, (WIDTH - 80, 105))
    
    # Post image
    image_rect = pygame.Rect(60, 150, WIDTH - 120, 150)
    pygame.draw.rect(screen, post.post_image_color, image_rect)
    
    # Action buttons (like, comment, share)
    pygame.draw.rect(screen, LIGHT_GRAY, (60, 310, WIDTH - 120, 40))
    
    # Caption
    caption_text = post_font.render(post.caption, True, BLACK)
    screen.blit(caption_text, (70, 360))
    
    # Options
    option_rects = []
    for i, option in enumerate(post.options):
        option_rect = pygame.Rect(100, 430 + i * 60, WIDTH - 200, 50)
        
        # Highlight selected option
        if selected_option == i:
            pygame.draw.rect(screen, LIGHT_GRAY, option_rect, border_radius=10)
        
        pygame.draw.rect(screen, BLACK, option_rect, 2, border_radius=10)
        
        option_text = font.render(option, True, BLACK)
        screen.blit(option_text, (option_rect.centerx - option_text.get_width()//2, 
                                 option_rect.centery - option_text.get_height()//2))
        
        option_rects.append(option_rect)
    
    return option_rects

def show_feedback(is_correct, explanation, post):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Feedback panel
    panel_rect = pygame.Rect(100, 150, WIDTH - 200, 300)
    pygame.draw.rect(screen, WHITE, panel_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=15)
    
    color = GREEN if is_correct else RED
    symbol = "✓" if is_correct else "✗"
    
    result_text = title_font.render(f"{symbol} {'SAFE CHOICE!' if is_correct else 'RISKY CHOICE!'}", True, color)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 180))
    
    # Explanation (wrapped)
    y_offset = 230
    words = explanation.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < WIDTH - 250:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    for line in lines:
        text = font.render(line, True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 30
    
    # Show the correct safe option
    safe_option_text = font.render(f"Safe choice: {post.options[post.correct_index]}", True, GREEN)
    screen.blit(safe_option_text, (WIDTH//2 - safe_option_text.get_width()//2, y_offset + 20))
    
    continue_text = font.render("Click anywhere to continue...", True, BLACK)
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 400))

def show_final_score(score, total_questions):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    panel_rect = pygame.Rect(100, 150, WIDTH - 200, 300)
    pygame.draw.rect(screen, WHITE, panel_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=15)
    
    # Score result
    if score == total_questions * 10:
        result = "PRIVACY EXPERT!"
        color = GREEN
    elif score >= total_questions * 7:
        result = "PRIVACY PRO!"
        color = BLUE
    else:
        result = "LEARNING!"
        color = INSTAGRAM_PURPLE
    
    result_text = title_font.render(result, True, color)
    score_text = title_font.render(f"Final Score: {score}/{total_questions * 10}", True, BLACK)
    
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 180))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 230))
    
    # Key privacy tips
    tips_title = font.render("Social Media Safety Tips:", True, INSTAGRAM_PURPLE)
    screen.blit(tips_title, (WIDTH//2 - tips_title.get_width()//2, 280))
    
    tips = [
        "Never share personal info like birth dates or addresses",
        "Turn off location sharing for sensitive posts",
        "Only accept friend requests from people you know",
        "Avoid posting vacation plans or when you're away",
        "Never share financial information or card details"
    ]
    
    for i, tip in enumerate(tips):
        tip_text = small_font.render(tip, True, BLACK)
        screen.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 320 + i*25))

    # ADD THE ENDING MESSAGE HERE - right after the tips
    ending_message = font.render("Stay safe online! Always think before you post. 🔒", True, INSTAGRAM_PURPLE)
    screen.blit(ending_message, (WIDTH//2 - ending_message.get_width()//2, 450))

    # RETURN the button position so it can be used in main()
    return Button(WIDTH//2 - 80, 500, 160, 40, "PLAY AGAIN", WHITE, LIGHT_GRAY)
def main():
    clock = pygame.time.Clock()
    
    # Social media quiz questions
    posts = [
        InstagramPost(
            username="travel_lover123",
            profile_pic_color=(255, 150, 150),
            post_image_color=(100, 200, 255),  # Beach color
            caption="2 weeks in Hawaii! So excited for this vacation!",
            options=[
                "Public + Location ON ",
                "Friends Only + No Location",
            ],
            correct_index=1,
            explanation="Sharing vacation plans publicly reveals your home is empty. Friends-only without location is safest!"
        ),
        InstagramPost(
            username="career_growth",
            profile_pic_color=(150, 200, 255),
            post_image_color=(200, 200, 200),  # Office color
            caption="So excited about my new job at Capital One!",
            options=[
                "Public - Share the great news!",
                "Friends Only - Keep it professional",
            ],
            correct_index=1,
            explanation="Never reveal your workplace publicly! Scammers can use this for social engineering attacks."
        ),
        InstagramPost(
            username="birthday_queen",
            profile_pic_color=(255, 200, 150),
            post_image_color=(255, 220, 150),  # Cake color
            caption="Best birthday ever! Feeling so loved today!",
            options=[
                "Show Full Birth Date",
                "Friends Only + Hide Date",
            ],
            correct_index=1,
            explanation="Birth dates are key identity verification info. Never share them publicly - friends-only without date is safest!"
        )
    ]
    
    # Game state
    current_post = 0
    score = 0
    show_feedback_screen = False
    current_feedback = None
    game_finished = False
    selected_option = None
    
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
                option_rects = draw_instagram_post(posts[current_post], selected_option)
                
                # Check option clicks
                for i, rect in enumerate(option_rects):
                    if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(mouse_pos):
                        selected_option = i
                        if i == posts[current_post].correct_index:
                            score += 10
                            show_feedback_screen = True
                            current_feedback = (True, posts[current_post].explanation, posts[current_post])
                        else:
                            show_feedback_screen = True
                            current_feedback = (False, posts[current_post].explanation, posts[current_post])
            
            elif show_feedback_screen and event.type == pygame.MOUSEBUTTONDOWN:
                show_feedback_screen = False
                selected_option = None
                current_post += 1
                if current_post >= len(posts):
                    game_finished = True
            
            elif game_finished and event.type == pygame.MOUSEBUTTONDOWN:
                # Restart game
                current_post = 0
                score = 0
                game_finished = False
                selected_option = None
        
        # Draw everything
        draw_instagram_ui()
        
        # Title and score
        title = title_font.render("Social Media Privacy Quiz", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        score_text = font.render(f"Privacy Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 175, 25))
        
        progress_text = font.render(f"Post {current_post + 1}/{len(posts)}", True, WHITE)
        screen.blit(progress_text, (50, 25))
        
        if not game_finished and not show_feedback_screen:
            draw_instagram_post(posts[current_post], selected_option)
            
            # Instructions
            instruct = font.render("Click the safest privacy option for this post:", True, WHITE)
            screen.blit(instruct, (WIDTH//2 - instruct.get_width()//2, 560))
        
        elif show_feedback_screen and current_feedback:
            show_feedback(current_feedback[0], current_feedback[1], current_feedback[2])
        
        elif game_finished:
            play_again_button = show_final_score(score, len(posts))
            
            # Play Again button
            play_again_button = Button(WIDTH//2 - 80, 480, 160, 40, "PLAY AGAIN", WHITE, LIGHT_GRAY)
            play_again_button.check_hover(mouse_pos)
            play_again_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()