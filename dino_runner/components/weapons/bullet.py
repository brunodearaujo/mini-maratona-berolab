from dino_runner.components.weapons.projectile import Projectile
import os
import pygame
import math

BULLET_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "weapons", "bullet.png")

class Bullet(Projectile):
    # Valores base que serão modificados pelos power-ups
    BASE_DAMAGE = 25
    BASE_PIERCE = 1

    def __init__(self, x, y, direction, assets):
        damage = Bullet.BASE_DAMAGE
        speed = 15
        pierce = Bullet.BASE_PIERCE
        
        image = assets.get_image("BULLET")
        
        super().__init__(x, y, image, damage, speed, direction, pierce)
        
        # --- CORREÇÃO DE TAMANHO E ROTAÇÃO ---

        # 1. Redimensiona a imagem para um tamanho mais adequado.
        # <<< ALTERE OS VALORES AQUI para ajustar o tamanho da bala.
        # O primeiro valor é a LARGURA e o segundo é a ALTURA em pixels.
        original_image = pygame.transform.scale(self.image, (48, 24)) 

        # 2. Calcula o ângulo da direção em graus.
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))

        # 3. Rotaciona a imagem original e a define como a imagem final do projétil.
        self.image = pygame.transform.rotate(original_image, angle)
        
        # Atualiza o retângulo com a nova imagem rotacionada
        self.rect = self.image.get_rect(center=(x, y))