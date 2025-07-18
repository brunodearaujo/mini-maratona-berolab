# dino_runner/components/obstacles/obstacle.py
import pygame
from dino_runner.utils.constants import SCREEN_WIDTH



class Obstacle:
    def __init__(self, assets, image_list, type):
        self.assets = assets
        self.image = image_list
        self.type = type
        self.rect = self.image[0].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self, game_speed, obstacle_list):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacle_list.pop()

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)