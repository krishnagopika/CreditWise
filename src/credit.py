import pygame
import sys
import random
import os

pygame.init()

# Get screen info and set responsive dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Use a reasonable default size but allow for different screen sizes
WIDTH = min(1200, SCREEN_WIDTH - 100)  # Max 1200px wide, leave some margin
HEIGHT = min(800, SCREEN_HEIGHT - 100)  # Max 800px tall, leave some margin

# If screen is too small, use minimum viable size
WIDTH = max(800, WIDTH)
HEIGHT = max(600, HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Grocery Budget Adventure")

# Colors - Grocery Store Theme
DARK_OVERLAY = (0, 0, 0, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 179, 113)  # Fresh green
RED = (220, 20, 60)     # Sale red
BLUE = (30, 144, 255)   # Cool blue
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 215, 0)  # Golden yellow
ORANGE = (255, 140, 0)  # Orange
PURPLE = (147, 112, 219) # Purple
CREAM = (255, 253, 208) # Cream background
WOOD = (210, 180, 140)  # Wooden shelves
AISLE_GREEN = (144, 238, 144) # Aisle color

# Responsive scaling functions
def get_scale_factor():
    """Calculate scale factor based on screen size"""
    base_width, base_height = 800, 600
    scale_x = WIDTH / base_width
    scale_y = HEIGHT / base_height
    return min(scale_x, scale_y)  # Use smaller scale to ensure everything fits

def scale_font_size(base_size):
    """Scale font size based on screen size"""
    scale = get_scale_factor()
    return max(12, int(base_size * scale))  # Minimum 12pt font

def scale_value(base_value):
    """Scale any value (margins, button sizes, etc.)"""
    return int(base_value * get_scale_factor())

def refresh_fonts():
    """Refresh fonts with current scale factor"""
    global TITLE_FONT, FONT, POPUP_FONT, SMALL_FONT
    TITLE_FONT = pygame.font.SysFont("arial", scale_font_size(36), bold=True)
    FONT = pygame.font.SysFont("arial", scale_font_size(28))
    POPUP_FONT = pygame.font.SysFont("arial", scale_font_size(24))
    SMALL_FONT = pygame.font.SysFont("arial", scale_font_size(20))

# Initialize responsive fonts
refresh_fonts()

# Game States
MAIN_MENU = "main_menu"
LEVEL_1_GAME = "level_1_game"
LEVEL_2_GAME = "level_2_game"
LEVEL_3_GAME = "level_3_game"
LEVEL_4_GAME = "level_4_game"
LEVEL_5_GAME = "level_5_game"
LEVEL_6_GAME = "level_6_game"

current_game_state = MAIN_MENU
current_level = 1
total_points = 0
completed_levels = set()

# Load images (replace with your actual PNG files)


# Load background image
def load_background():
    try:
        background = pygame.image.load("./src/assets/background.webp")
        # Scale background to fit screen
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        return background
    except:
        # Fallback to solid color if image not found
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(CREAM)
        return surf


class Level1Game:  # Budget Allocation - Grocery Store Budget
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.total_budget = 100
        self.categories = {
            "Fresh Produce": {"allocated": 0, "recommended": 30, "color": GREEN, "icon": ""},
            "Dairy & Eggs": {"allocated": 0, "recommended": 25, "color": LIGHT_BLUE, "icon": ""},
            "Meat & Fish": {"allocated": 0, "recommended": 20, "color": RED, "icon": ""},
            "Pantry Items": {"allocated": 0, "recommended": 15, "color": ORANGE, "icon": ""},
            "Treats & Snacks": {"allocated": 0, "recommended": 10, "color": YELLOW, "icon": ""}
        }
        self.remaining = self.total_budget
        
    def allocate_money(self, category, amount):
        if self.remaining >= amount:
            self.categories[category]["allocated"] += amount
            self.remaining -= amount
            return True
        return False
        
    def get_score(self):
        score = 0
        for category, data in self.categories.items():
            difference = abs(data["allocated"] - data["recommended"])
            if difference <= 5:  # Within £5 of recommendation
                score += 20
        return score

