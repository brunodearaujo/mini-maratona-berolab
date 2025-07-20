# Arquivo: dino_runner/components/enemies/bero_run/teki.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy

class Teki(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        image = self.assets.get_image("TEKI")
        
        # --- REDIMENSIONAMENTO DA IMAGEM ---
        image = pygame.transform.scale(image, (100, 110))

        # --- BALANCEAMENTO: TANQUE ---
        health = 250  # Vida muito alta
        damage = 15   # Dano de colisão moderado
        speed = 1.0   # Muito lento
        exp_value = 50 # Recompensa alta pela demora
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        self.hitbox = self.rect.inflate(-30, -25)
        