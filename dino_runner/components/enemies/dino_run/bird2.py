import pygame
from dino_runner.components.enemies.enemy import Enemy
from dino_runner.components.weapons.enemy_projectile import EnemyProjectile
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Bird2(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        # CORREÇÃO: Pega a LISTA de imagens de animação do AssetManager
        image = self.assets.get_image("BIRD") # Assumindo que "BIRD" é a sua lista de frames
        health, damage, speed, exp_value = 60, 10, 1.8, 25
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        
        self.hitbox = self.rect.inflate(-15, -15)
        
        self.attack_cooldown = 2500
        self.last_shot_time = pygame.time.get_ticks()
        self.preferred_distance = 350

    def update(self, player, enemy_projectiles):
        # A lógica de animação agora está na classe base Enemy, então
        # chamamos o super().update() primeiro.
        super().update(player, enemy_projectiles)

        # Lógica de IA específica do Bird1 (manter distância e atirar)
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5

        if distance > 0:
            if distance < self.preferred_distance:
                self.rect.x -= (dx / distance) * self.speed
            else:
                self.rect.x += (dx / distance) * self.speed
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.attack_cooldown:
            self.last_shot_time = current_time
            if distance > 0:
                direction = pygame.math.Vector2(dx, dy).normalize()
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, direction, self.assets)
                enemy_projectiles.append(projectile)

        # Limites de tela
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        
        self.hitbox.center = self.rect.center