# Arquivo: dino_runner/components/enemies/dino_run/cacto1.py (Caminho do Dino)
import pygame
from dino_runner.components.enemies.enemy import Enemy

class Cacto1(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        health = 50
        damage = 10
        speed = 2.5
        exp_value = 20
        image = assets.get_image("CACTO1")
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)

        # AJUSTE DA HITBOX: Agora você pode encolher a hitbox para ser mais justa.
        # Esta linha sobrescreve a hitbox padrão criada na classe Enemy.
        self.hitbox = self.rect.inflate(-25, -15)


    
