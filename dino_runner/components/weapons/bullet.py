from dino_runner.components.weapons.projectile import Projectile
import os
import pygame
import math

BULLET_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "weapons", "bullet.png")

class Bullet(Projectile):
    # BALANCEAMENTO: Dano base da bola de fogo reduzido
    BASE_DAMAGE = 15
    BASE_PIERCE = 1
    BASE_SPEED = 15.0
    BASE_BOUNCES = 0

    # CORREÇÃO: O __init__ agora aceita o parâmetro 'is_frozen'.
    def __init__(self, x, y, direction, assets, is_frozen=False):
        damage = Bullet.BASE_DAMAGE
        speed = Bullet.BASE_SPEED
        pierce = Bullet.BASE_PIERCE
        
        self.is_frozen = is_frozen
        self.bounces_left = Bullet.BASE_BOUNCES
        
        image = assets.get_image("BULLET")
        super().__init__(x, y, image, damage, speed, direction, pierce)
        
        base_image = pygame.transform.scale(self.image, (30, 30))
        base_image = pygame.transform.rotate(base_image, 90)

        # Se o tiro for congelante, aplica um filtro azul
        if self.is_frozen:
            blue_tint = base_image.copy()
            blue_tint.fill((50, 50, 200), special_flags=pygame.BLEND_RGB_ADD)
            base_image = blue_tint

        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(base_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-20, -20)

    
    

    def update(self):
       super().update()
       # Garante que a hitbox se move juntamente com a imagem
       self.hitbox.center = self.rect.center
