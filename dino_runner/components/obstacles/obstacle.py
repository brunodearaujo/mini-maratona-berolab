# dino_runner/components/obstacles/obstacle.py
import pygame
from dino_runner.utils.constants import SCREEN_WIDTH

class Obstacle:
    def __init__(self, assets, image_list, type):
        self.assets = assets
        self.image = image_list
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.hitbox = self.rect.copy()
        self.rect.x = SCREEN_WIDTH

    def update(self, game_speed, obstacle_list):
        self.rect.x -= game_speed
        # CORREÇÃO: Garante que a hitbox se move perfeitamente com o obstáculo.
        # Isto resolve o problema de desalinhamento vertical.
        self.hitbox.center = self.rect.center
        
        if self.rect.x < -self.rect.width:
            obstacle_list.pop()

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)