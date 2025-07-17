from dino_runner.components.weapons.projectile import Projectile
import os
import pygame
import math

BULLET_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "weapons", "bullet.png")

class Bullet(Projectile):
    # Valores base que serão modificados pelos power-ups
    BASE_DAMAGE = 25
    BASE_PIERCE = 1

    def __init__(self, x, y, direction):
        # Usa os valores base da classe
        damage = Bullet.BASE_DAMAGE
        speed = 15
        pierce = Bullet.BASE_PIERCE
        
        super().__init__(x, y, BULLET_IMAGE_PATH, damage, speed, direction, pierce)

        # --- CORREÇÃO DE TAMANHO E ROTAÇÃO ---
        original_image = pygame.transform.scale(self.image, (20, 10))
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))