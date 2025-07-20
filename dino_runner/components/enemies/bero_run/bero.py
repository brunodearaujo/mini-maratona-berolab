# Arquivo: dino_runner/components/enemies/bero_run/bero.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy

class Bero(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        image = self.assets.get_image("BERO")
        
        # --- REDIMENSIONAMENTO DA IMAGEM ---
        # Altere (largura, altura) para o tamanho que desejar.
        image = pygame.transform.scale(image, (80, 100))
        
        # --- BALANCEAMENTO: MINIBOSS (Elite) ---
        health = 180   # Vida alta
        damage = 25    # Dano alto
        speed = 2.0    # Rápido
        exp_value = 60 # Recompensa muito alta
        
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        self.hitbox = self.rect.inflate(-20, -15)
        