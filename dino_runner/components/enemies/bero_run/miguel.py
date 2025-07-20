# Arquivo: dino_runner/components/enemies/bero_run/miguel.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy

class Miguel(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        health = 50
        damage = 10
        speed = 2.5
        exp_value = 20
        image = assets.get_image("MIGUEL")
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)