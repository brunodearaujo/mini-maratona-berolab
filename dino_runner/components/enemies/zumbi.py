# dino_runner/components/enemies/zumbi.py
import pygame
from dino_runner.components.enemies.enemy import Enemy
import os

# Define o caminho para a imagem do zumbi
ZUMBI_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "enemies", "zumbi.png")

class Zumbi(Enemy):
    def __init__(self, x, y, assets): # Recebe o AssetManager
        health = 100
        damage = 10
        speed = 2
        exp_value = 50
        # Pega a imagem do AssetManager e a passa para a classe pai
        image = assets.get_image("ZUMBI")
        super().__init__(x, y, image, health, damage, speed, exp_value)

    def update(self, player):
        """Implementa a IA do Zumbi: mover-se em direção ao jogador."""
        # Calcula a direção para o jogador
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        
        # Normaliza o vetor de direção para manter a velocidade constante
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            dx /= distance
            dy /= distance

        # Move o inimigo
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed