# Arquivo: dino_runner/components/enemies/bero_run/pam.py (Caminho do Bero)

import pygame
from dino_runner.components.enemies.enemy import Enemy
from dino_runner.components.weapons.enemy_projectile import EnemyProjectile
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Pam(Enemy):
    def __init__(self, x, y, assets, is_boss=False):
        self.assets = assets
        image = self.assets.get_image("PAM")
        
        # --- REDIMENSIONAMENTO DA IMAGEM ---
        image = pygame.transform.scale(image, (70, 90))

        # --- BALANCEAMENTO: SNIPER ---
        health = 60    # Vida baixa
        damage = 5     # Dano de colisão baixo (o perigo são os tiros)
        speed = 1.2    # Lenta, posiciona-se para atirar
        exp_value = 30

        super().__init__(x, y, image, health, damage, speed, exp_value, is_boss)
        self.hitbox = self.rect.inflate(-15, -15)
        
        self.attack_cooldown = 3000 # Cooldown longo entre os tiros
        self.last_shot_time = pygame.time.get_ticks()
        self.preferred_distance = 450 # Tenta ficar bem longe

    def update(self, player, enemy_projectiles):
        """IA da Pam: mantém distância, atira e respeita os limites da tela."""
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

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        
        # CORREÇÃO: Garante que a hitbox se move juntamente com a imagem.
        self.hitbox.center = self.rect.center

