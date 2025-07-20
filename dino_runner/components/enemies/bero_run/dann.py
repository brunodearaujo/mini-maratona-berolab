# Arquivo: dino_runner/components/enemies/bero_run/dann.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy

class Dann(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        image = self.assets.get_image("DANN")
        
        # --- REDIMENSIONAMENTO DA IMAGEM ---
        image = pygame.transform.scale(image, (90, 90))

        # --- BALANCEAMENTO: GUERREIRO (All-rounder) ---
        health = 120   # Vida padrão
        damage = 20    # Dano padrão
        speed = 1.8    # Velocidade padrão
        exp_value = 35
        
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        self.hitbox = self.rect.inflate(-25, -20)

