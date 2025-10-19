import pygame, sys
from settings import *
from player import Player
from npc import NPC
from ui import UI
from store import CoffeeShop
import functions
from action_tracker import action_tracker

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("☕ Cosmic Café – Financial Literacy Game")
clock = pygame.time.Clock()

# Camera/scroll system
camera_x = 0
camera_y = 0

# Player
player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
all_sprites = pygame.sprite.Group(player)

# Initialize player debts dictionary if not exists
if not hasattr(player, 'debts'):
    player.debts = {
        'Banker Bard': 0,
        'Poultry Guy Pip': 0,
        'Farmer Finn': 0,
        'Witch of Woe': 0
    }

# Coffee Shop
coffee_shop = CoffeeShop((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))

# NPCs
npcs = pygame.sprite.Group()
farmer = NPC("Farmer Finn", "./src/assets/farmer.png", pos=(300, 200))
poultry = NPC("Poultry Guy Pip", "./src/assets/poultry-guy.png", pos=(800, 600))
witch = NPC("Witch of Woe", "./src/assets/evil-wizard.png", pos=(1200, 300))
banker = NPC("Banker Bard", "./src/assets/banker.png", pos=(1600, 800))
npcs.add(farmer, poultry, witch, banker)

# Character list for UI
characters = ["Farmer Finn", "Poultry Guy Pip", "Witch of Woe", "Banker Bard"]

# UI
ui = UI(screen)

# Show tutorial on first run
if not functions.game_state.tutorial_shown:
    functions.show_tutorial(ui, player)
    functions.game_state.tutorial_shown = True

def draw_gradient_background(screen):
    """Farm/mystical small-town background with visible dark objects."""
    import time, math
    current_time = time.time()

    # Sky colors: dark top to warm horizon
    top_sky = (20, 25, 50)         # night/dusk blue
    middle_sky = (50, 40, 80)      # soft purple
    bottom_sky = (150, 100, 90)    # warm sunrise/sunset near horizon

    # Ground/farm colors
    ground_top = (60, 80, 50)      # darker green
    ground_bottom = (100, 120, 70) # lighter green

    for y in range(SCREEN_HEIGHT):
        factor = y / SCREEN_HEIGHT
        if factor < 0.6:  # sky part
            interp = factor / 0.6
            r = int(top_sky[0] + (middle_sky[0] - top_sky[0]) * interp)
            g = int(top_sky[1] + (middle_sky[1] - top_sky[1]) * interp)
            b = int(top_sky[2] + (middle_sky[2] - top_sky[2]) * interp)
        elif factor < 0.8:  # near horizon
            interp = (factor - 0.6) / 0.2
            r = int(middle_sky[0] + (bottom_sky[0] - middle_sky[0]) * interp)
            g = int(middle_sky[1] + (bottom_sky[1] - middle_sky[1]) * interp)
            b = int(middle_sky[2] + (bottom_sky[2] - middle_sky[2]) * interp)
        else:  # ground/farm
            interp = (factor - 0.8) / 0.2
            r = int(ground_top[0] + (ground_bottom[0] - ground_top[0]) * interp)
            g = int(ground_top[1] + (ground_bottom[1] - ground_top[1]) * interp)
            b = int(ground_top[2] + (ground_bottom[2] - ground_top[2]) * interp)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_game_status(screen, player):
    """Display game status messages"""
    total_debt = sum(player.debts.values()) if player.debts else 0
    status = functions.check_game_status(player)
    
    font = pygame.font.SysFont("arial", 14)
    
    if status == "WIN":
        msg = "🎉 YOU WON! Goal achieved: 500+ gold, 0 debt!"
        color = (0, 255, 0)
        
        actions = action_tracker.get_action_summary()
        full_msg = msg 
        text = font.render(full_msg, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 20))
        
    elif status == "LOSE":
        msg = f"💀 GAME OVER! Debt spiral: {int(total_debt)} gold owed"
        color = (255, 0, 0)
        
        full_msg = msg 
        text = font.render(full_msg, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 20))

# Main loop
running = True
last_debt_update = 0
DEBT_UPDATE_INTERVAL = 30  # seconds

while running:
    clock.tick(FPS)

    # Update debts
    current_time = pygame.time.get_ticks() / 1000  # convert ms → seconds
    if current_time - last_debt_update >= DEBT_UPDATE_INTERVAL:
        last_debt_update = current_time
        total_debt = player.update_debts()
        print("Updated debts:", player.debts)
        print("Total debt:", total_debt)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # MOUSE CLICK - Pass to UI handler
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            ui.handle_click(mouse_pos, player)

    keys = pygame.key.get_pressed()
    player.move(keys)

    # Update camera to follow player
    camera_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_y = player.rect.centery - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, WORLD_WIDTH - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - SCREEN_HEIGHT))

    # Draw background
    draw_gradient_background(screen)

    # Draw coffee shop
    coffee_shop_offset = coffee_shop.rect.copy()
    coffee_shop_offset.x -= camera_x
    coffee_shop_offset.y -= camera_y
    screen.blit(coffee_shop.image, coffee_shop_offset)

    # Draw NPCs
    for npc in npcs:
        npc_offset = npc.rect.copy()
        npc_offset.x -= camera_x
        npc_offset.y -= camera_y
        screen.blit(npc.image, npc_offset)

    # Draw player
    player_offset = player.rect.copy()
    player_offset.x -= camera_x
    player_offset.y -= camera_y
    screen.blit(player.image, player_offset)

    # Draw UI (panels + menus + popups)
    ui.draw_all(player, characters, coffee_shop=coffee_shop, npcs=list(npcs))
    
    # Draw game status
    draw_game_status(screen, player)

    pygame.display.flip()

pygame.quit()
sys.exit()