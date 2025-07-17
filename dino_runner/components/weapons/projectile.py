import pygame

class Projectile:
    def __init__(self, x, y, image_path, damage, speed, direction, pierce):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 0)) # Placeholder amarelo

        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.speed = speed
        self.direction = direction # Um vetor de direção (ex: pygame.math.Vector2)
        self.pierce = pierce # Quantos inimigos pode atravessar

    def update(self):
        # Move o projétil na sua direção
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)