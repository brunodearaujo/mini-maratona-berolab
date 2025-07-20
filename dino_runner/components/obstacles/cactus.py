# dino_runner/components/obstacles/cactus.py
import pygame
import random
from dino_runner.components.obstacles.obstacle import Obstacle


class Cactus(Obstacle):
    def __init__(self, assets):
        large_cactus_images = assets.get_image("LARGE_CACTUS")
        small_cactus_images = assets.get_image("SMALL_CACTUS")
        
        if random.randint(0, 1) == 0:
            image_list = small_cactus_images
        else:
            image_list = large_cactus_images
        
        # A chamada super() agora passa 'assets'
        super().__init__(assets, image_list, random.randint(0, 2))
        
        if image_list == small_cactus_images:
            self.rect.y = 325
            self.hitbox = self.rect.inflate(-10, -10)
        else:
            self.rect.y = 300
            self.hitbox = self.rect.inflate(-40, -20) 
        
        self.hitbox.y = self.rect.y