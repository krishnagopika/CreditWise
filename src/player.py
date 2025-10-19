# player.py
import pygame
import os
import time  # NEW: For energy regen timing

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Load footsteps image
        try:
            image_path = os.path.join(os.path.dirname(__file__), 'assets', 'footsteps.png')
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (100, 100))
        except pygame.error:
            # Fallback: create a simple player representation
            self.image = pygame.Surface((40, 40))
            self.image.fill((180, 150, 255))  # Purple color for player
        
        self.rect = self.image.get_rect(center=pos)

        self.money = 200
        self.debts = {
            "Wizard of Woe": 50,
            "Banker Bard": 20,
            "Poultry Guy Pip": 10
        }

        # ===== NEW ATTRIBUTES =====
        self.stock = 100             # Player energy (0-100)
        self.last_stock_update = time.time()  # For regen calculation
        self.actions_log = []         # Track all actions for analytics

    def move(self, keys_pressed):
        speed = 4
        
        # Arrow keys
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.rect.x -= speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.rect.x += speed
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.rect.y -= speed
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.rect.y += speed
            
        # Keep player within world bounds
        from settings import WORLD_WIDTH, WORLD_HEIGHT
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, WORLD_HEIGHT - self.rect.height))

    # ===== NEW METHODS =====
    def update_energy(self):
        """Regenerate energy slowly over time (1 energy per 5 seconds)"""
        current_time = time.time()
        delta = current_time - self.last_energy_update
        if delta >= 5:  # every 5 seconds
            self.energy = min(100, self.energy + 1)
            self.last_energy_update = current_time

    def spend_stock(self, amount, action_name):
        """Reduce energy and log the action"""
        self.stock = max(0, self.stock - amount)
        self.actions_log.append({
            "action": action_name,
            "energy_change": -amount,
            "money_change": 0,
            "timestamp": time.time()
        })

    def gain_energy(self, amount, action_name):
        """Increase energy (e.g., coffee) and log the action"""
        self.energy = min(100, self.energy + amount)
        self.actions_log.append({
            "action": action_name,
            "energy_change": amount,
            "money_change": 0,
            "timestamp": time.time()
        })

    def update_debts(self):
        """Apply interest to all current debts and return total debt"""
        interest_rates = {
            "Banker Bard": 0.02,
            "Poultry Guy": 0.10,
            "Farmer Finn": 0.08,
            "Wizard of Woe": 0.25
        }
        
        total_debt = 0
        for lender, amount in self.debts.items():
            rate = interest_rates.get(lender, 0)
            self.debts[lender] = round(amount * (1 + rate), 2)
            total_debt += self.debts[lender]
        
        return total_debt