class Level2Game:  # Grocery Shopping - Interactive Cart
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.budget = 50
        self.spent = 0
        self.cart = []
        self.items = [
            {"name": "Milk", "price": 1.2, "type": "need", "essential": True, "image": "milk"},
            {"name": "Bread", "price": 1.5, "type": "need", "essential": True, "image": "bread"},
            {"name": "Eggs", "price": 2.0, "type": "need", "essential": True, "image": "eggs"},
            {"name": "Apples", "price": 2.5, "type": "need", "essential": False, "image": "apples"},
            {"name": "Rice", "price": 3.0, "type": "need", "essential": True, "image": "rice"},
            {"name": "Chicken", "price": 5.0, "type": "need", "essential": True, "image": "chicken"},
            {"name": "Chocolate", "price": 3.0, "type": "want", "essential": False, "image": "chocolate"},
            {"name": "Juice", "price": 2.5, "type": "want", "essential": False, "image": "juice"},
            {"name": "Chips", "price": 2.0, "type": "want", "essential": False, "image": "chips"},
            {"name": "Soda", "price": 2.5, "type": "want", "essential": False, "image": "soda"},
        ]
        random.shuffle(self.items)
        
    def add_to_cart(self, item_index):
        item = self.items[item_index]
        if self.spent + item["price"] <= self.budget:
            self.spent += item["price"]
            self.cart.append(item)
            return True
        return False
        
    def get_score(self):
        score = 0
        essentials_count = sum(1 for item in self.cart if item["essential"])
        if essentials_count >= 4:  # At least 4 essentials
            score += 50
        if self.spent <= self.budget:
            score += 30
        if self.spent >= self.budget * 0.7:  # Good utilization
            score += 20
        return min(100, score)

class Level3Game:  # Needs vs Wants - Grocery Edition
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.items = [
            ("Fresh Vegetables", "need", ""),
            ("Designer Ice Cream", "want", ""),
            ("Whole Grain Bread", "need", ""),
            ("Organic Milk", "need", ""),
            ("Premium Coffee", "want", ""),
            ("Basic Rice", "need", ""),
            ("Fancy Cupcakes", "want", ""),
            ("Canned Beans", "need", ""),
            ("Fresh Fruits", "need", ""),
            ("Gourmet Cheese", "want", ""),
        ]
        random.shuffle(self.items)
        self.current_item = 0
        self.correct = 0
        self.choices_made = []
        
    def make_choice(self, choice):
        correct_answer = self.items[self.current_item][1]
        is_correct = (choice == correct_answer)
        self.choices_made.append((self.items[self.current_item][0], choice, is_correct))
        if is_correct:
            self.correct += 1
        self.current_item += 1
        return is_correct
        
    def get_score(self):
        return (self.correct / len(self.items)) * 100

# Keep the other level classes but they won't be used for now
class Level4Game:  # Emergency Fund
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.completed = True
        
    def get_score(self):
        return 100

class Level5Game:  # Goal Setting
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.completed = True
        
    def get_score(self):
        return 100

class Level6Game:  # Compound Interest
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.completed = True
        
    def get_score(self):
        return 100

