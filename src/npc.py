import pygame
import random

class NPC(pygame.sprite.Sprite):
    def __init__(self, name, image_path, pos=(0,0), size=(150, 150)):
        super().__init__()
        self.name = name
        
        # Load and scale image
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

    def random_move(self):
        # Simple random movement example
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        self.pos.x += dx
        self.pos.y += dy
        self.rect.center = self.pos
