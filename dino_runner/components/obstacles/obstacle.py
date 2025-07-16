# dino_runner/components/obstacles/obstacle.py
import pygame
from dino_runner.utils.constants import SCREEN_WIDTH

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        # Pega o retângulo da primeira imagem da lista (se for uma animação)
        self.rect = self.image[self.type].get_rect()
        # Define a posição inicial do obstáculo fora da tela, à direita
        self.rect.x = SCREEN_WIDTH

    def update(self, game_speed, obstacle_list):
        # Move o obstáculo para a esquerda com base na velocidade do jogo
        self.rect.x -= game_speed
        # Se o obstáculo saiu completamente da tela, remove-o da lista
        if self.rect.x < -self.rect.width:
            obstacle_list.pop()

    def draw(self, screen):
        # Desenha o obstáculo na tela
        screen.blit(self.image[self.type], self.rect)