class PopupManager:
    def __init__(self):
        self.active_popup = None
        self.all_popups = []
        self.current_popup_index = -1
        
    def set_popups(self, popups_list):
        self.all_popups = popups_list
        self.current_popup_index = -1
        
    def show_next_popup(self):
        self.current_popup_index += 1
        if self.current_popup_index < len(self.all_popups):
            self.active_popup = self.all_popups[self.current_popup_index]
            return True
        else:
            self.active_popup = None
            return False
            
    def draw_popup(self, screen):
        if not self.active_popup:
            return []
            
        # Grocery-themed popup background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY)
        screen.blit(overlay, (0, 0))
        
        popup_width = min(scale_value(600), WIDTH - scale_value(100))
        popup_height = min(scale_value(400), HEIGHT - scale_value(100))
        popup_rect = pygame.Rect(WIDTH//2 - popup_width//2, HEIGHT//2 - popup_height//2, popup_width, popup_height)
        pygame.draw.rect(screen, CREAM, popup_rect, border_radius=15)
        pygame.draw.rect(screen, GREEN, popup_rect, 3, border_radius=15)
        
        # Add grocery pattern
        for i in range(0, popup_width, scale_value(40)):
            pygame.draw.line(screen, AISLE_GREEN, 
                           (popup_rect.x + i, popup_rect.y),
                           (popup_rect.x + i, popup_rect.y + popup_height), 1)
        
        buttons = []
        y_offset = popup_rect.y + scale_value(30)
        
        if "title" in self.active_popup:
            title = TITLE_FONT.render(self.active_popup["title"], True, GREEN)
            screen.blit(title, (popup_rect.centerx - title.get_width()//2, y_offset))
            y_offset += scale_value(60)
            
        if "content" in self.active_popup:
            if callable(self.active_popup["content"]):
                self.active_popup["content"](screen, popup_rect, y_offset)
                y_offset += scale_value(150)
            else:
                self.wrap_text(screen, self.active_popup["content"], BLACK, 
                             pygame.Rect(popup_rect.x + scale_value(30), y_offset, popup_width - scale_value(60), scale_value(150)), POPUP_FONT)
                y_offset += scale_value(120)
                
        button_y = popup_rect.y + scale_value(320)
        if "choices" in self.active_popup:
            for i, choice in enumerate(self.active_popup["choices"]):
                btn_width = scale_value(120)
                spacing = scale_value(20)
                total_width = len(self.active_popup["choices"]) * btn_width + (len(self.active_popup["choices"]) - 1) * spacing
                btn_x = popup_rect.centerx - total_width // 2 + i * (btn_width + spacing)
                
                btn_rect = pygame.Rect(btn_x, button_y, btn_width, scale_value(50))
                
                color = GREEN if choice.get("primary", False) else YELLOW
                pygame.draw.rect(screen, color, btn_rect, border_radius=10)
                pygame.draw.rect(screen, BLACK, btn_rect, 2, border_radius=10)
                
                text = POPUP_FONT.render(choice["text"], True, BLACK)
                screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - text.get_height()//2))
                
                buttons.append((btn_rect, choice["action"]))
        else:
            btn_rect = pygame.Rect(popup_rect.centerx - scale_value(70), button_y, scale_value(140), scale_value(50))
            pygame.draw.rect(screen, GREEN, btn_rect, border_radius=10)
            pygame.draw.rect(screen, BLACK, btn_rect, 2, border_radius=10)
            text = POPUP_FONT.render("Continue", True, BLACK)
            screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - text.get_height()//2))
            buttons.append((btn_rect, "next"))
            
        return buttons
        
    def wrap_text(self, screen, text, color, rect, font):
        words = text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] < rect.width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        
        y = rect.y
        for line in lines:
            if y + font.get_height() < rect.y + rect.height:
                rendered = font.render(line, True, color)
                screen.blit(rendered, (rect.x, y))
                y += font.get_height() + 5

def draw_background(screen):
    # Draw the background image
    background_image = load_background()
    screen.blit(background_image, (0, 0))

def draw_game_popup_overlay(screen):
    # Create black semi-transparent overlay for game popup
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))  # Black with 120 alpha (less opaque)
    screen.blit(overlay, (0, 0))

