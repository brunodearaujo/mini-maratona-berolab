# dino_runner/components/weapons/projectile.py
import pygame

class Projectile:
    def __init__(self, x, y, image, damage, speed, direction, pierce):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.pierce = pierce

    def update(self):
        # Move o projétil na sua direção
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)