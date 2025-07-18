# dino_runner/components/obstacles/bird.py
import pygame
from dino_runner.components.obstacles.obstacle import Obstacle


class Bird(Obstacle):
    def __init__(self, assets):
        self.assets = assets
        bird_images = self.assets.get_image("BIRD")
        # A chamada super() agora inclui 'assets'
        super().__init__(assets, bird_images, 0) # Usamos 0 como tipo para a primeira imagem
        self.rect.y = 250
        self.step_index = 0

    def draw(self, screen):
        screen.blit(self.image[self.step_index // 5], self.rect)
        self.step_index += 1

        if self.step_index >= 10:
            self.step_index = 0