def draw_level1_game(screen):
    draw_background(screen)
    draw_game_popup_overlay(screen)
    
    # Store header
    header_rect = pygame.Rect(50, 20, WIDTH - 100, 80)
    pygame.draw.rect(screen, GREEN, header_rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, header_rect, 3, border_radius=15)
    
    title = TITLE_FONT.render("Weekly Grocery Budget Planner", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 35))
    
    # Budget display
    budget_rect = pygame.Rect(50, 100, WIDTH - 100, 80)
    pygame.draw.rect(screen, WHITE, budget_rect, border_radius=15)
    pygame.draw.rect(screen, BLUE, budget_rect, 3, border_radius=15)
    
    budget_text = SMALL_FONT.render(f"Total Weekly Budget: £{level1_game.total_budget}", True, BLUE)
    remaining_text = SMALL_FONT.render(f"Remaining: £{level1_game.remaining}", True, GREEN if level1_game.remaining > 0 else RED)
    screen.blit(budget_text, (70, 110))
    screen.blit(remaining_text, (70, 170))
    
    buttons = []
    y_pos = 200
    
    # Grocery department cards
    for i, (category, data) in enumerate(level1_game.categories.items()):
        dept_rect = pygame.Rect(50, y_pos + i*90, WIDTH - 100, 80)
        pygame.draw.rect(screen, WHITE, dept_rect, border_radius=15)
        pygame.draw.rect(screen, data["color"], dept_rect, 3, border_radius=15)
        
        # Department icon and name
        name_text = SMALL_FONT.render(category, True, BLACK)
        alloc_text = SMALL_FONT.render(f"Allocated: £{data['allocated']}", True, GREEN)
        rec_text = SMALL_FONT.render(f"Recommended: £{data['recommended']}", True, BLUE)
        
        if data["icon"]:
            icon_text = FONT.render(data["icon"], True, BLACK)
            screen.blit(icon_text, (70, y_pos + i*90 + 20))
        screen.blit(name_text, (110, y_pos + i*90 + 15))
        screen.blit(alloc_text, (110, y_pos + i*90 + 45))
        screen.blit(rec_text, (300, y_pos + i*90 + 45))
        
        # Money buttons styled as price tags
        for j, amount in enumerate([1, 5, 10]):
            btn_rect = pygame.Rect(600 + j*90, y_pos + i*90 + 20, 80, 40)
            pygame.draw.rect(screen, YELLOW, btn_rect, border_radius=8)
            pygame.draw.rect(screen, ORANGE, btn_rect, 2, border_radius=8)
            amount_text = SMALL_FONT.render(f"£{amount}", True, BLACK)
            screen.blit(amount_text, (btn_rect.centerx - amount_text.get_width()//2, btn_rect.centery - amount_text.get_height()//2))
            buttons.append((btn_rect, f"alloc_{i}_{amount}"))
    
    # Checkout button
    checkout_btn = pygame.Rect(WIDTH//2 - scale_value(120), HEIGHT - scale_value(80), scale_value(240), scale_value(50))
    pygame.draw.rect(screen, GREEN, checkout_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE, checkout_btn, 3, border_radius=10)
    checkout_text = FONT.render("Plan Complete", True, WHITE)
    screen.blit(checkout_text, (checkout_btn.centerx - checkout_text.get_width()//2, checkout_btn.centery - checkout_text.get_height()//2))
    buttons.append((checkout_btn, "complete_level"))
    
    return buttons

def draw_level2_game(screen):
    draw_background(screen)
    draw_game_popup_overlay(screen)
    
    # Store header
    header_rect = pygame.Rect(50, 20, WIDTH - 100, 60)
    pygame.draw.rect(screen, BLUE, header_rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, header_rect, 3, border_radius=15)
    
    title = TITLE_FONT.render("Smart Shopping Challenge", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 35))
    
    # Budget display
    budget_display = pygame.Rect(50, 100, WIDTH - 100, 60)
    pygame.draw.rect(screen, WHITE, budget_display, border_radius=10)
    pygame.draw.rect(screen, GREEN, budget_display, 3, border_radius=10)
    
    budget_text = FONT.render(f"Budget: £{level2_game.budget}", True, GREEN)
    spent_text = FONT.render(f"Spent: £{level2_game.spent:.2f}", True, RED if level2_game.spent > level2_game.budget else BLUE)
    remaining_text = FONT.render(f"Left: £{level2_game.budget - level2_game.spent:.2f}", True, ORANGE)
    
    screen.blit(budget_text, (70, 110))
    screen.blit(spent_text, (300, 110))
    screen.blit(remaining_text, (700, 110))
    
    buttons = []
    
    # Grocery items on shelves
    shelf_y = 180
    for i, item in enumerate(level2_game.items):
        shelf_pos = i % 4  # 4 items per shelf
        shelf_row = i // 4
        
        item_rect = pygame.Rect(80 + shelf_pos * 180, shelf_y + shelf_row * 140, 160, 120)
        
        # Draw shelf
        pygame.draw.rect(screen, WOOD, (70 + shelf_pos * 180, shelf_y + shelf_row * 140 + 110, 180, 10))
        
        # Item card
        bg_color = GREEN if item["type"] == "need" else YELLOW
        pygame.draw.rect(screen, WHITE, item_rect, border_radius=10)
        pygame.draw.rect(screen, bg_color, item_rect, 3, border_radius=10)
        
        # Item image
        try:
            item_img = GROCERY_IMAGES[item["image"]]
            screen.blit(item_img, (item_rect.x + 50, item_rect.y + 10))
        except:
            # No fallback needed - just show the item name
            pass
        
        # Item info
        name_text = SMALL_FONT.render(item["name"], True, BLACK)
        price_text = SMALL_FONT.render(f"£{item['price']:.2f}", True, GREEN)
        type_text = SMALL_FONT.render("need" if item["essential"] else "want", True, bg_color)
        
        screen.blit(name_text, (item_rect.x + 50, item_rect.y + 50))
        screen.blit(price_text, (item_rect.x + 10, item_rect.y + 90))
        screen.blit(type_text, (item_rect.x + 100, item_rect.y + 10))
        
        # Add to cart button
        add_btn = pygame.Rect(item_rect.x + 85, item_rect.y + 85, 60, 25)
        pygame.draw.rect(screen, BLUE, add_btn, border_radius=5)
        pygame.draw.rect(screen, WHITE, add_btn, 2, border_radius=5)
        add_text = SMALL_FONT.render("add", True, WHITE)
        screen.blit(add_text, (add_btn.centerx - add_text.get_width()//2, add_btn.centery - add_text.get_height()//2))
        buttons.append((add_btn, f"add_{i}"))
    
    # Shopping cart section
    cart_rect = pygame.Rect(50, HEIGHT - 150, WIDTH - 100, 60)
    pygame.draw.rect(screen, WHITE, cart_rect, border_radius=10)
    pygame.draw.rect(screen, PURPLE, cart_rect, 3, border_radius=10)
    
    cart_text = FONT.render(f"Items in Cart: {len(level2_game.cart)}", True, PURPLE)
    screen.blit(cart_text, (70, HEIGHT - 135))
    
    # Checkout button
    checkout_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 50)
    pygame.draw.rect(screen, GREEN, checkout_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE, checkout_btn, 3, border_radius=10)
    checkout_text = FONT.render("Checkout", True, WHITE)
    screen.blit(checkout_text, (checkout_btn.centerx - checkout_text.get_width()//2, checkout_btn.centery - checkout_text.get_height()//2))
    buttons.append((checkout_btn, "complete_level"))
    
    return buttons

def draw_level3_game(screen):
    draw_background(screen)
    draw_game_popup_overlay(screen)
    
    # Store header
    header_rect = pygame.Rect(50, 20, WIDTH - 100, 60)
    pygame.draw.rect(screen, PURPLE, header_rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, header_rect, 3, border_radius=15)
    
    title = TITLE_FONT.render("Needs vs Wants Quiz", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 35))
    
    if level3_game.current_item < len(level3_game.items):
        current_item, correct_type, emoji = level3_game.items[level3_game.current_item]
        
        # Quiz card
        quiz_rect = pygame.Rect(100, 120, WIDTH - 200, 200)
        pygame.draw.rect(screen, WHITE, quiz_rect, border_radius=15)
        pygame.draw.rect(screen, ORANGE, quiz_rect, 3, border_radius=15)
        
        question_text = FONT.render("Is this grocery item a NEED or WANT?", True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 150))
        
        # Item display
        item_rect = pygame.Rect(WIDTH//2 - 150, 200, 270, 80)
        pygame.draw.rect(screen, LIGHT_BLUE, item_rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, item_rect, 3, border_radius=10)
        
        item_name = FONT.render(current_item, True, BLACK)
        screen.blit(item_name, (WIDTH//2 - item_name.get_width()//2, 225))
        
        buttons = []
        
        # Need button (green)
        need_btn = pygame.Rect(WIDTH//2 - 180, 320, 150, 60)
        pygame.draw.rect(screen, GREEN, need_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, need_btn, 3, border_radius=10)
        need_text = FONT.render("NEED", True, WHITE)
        screen.blit(need_text, (need_btn.centerx - need_text.get_width()//2, need_btn.centery - need_text.get_height()//2))
        buttons.append((need_btn, "choice_need"))
        
        # Want button (yellow)
        want_btn = pygame.Rect(WIDTH//2 + 30, 320, 150, 60)
        pygame.draw.rect(screen, YELLOW, want_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, want_btn, 3, border_radius=10)
        want_text = FONT.render("WANT", True, BLACK)
        screen.blit(want_text, (want_btn.centerx - want_text.get_width()//2, want_btn.centery - want_text.get_height()//2))
        buttons.append((want_btn, "choice_want"))
        
        # Progress
        progress = FONT.render(f"Question {level3_game.current_item + 1}/{len(level3_game.items)}", True, BLACK)
        screen.blit(progress, (WIDTH//2 - progress.get_width()//2, 400))
        
        return buttons
    else:
        # Results screen
        results_rect = pygame.Rect(100, 150, WIDTH - 200, 200)
        pygame.draw.rect(screen, WHITE, results_rect, border_radius=15)
        pygame.draw.rect(screen, GREEN, results_rect, 3, border_radius=15)
        
        score = level3_game.get_score()
        score_text = TITLE_FONT.render(f"Quiz Score: {score:.0f}%", True, GREEN)
        result_text = FONT.render("Great job! You understand needs vs wants!", True, BLACK) if score >= 80 else \
                     FONT.render("Good effort! Keep learning!", True, BLACK)
        
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 240))
        
        complete_btn = pygame.Rect(WIDTH//2 - scale_value(120), scale_value(320), scale_value(240), scale_value(50))
        pygame.draw.rect(screen, GREEN, complete_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, complete_btn, 3, border_radius=10)
        complete_text = FONT.render("Complete Level", True, WHITE)
        screen.blit(complete_text, (complete_btn.centerx - complete_text.get_width()//2, complete_btn.centery - complete_text.get_height()//2))
        return [(complete_btn, "complete_level")]

def draw_main_menu(screen):
    draw_background(screen)
    
    # Store sign
    sign_rect = pygame.Rect(WIDTH//2 - 400, 50, 900, 150)
    pygame.draw.rect(screen, RED, sign_rect, border_radius=20)
    pygame.draw.rect(screen, YELLOW, sign_rect, 5, border_radius=20)
    
    title = TITLE_FONT.render("Grocery Budget Adventure", True, WHITE)
    subtitle = FONT.render("Learn Financial Literacy Through Shopping!", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 115))
    
    # Store info board
    info_rect = pygame.Rect(WIDTH//2 - 150, 200, 300, 80)
    pygame.draw.rect(screen, WHITE, info_rect, border_radius=15)
    pygame.draw.rect(screen, BLUE, info_rect, 3, border_radius=15)
    
    level_text = FONT.render(f"Current Level: {current_level}", True, BLUE)
    points_text = FONT.render(f"Total Points: {total_points}", True, GREEN)
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 195))
    screen.blit(points_text, (WIDTH//2 - points_text.get_width()//2, 230))
    
    # Grocery department buttons
    departments = [
        ("1. Budget Planning", "Plan your grocery budget", 1, ""),
        ("2. Smart Shopping", "Shop within your budget", 2, ""),
        ("3. Needs vs Wants", "Learn to prioritize", 3, ""),
        ("4. Emergency Fund", "Save for rainy days", 4, ""),
        ("5. Goal Setting", "Plan your financial future", 5, ""),
        ("6. Compound Interest", "Watch your money grow", 6, "")
    ]
    
    buttons = []
    for i, (main_text, sub_text, level, icon) in enumerate(departments):
        dept_rect = pygame.Rect(100, 300 + i * 70, WIDTH - 200, 60)
        
        # Color based on status
        if level in completed_levels:
            color = GREEN  # Completed - green
        elif level == current_level:
            color = YELLOW  # Current - yellow
        elif level < current_level:
            color = LIGHT_BLUE  # Available - light blue
        else:
            color = (200, 200, 200)  # Locked - gray
            
        pygame.draw.rect(screen, color, dept_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dept_rect, 2, border_radius=10)
        
        # Department content
        main = SMALL_FONT.render(main_text, True, BLACK)
        sub = SMALL_FONT.render(sub_text, True, BLACK)
        
        if icon:
            icon_text = FONT.render(icon, True, BLACK)
            screen.blit(icon_text, (dept_rect.x + 20, dept_rect.y + 15))
        screen.blit(main, (dept_rect.x + 60, dept_rect.y + 10))
        screen.blit(sub, (dept_rect.x + 60, dept_rect.y + 35))
        
        # Status indicator
        status = "COMPLETED" if level in completed_levels else \
                "CURRENT" if level == current_level else \
                "LOCKED" if level > current_level else "AVAILABLE"
        
        status_text = SMALL_FONT.render(status, True, BLACK)
        screen.blit(status_text, (dept_rect.x + dept_rect.width - 120, dept_rect.y + 20))
        
        if level <= current_level:
            buttons.append((dept_rect, f"level_{level}"))
    
    return buttons

def advance_level():
    global current_level, total_points
    completed_levels.add(current_level)
    current_level = min(6, current_level + 1)  # Don't go beyond level 6
    total_points += 100
    print(f"Advanced to level {current_level}")

# Initialize game components
level1_game = Level1Game()
level2_game = Level2Game()
level3_game = Level3Game()
level4_game = Level4Game()
level5_game = Level5Game()
level6_game = Level6Game()
popup_manager = PopupManager()

# EDUCATIONAL CONTENT FOR EACH LEVEL
level_popups = {
    1: [
        {
            "title": "Level 1: Grocery Budget Planning",
            "content": "Welcome to the grocery store! Every smart shopper starts with a budget. Key concepts:• Plan your spending before you shop • Allocate money to different departments",
            "choices": [{"text": "Next", "action": "next", "primary": True}]
        },
        {
            "title": "Smart Budget Allocation", 
            "content": "A good grocery budget might look like: Fresh Produce: 30%, Dairy & Eggs: 25% Meat & Fish: 20% Pantry Items: 15% Treats & Snacks: 10% This ensures you get essentials first!",
            "choices": [{"text": "Start Planning", "action": "start_game", "primary": True}]
        }
    ],
    2: [
        {
            "title": "Level 2: Smart Shopping",
            "content": "Time to hit the aisles! Smart shopping means making choices that fit your budget while getting what you need. Shopping tips: • Make a list and stick to it • Compare prices and sizes • Choose store brands • Watch for sales and deals",
            "choices": [{"text": "Next", "action": "next", "primary": True}]
        },
        {
            "title": "Smart Choices",
            "content": "Remember: • Essentials first (milk, bread, eggs) • Compare unit prices • Avoid impulse buys • Check your budget as you shop • Don't forget treats in moderation!",
            "choices": [{"text": "Start Shopping", "action": "start_game", "primary": True}]
        }
    ],
    3: [
        {
            "title": "Level 3: Needs vs Wants",
            "content": "The key to smart spending is knowing the difference between needs and wants! NEEDS: Essentials for health and nutrition • Fresh vegetables, basic proteins, grains WANTS: Nice-to-haves and treats • Premium brands, desserts, luxury items",
            "choices": [{"text": "Next", "action": "next", "primary": True}]
        },
        {
            "title": "Smart Prioritizing",
            "content": "Ask yourself: • Do I need this to eat healthy? • Can I find a cheaper alternative? • Will this help my budget or hurt it? • Is this a treat I can afford? Balance is key - some wants are okay in moderation!",
            "choices": [{"text": "Take the Quiz", "action": "start_game", "primary": True}]
        }
    ],
    4: [
        {
            "title": "Level 4: Emergency Fund",
            "content": "Just like keeping extra groceries for unexpected guests, an emergency fund prepares you for financial surprises!",
            "choices": [{"text": "Complete Level", "action": "complete_direct", "primary": True}]
        }
    ],
    5: [
        {
            "title": "Level 5: Goal Setting",
            "content": "Planning your financial future is like making a shopping list for your dreams!",
            "choices": [{"text": "Complete Level", "action": "complete_direct", "primary": True}]
        }
    ],
    6: [
        {
            "title": "Level 6: Compound Interest",
            "content": "Watch your savings grow like a well-stocked pantry - it gets bigger over time!",
            "choices": [{"text": "Complete Level", "action": "complete_direct", "primary": True}]
        }
    ]
}

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    buttons = []
    
    # Draw current game state
    if current_game_state == MAIN_MENU:
        buttons = draw_main_menu(screen)
    elif current_game_state == LEVEL_1_GAME:
        buttons = draw_level1_game(screen)
    elif current_game_state == LEVEL_2_GAME:
        buttons = draw_level2_game(screen)
    elif current_game_state == LEVEL_3_GAME:
        buttons = draw_level3_game(screen)
    else:
        draw_background(screen)
    
    # Draw active popup
    popup_buttons = []
    if popup_manager.active_popup:
        popup_buttons = popup_manager.draw_popup(screen)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # Handle window resize
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            # Refresh fonts with new scale factor
            refresh_fonts()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if popup_manager.active_popup and popup_buttons:
                for btn_rect, action in popup_buttons:
                    if btn_rect.collidepoint(event.pos):
                        if action == "next":
                            popup_manager.show_next_popup()
                        elif action == "start_game":
                            popup_manager.active_popup = None
                            # Start the appropriate game
                            if current_level == 1:
                                current_game_state = LEVEL_1_GAME
                                level1_game.reset()
                            elif current_level == 2:
                                current_game_state = LEVEL_2_GAME
                                level2_game.reset()
                            elif current_level == 3:
                                current_game_state = LEVEL_3_GAME
                                level3_game.reset()
                            elif current_level >= 4:
                                # Auto-complete levels 4-6
                                advance_level()
                                popup_manager.active_popup = {
                                    "title": "Level Complete!",
                                    "content": f"Level {current_level-1} completed! You earned 100 points! Ready for Level {current_level}",
                                    "choices": [{"text": "Continue", "action": "back_to_menu", "primary": True}]
                                }
                        elif action == "complete_direct":
                            advance_level()
                            popup_manager.active_popup = {
                                "title": "Level Complete!",
                                "content": f"Level {current_level-1} completed! You earned 100 points!",
                                "choices": [{"text": "Continue", "action": "back_to_menu", "primary": True}]
                            }
                        elif action == "back_to_menu":
                            popup_manager.active_popup = None
                            current_game_state = MAIN_MENU
                            
            else:
                for btn_rect, action in buttons:
                    if btn_rect.collidepoint(event.pos):
                        if current_game_state == MAIN_MENU and action.startswith("level_"):
                            level = int(action.split("_")[1])
                            if level_popups.get(level):
                                popup_manager.set_popups(level_popups[level])
                                popup_manager.show_next_popup()
                                
                        elif current_game_state == LEVEL_1_GAME:
                            if action.startswith("alloc_"):
                                parts = action.split("_")
                                cat_index = int(parts[1])
                                amount = int(parts[2])
                                category = list(level1_game.categories.keys())[cat_index]
                                level1_game.allocate_money(category, amount)
                            elif action == "complete_level":
                                score = level1_game.get_score()
                                advance_level()
                                popup_manager.active_popup = {
                                    "title": "Budget Plan Complete!",
                                    "content": f"Budget Planning Score: {score}/100 You earned 100 points! Moving to Smart Shopping!",
                                    "choices": [{"text": "Continue", "action": "back_to_menu", "primary": True}]
                                }
                                
                        elif current_game_state == LEVEL_2_GAME:
                            if action.startswith("add_"):
                                item_index = int(action.split("_")[1])
                                level2_game.add_to_cart(item_index)
                            elif action == "complete_level":
                                score = level2_game.get_score()
                                advance_level()
                                popup_manager.active_popup = {
                                    "title": "Shopping Complete!",
                                    "content": f"Shopping Score: {score:.0f}/100 You earned 100 points! Moving to Needs vs Wants!",
                                    "choices": [{"text": "Continue", "action": "back_to_menu", "primary": True}]
                                }
                                
                        elif current_game_state == LEVEL_3_GAME:
                            if action in ["choice_need", "choice_want"]:
                                choice = "need" if action == "choice_need" else "want"
                                level3_game.make_choice(choice)
                            elif action == "complete_level":
                                score = level3_game.get_score()
                                advance_level()
                                popup_manager.active_popup = {
                                    "title": "Quiz Complete!",
                                    "content": f"Needs vs Wants Score: {score:.0f}% You earned 100 points! Moving to next level!",
                                    "choices": [{"text": "Continue", "action": "back_to_menu", "primary": True}]
                                }
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()