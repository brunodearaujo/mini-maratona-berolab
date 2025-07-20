import pygame
from dino_runner.components.enemies.enemy import Enemy
from dino_runner.components.weapons.enemy_projectile import EnemyProjectile
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Bird2(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        # ADICIONE ESTA LINHA:
        self.assets = assets

        health = 60
        damage = 10
        speed = 1.8
        exp_value = 25
        image = self.assets.get_image("BIRD2")
        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)

        # Atributos de combate à distância
        self.attack_cooldown = 2500 # Atira a cada 2.5 segundos
        self.last_shot_time = pygame.time.get_ticks()
        self.preferred_distance = 350

    def update(self, player, enemy_projectiles):
        """IA do Bird2: mantém distância, atira e respeita os limites da tela."""
        # --- Lógica de movimento e tiro (código que você já tem) ---
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5

        if distance > 0:
            if distance < self.preferred_distance:
                self.rect.x -= (dx / distance) * self.speed
                self.rect.y -= (dy / distance) * self.speed
            else:
                self.rect.x += (dx / distance) * self.speed
                self.rect.y += (dy / distance) * self.speed
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.attack_cooldown:
            self.last_shot_time = current_time
            if distance > 0:
                direction = pygame.math.Vector2(dx, dy).normalize()
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, direction, self.assets)
                enemy_projectiles.append(projectile)

        # --- ADICIONE ESTE BLOCO DE CÓDIGO NO FINAL DO MÉTODO ---
        # Garante que o inimigo não saia do mapa
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
