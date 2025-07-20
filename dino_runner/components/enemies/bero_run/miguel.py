# Arquivo: dino_runner/components/enemies/bero_run/miguel.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy

class Miguel(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        image = self.assets.get_image("MIGUEL")
        
        # --- REDIMENSIONAMENTO DA IMAGEM ---
        image = pygame.transform.scale(image, (85, 95))

        # --- BALANCEAMENTO: ASSASSINO ---
        health = 50    # Vida muito baixa (frágil)
        damage = 25    # Dano de colisão alto
        speed = 6    # Extremamente rápido
        exp_value = 30 # Recompensa moderada
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        self.hitbox = self.rect.inflate(-20, -15)

