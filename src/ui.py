import pygame
from pygame_emojis import load_emoji
from settings import WHITE, GOLD, RED, PURPLE, BLUE, FONT_NAME, GRAY, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.font = pygame.font.SysFont(FONT_NAME, 16)
        self.small_font = pygame.font.SysFont(FONT_NAME, 14)
        
        # Left panel dimensions
        self.left_panel_width = 250
        self.left_panel_height = 400
        self.left_panel_x = 10
        self.left_panel_y = 10
        
        # Colors
        self.bg_color = (40, 40, 50)
        self.border_color = (100, 100, 120)
        self.accent_color = (80, 120, 200)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)
        
        # Button dimensions
        self.button_width = 220
        self.button_height = 40
        self.button_spacing = 10
        self.button_list = []
        
        # Right panel dimensions
        self.right_panel_width = 250
        self.right_panel_height = 500
        self.right_panel_x = self.screen_width - self.right_panel_width - 10
        self.right_panel_y = 10
        
        # Menu state
        self.active_menu = None
        self.menu_options = []
        self.menu_rects = []
        
        # Popup state
        self.popup_title = ""
        self.popup_description = ""
        self.popup_buttons = []
        self.showing_popup = False
        self.popup_button_rects = []
        
        # Load emojis
        EMOJI_SIZE = (24, 24)
        self.emojis = {
            "gold": load_emoji("💰", EMOJI_SIZE),
            "debt": load_emoji("💸", EMOJI_SIZE),
            "witch": load_emoji("🧙", EMOJI_SIZE),
            "banker": load_emoji("🏦", EMOJI_SIZE),
            "poultry": load_emoji("🐔", EMOJI_SIZE),
            "check": load_emoji("✅", EMOJI_SIZE),
            "stock": load_emoji("🛒", EMOJI_SIZE),
        }

    def draw_left_panel(self, player, characters, coffee_shop):
        """Draw the left panel with stats"""
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.left_panel_x, self.left_panel_y, self.left_panel_width, self.left_panel_height), 
                        border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.left_panel_x, self.left_panel_y, self.left_panel_width, self.left_panel_height), 
                        width=2, border_radius=12)

        y_offset = self.left_panel_y + 20
        title_text = self.title_font.render("Café Finances", True, WHITE)
        self.screen.blit(title_text, (self.left_panel_x + 15, y_offset))
        y_offset += 40

        pygame.draw.line(self.screen, self.border_color, 
                        (self.left_panel_x + 15, y_offset), 
                        (self.left_panel_x + self.left_panel_width - 15, y_offset), 1)
        y_offset += 20

        # Gold
        self.screen.blit(self.emojis["gold"], (self.left_panel_x + 15, y_offset))
        money_text = self.font.render(f"Gold: {int(player.money)}", True, GOLD)
        self.screen.blit(money_text, (self.left_panel_x + 50, y_offset))
        y_offset += 30

        # Stock
        self.screen.blit(self.emojis["stock"], (self.left_panel_x + 15, y_offset))
        stock_text = self.font.render(f"Stock: {int(player.stock)}", True, (255, 100, 100))  # red-ish
        self.screen.blit(stock_text, (self.left_panel_x + 50, y_offset))
        y_offset += 30

        # Total Debt
        total_debt = sum(player.debts.values()) if player.debts else 0
        debt_color = RED if total_debt > 0 else (100, 200, 100)
        self.screen.blit(self.emojis["debt"], (self.left_panel_x + 15, y_offset))
        debt_text = self.font.render(f"Debt: {int(total_debt)}", True, debt_color)
        self.screen.blit(debt_text, (self.left_panel_x + 50, y_offset))
        y_offset += 30

        # Individual debts
        if player.debts:
            debt_title = self.small_font.render("Debts:", True, WHITE)
            self.screen.blit(debt_title, (self.left_panel_x + 15, y_offset))
            y_offset += 20
            for lender, amount in player.debts.items():
                if amount > 0:
                    prefix = lender.split()[0]
                    display_name = prefix[:10]
                    text_surface = self.small_font.render(f"{display_name}: {int(amount)}", True, GOLD)
                    self.screen.blit(text_surface, (self.left_panel_x + 15, y_offset))
                    y_offset += 20
        
    def get_npc_icon(self, name):
        if "Farmer" in name:
            return "🌾"
        elif "Poultry" in name:
            return "🐔"
        elif "Witch" in name:
            return "🧙"
        elif "Banker" in name:
            return "🏦"
        else:
            return "👤"

    def draw_button(self, text, x, y, width, height, target_name):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.button_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, rect, width=1, border_radius=8)
        text_surface = self.small_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(text_surface, text_rect)
        return rect, target_name

    def draw_minimap(self, player, npcs=None, coffee_shop=None):
        minimap_size = 120
        minimap_x = self.screen_width - minimap_size - 10
        minimap_y = self.screen_height - minimap_size - 10

        pygame.draw.rect(self.screen, self.bg_color, (minimap_x, minimap_y, minimap_size, minimap_size), border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, (minimap_x, minimap_y, minimap_size, minimap_size), width=2, border_radius=8)

        minimap_title = self.small_font.render("Map", True, WHITE)
        self.screen.blit(minimap_title, (minimap_x + 5, minimap_y + 5))

        scale_x = minimap_size / self.screen_width
        scale_y = minimap_size / self.screen_height

        if coffee_shop and hasattr(coffee_shop, 'rect'):
            shop_x = minimap_x + int(coffee_shop.rect.centerx * scale_x)
            shop_y = minimap_y + int(coffee_shop.rect.centery * scale_y)
            pygame.draw.circle(self.screen, (139, 69, 19), (shop_x, shop_y), 4)

        if npcs:
            for npc in npcs:
                if hasattr(npc, 'rect'):
                    npc_x = minimap_x + int(npc.rect.centerx * scale_x)
                    npc_y = minimap_y + int(npc.rect.centery * scale_y)
                    pygame.draw.circle(self.screen, WHITE, (npc_x, npc_y), 2)

        if player and hasattr(player, 'rect'):
            player_x = minimap_x + int(player.rect.centerx * scale_x)
            player_y = minimap_y + int(player.rect.centery * scale_y)
            pygame.draw.circle(self.screen, WHITE, (player_x, player_y), 3)

    def draw_status_bar(self, player):
        bar_height = 30
        bar_y = self.screen_height - bar_height
        pygame.draw.rect(self.screen, self.bg_color, (0, bar_y, self.screen_width, bar_height))
        pygame.draw.line(self.screen, self.border_color, (0, bar_y), (self.screen_width, bar_y), 2)
        status_text = f"Pos: ({player.rect.centerx}, {player.rect.centery}) | Move: WASD/Arrows | Click to interact"
        text = self.small_font.render(status_text, True, WHITE)
        self.screen.blit(text, (10, bar_y + 8))

    def check_proximity(self, player, npcs, coffee_shop):
        proximity_distance = 150
        nearby_entities = []

        if coffee_shop and hasattr(coffee_shop, 'rect'):
            distance = ((coffee_shop.rect.centerx - player.rect.centerx) ** 2 +
                        (coffee_shop.rect.centery - player.rect.centery) ** 2) ** 0.5
            if distance <= proximity_distance:
                nearby_entities.append(("Coffee Shop", coffee_shop, distance))

        if npcs:
            for npc in npcs:
                if hasattr(npc, 'rect'):
                    distance = ((npc.rect.centerx - player.rect.centerx) ** 2 +
                                (npc.rect.centery - player.rect.centery) ** 2) ** 0.5
                    if distance <= proximity_distance:
                        nearby_entities.append((npc.name, npc, distance))

        return nearby_entities

    def draw_right_panel(self, nearby_entities):
        if not nearby_entities:
            return
        self.button_list.clear()
        pygame.draw.rect(self.screen, self.bg_color, 
                         (self.right_panel_x, self.right_panel_y, self.right_panel_width, self.right_panel_height), border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, 
                         (self.right_panel_x, self.right_panel_y, self.right_panel_width, self.right_panel_height), width=2, border_radius=12)

        y_offset = self.right_panel_y + 20
        title_text = self.title_font.render("Nearby", True, WHITE)
        self.screen.blit(title_text, (self.right_panel_x + 15, y_offset))
        y_offset += 40

        for entity_name, entity, distance in nearby_entities:
            entity_text = self.font.render(f"{entity_name}", True, self.accent_color)
            self.screen.blit(entity_text, (self.right_panel_x + 15, y_offset))
            y_offset += 25
            distance_text = self.small_font.render(f"Dist: {int(distance)}", True, GRAY)
            self.screen.blit(distance_text, (self.right_panel_x + 15, y_offset))
            y_offset += 20

            if entity_name == "Coffee Shop":
                rect, name = self.draw_button("Visit", self.right_panel_x + 15, y_offset,
                                              self.right_panel_width - 30, self.button_height, "Coffee Shop")
            else:
                rect, name = self.draw_button(f"Talk", self.right_panel_x + 15, y_offset,
                                              self.right_panel_width - 30, self.button_height, entity_name)

            self.button_list.append((rect, name))
            y_offset += self.button_height + 20

    def coffee_shop_menu(self):
        self.active_menu = "Coffee Shop"
        self.menu_options = ["Generate a Sale", "Check Account", "Back"]

    def witch_menu(self):
        self.active_menu = "Witch"
        self.menu_options = ["Borrow 50 gold", "Borrow 100 gold", "Repay Debt", "Back"]

    def banker_menu(self):
        self.active_menu = "Banker"
        self.menu_options = ["Request Loan", "Repay Debt", "Back"]

    def poultry_menu(self):
        self.active_menu = "Poultry"
        self.menu_options = ["Borrow 25 stock", "Borrow 15 stock", "Repay Debt", "Buy 10 Stock", "Back"]

    def farmer_menu(self):
        self.active_menu = "Farmer"
        self.menu_options = ["Borrow 10 stock", "Borrow 5 stock", "Repay Debt","Buy 5 Stock" ,"Back"]
    def handle_click(self, mouse_pos, player):
        # Handle popup button clicks first
        if self.showing_popup:
            for rect, button_text in self.popup_button_rects:
                if rect.collidepoint(mouse_pos):
                    # Special handling for different button types
                    if button_text == "View Suggestions":
                        import functions
                        functions.coffee_shop_action(self, player, "View Suggestions")
                        return
                    elif button_text == "Accept Loan":
                        import functions
                        functions.banker_action(self, player, "Accept Loan")
                        return
                    else:
                        self.showing_popup = False
                        return
            return

        # If menu is open, handle its clicks
        if self.active_menu:
            for rect, option in self.menu_rects:
                if rect.collidepoint(mouse_pos):
                    if option == "Back":
                        self.active_menu = None
                        self.menu_options = []
                        self.menu_rects = []
                    else:
                        import functions
                        if self.active_menu == "Coffee Shop":
                            functions.coffee_shop_action(self, player, option)
                        elif self.active_menu == "Witch":
                            functions.witch_action(self, player, option)
                        elif self.active_menu == "Banker":
                            functions.banker_action(self, player, option)
                        elif self.active_menu == "Poultry":
                            functions.poultry_action(self, player, option)
                        elif self.active_menu == "Farmer":
                            functions.farmer_action(self, player, option)
                    return

        # Handle right panel button clicks
        for rect, entity_name in self.button_list:
            if rect.collidepoint(mouse_pos):
                if entity_name == "Coffee Shop":
                    self.coffee_shop_menu()
                elif "Witch" in entity_name:
                    self.witch_menu()
                elif "Banker" in entity_name:
                    self.banker_menu()
                elif "Poultry" in entity_name:
                    self.poultry_menu()
                elif "Farmer" in entity_name:
                    self.farmer_menu()

    def draw_active_menu(self):
        if not self.active_menu:
            return
        
        panel_width = 300
        panel_height = 280
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(self.screen, self.bg_color, (panel_x, panel_y, panel_width, panel_height), border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, (panel_x, panel_y, panel_width, panel_height), width=3, border_radius=12)

        # Title
        title_surface = self.title_font.render(f"{self.active_menu}", True, WHITE)
        self.screen.blit(title_surface, (panel_x + 15, panel_y + 15))

        # Draw menu buttons
        y_offset = panel_y + 50
        self.menu_rects = []

        for option in self.menu_options:
            rect = pygame.Rect(panel_x + 20, y_offset, panel_width - 40, 35)
            pygame.draw.rect(self.screen, self.button_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.border_color, rect, width=1, border_radius=8)
            text_surface = self.small_font.render(option, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            self.menu_rects.append((rect, option))
            y_offset += 45

    def draw_popup(self):
        """Draw the popup with description and buttons"""
        if not self.showing_popup:
            return

        panel_width = 500
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Panel background
        pygame.draw.rect(self.screen, self.bg_color, (panel_x, panel_y, panel_width, panel_height), border_radius=12)
        pygame.draw.rect(self.screen, self.border_color, (panel_x, panel_y, panel_width, panel_height), width=3, border_radius=12)

        # Title
        title_surface = self.title_font.render(self.popup_title, True, WHITE)
        self.screen.blit(title_surface, (panel_x + 20, panel_y + 15))

        # Description (wrapped text)
        description_y = panel_y + 60
        margin = 20
        max_width = panel_width - (2 * margin)
        
        words = self.popup_description.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_width = self.font.size(test_line)[0]
            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        for line in lines:
            text_surface = self.font.render(line, True, WHITE)
            self.screen.blit(text_surface, (panel_x + margin, description_y))
            description_y += 25

        # Buttons
        button_y = panel_y + panel_height - 80
        self.popup_button_rects = []
        button_width = 120
        button_height = 40
        button_spacing = 15
        total_width = (button_width * len(self.popup_buttons)) + (button_spacing * (len(self.popup_buttons) - 1))
        start_x = panel_x + (panel_width - total_width) // 2

        for i, (button_text, action) in enumerate(self.popup_buttons):
            x = start_x + (i * (button_width + button_spacing))
            rect = pygame.Rect(x, button_y, button_width, button_height)
            pygame.draw.rect(self.screen, self.button_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.border_color, rect, width=2, border_radius=8)
            text_surface = self.small_font.render(button_text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            self.popup_button_rects.append((rect, button_text))

    def draw_all(self, player, characters, coffee_shop=None, npcs=None):
        self.draw_left_panel(player, characters, coffee_shop)
        self.draw_minimap(player, npcs, coffee_shop)
        self.draw_status_bar(player)
        nearby_entities = self.check_proximity(player, npcs, coffee_shop)
        if nearby_entities:
            self.draw_right_panel(nearby_entities)
        self.draw_active_menu()
        self.draw_popup()

    