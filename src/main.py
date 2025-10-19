import pygame
import sys
import subprocess
import os

from settings import PURPLE

pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Financial Learning Adventure")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)

# Fonts
BASE_FONT_SIZE = 48
FONT_NAME = None  # Default font
SMALL_FONT = pygame.font.SysFont(None, 28)

# Background
background = pygame.image.load("./src/assets/mainimg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def draw_button(text, color, x, y, width=200, height=100):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, rect, 3, border_radius=15)

    # Dynamically scale font to fit text inside button
    font_size = BASE_FONT_SIZE
    font = pygame.font.SysFont(FONT_NAME, font_size)
    text_render = font.render(text, True, BLACK)
    while (text_render.get_width() > width - 10 or text_render.get_height() > height - 10) and font_size > 10:
        font_size -= 2
        font = pygame.font.SysFont(FONT_NAME, font_size)
        text_render = font.render(text, True, BLACK)

    # Center text
    screen.blit(text_render, (x + width//2 - text_render.get_width()//2,
                              y + height//2 - text_render.get_height()//2))
    return rect

running = True
while running:
    screen.blit(background, (0, 0))

    # Title
    title_font = pygame.font.SysFont(FONT_NAME, 48)
    title = title_font.render("Welcome to Your Financial Learning Adventure!", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    # Description
    desc = SMALL_FONT.render("Choose a topic to begin your learning journey:", True, WHITE)
    screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 160))

    # Buttons - same width and height for consistency
    button_width = 200
    button_height = 100
    spacing = 50
    start_x = (WIDTH - (4 * button_width + 3 * spacing)) // 2  # space for 4 buttons
    y_pos = 400

    budgeting_btn = draw_button("Budgeting", GREEN, start_x, y_pos, button_width, button_height)
    scams_btn = draw_button("Scams", RED, start_x + button_width + spacing, y_pos, button_width, button_height)
    loans_btn = draw_button("Loans & Debt", BLUE, start_x + 2 * (button_width + spacing), y_pos, button_width, button_height)
    basics_btn = draw_button("Credit Basics", PURPLE, start_x + 3 * (button_width + spacing), y_pos, button_width, button_height)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if budgeting_btn.collidepoint(event.pos):
                pygame.quit()
                subprocess.run(["python", os.path.join("src", "credit.py")])
                sys.exit()
            elif scams_btn.collidepoint(event.pos):
                pygame.quit()
                subprocess.run(["python", os.path.join("src", "whack", "main.py")])
                sys.exit()
            elif loans_btn.collidepoint(event.pos):
                pygame.quit()
                subprocess.run(["python", os.path.join("src", "loans_main.py")])
                sys.exit()
            elif basics_btn.collidepoint(event.pos):
                pygame.quit()
                subprocess.run(["python", os.path.join("src", "CredCity","credcity.py")])
                sys.exit()

pygame.quit()
sys.exit()
