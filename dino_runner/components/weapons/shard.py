import pygame
from dino_runner.components.weapons.projectile import Projectile

class Shard(Projectile):
    def __init__(self, x, y, direction, assets):
        # Atributos do estilhaço
        damage = 15
        speed = 6
        pierce = 1
        
        image = assets.get_image("SHARD")
        scaled_image = pygame.transform.scale(image, (20, 20))
        
        super().__init__(x, y, scaled_image, damage, speed, direction, pierce)
