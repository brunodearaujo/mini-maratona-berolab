import pygame
from dino_runner.components.weapons.projectile import Projectile

class EnemyProjectile(Projectile):
    def __init__(self, x, y, direction, assets):
        # Atributos do projétil inimigo
        damage = 10 # Dano fixo por enquanto
        speed = 5   # Mais lento que o do jogador
        pierce = 1  # Não atravessa
        
        # Pega a imagem do AssetManager
        image = assets.get_image("ENEMY_BULLET")
        
        # Redimensiona para um tamanho adequado
        scaled_image = pygame.transform.scale(image, (15, 15))
        
        # Chama o construtor da classe pai (Projectile)
        super().__init__(x, y, scaled_image, damage, speed, direction, pierce)
