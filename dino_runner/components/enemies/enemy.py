# dino_runner/components/enemies/enemy.py
import pygame

class Enemy:
    def __init__(self, x, y, image, health, damage, speed, exp_value):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.exp_value = exp_value

    def update(self, player):
        pass

    def draw(self, screen):
        # Desenha o inimigo na tela
        screen.blit(self.image, self.rect)
        # --- DESENHA A BARRA DE VIDA DO INIMIGO ---
        self.draw_health_bar(screen)

    def take_damage(self, amount):
        # ... (código existente)
        self.health -= amount
        return self.health <= 0
        
    def draw_health_bar(self, screen):
        """Desenha uma barra de vida abaixo do inimigo."""
        if self.health < self.max_health: # Só desenha se o inimigo já tomou dano
            health_ratio = self.health / self.max_health
            # Posição e tamanho da barra
            bar_width = self.rect.width * 0.8
            bar_height = 5
            bar_x = self.rect.centerx - (bar_width / 2)
            bar_y = self.rect.bottom + 5 # Um pouco abaixo do inimigo
            
            # Desenha o fundo da barra (vermelho)
            pygame.draw.rect(screen, (180, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Desenha a vida atual (verde)
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))