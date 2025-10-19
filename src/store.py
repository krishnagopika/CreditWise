# store.py
import pygame
import random
import os

class CoffeeShop(pygame.sprite.Sprite):
    def __init__(self, pos=(500, 300)):
        super().__init__()
        
        # Load coffee shop image
        try:
            image_path = os.path.join(os.path.dirname(__file__), 'assets', 'coffee-shop.png')
            self.image = pygame.image.load(image_path)
            # Scale the image to appropriate size
            self.image = pygame.transform.scale(self.image, (200, 200))
        except pygame.error:
            # Fallback: create a simple coffee shop representation
            self.image = pygame.Surface((100, 100))
            self.image.fill((139, 69, 19))  # Brown color for coffee shop
            # Draw a simple coffee cup icon
            pygame.draw.rect(self.image, (255, 255, 255), (50, 30, 20, 30))
            pygame.draw.ellipse(self.image, (255, 255, 255), (45, 25, 30, 10))
        
        self.rect = self.image.get_rect(center=pos)
        self.name = "☕ Cosmic Café"
        
        # Coffee shop inventory
        self.inventory = {
            "Espresso": {"price": 8, "cost": 3, "description": "Strong coffee shot"},
            "Latte": {"price": 12, "cost": 5, "description": "Coffee with steamed milk"},
            "Cappuccino": {"price": 10, "cost": 4, "description": "Espresso with foam"},
            "Mocha": {"price": 15, "cost": 6, "description": "Coffee with chocolate"},
            "Americano": {"price": 6, "cost": 2, "description": "Espresso with hot water"},
            "Frappuccino": {"price": 18, "cost": 8, "description": "Blended iced coffee"}
        }
        
        # Business metrics
        self.daily_sales = 0
        self.customer_satisfaction = 100
        self.reputation = 50
        
        # Initialize player inventory if it doesn't exist
        self.player_inventory = {}

    def sell_item(self, player, item):
        """Sell coffee to customer"""
        if item in self.inventory:
            price = self.inventory[item]["price"]
            player.money += price
            self.daily_sales += price
            self.customer_satisfaction = min(100, self.customer_satisfaction + 2)
            self.reputation = min(100, self.reputation + 1)
            return f"Sold {item} for {price} gold!"
        return "Item not available"

    def buy_ingredients(self, player, item):
        """Buy ingredients to make coffee"""
        if item in self.inventory:
            cost = self.inventory[item]["cost"]
            if player.money >= cost:
                player.money -= cost
                # Add to player inventory
                if item not in self.player_inventory:
                    self.player_inventory[item] = 0
                self.player_inventory[item] += 1
                return f"Bought ingredients for {item}!"
            else:
                return "Not enough money!"
        return "Item not available"

    def get_menu(self):
        """Get the coffee shop menu"""
        menu_text = f"=== {self.name} Menu ===\n"
        for item, details in self.inventory.items():
            menu_text += f"{item}: {details['price']} gold (Cost: {details['cost']})\n"
            menu_text += f"  {details['description']}\n"
        return menu_text

    def get_stats(self):
        """Get coffee shop statistics"""
        return {
            "daily_sales": self.daily_sales,
            "satisfaction": self.customer_satisfaction,
            "reputation": self.reputation,
            "inventory_count": len(self.player_inventory)
        }

    def update(self):
        """Update coffee shop state"""
        # Gradually decrease satisfaction over time
        self.customer_satisfaction = max(0, self.customer_satisfaction - 0.1)
        
        # Random events
        if random.random() < 0.01:  # 1% chance per frame
            self.customer_satisfaction += random.randint(1, 5)
            self.reputation += random.randint(0, 2)

# Legacy Store class for compatibility
class Store(CoffeeShop):
    def __init__(self):
        super().__init__()
        # Keep old inventory for backward compatibility
        self.inventory.update({
            "Healing Potion": {"price": 10, "cost": 5, "description": "Restores health"},
            "Mana Potion": {"price": 15, "cost": 8, "description": "Restores magic"},
            "Elixir": {"price": 25, "cost": 12, "description": "Powerful healing"}
        })
