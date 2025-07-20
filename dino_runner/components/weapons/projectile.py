class Projectile:
    def __init__(self, x, y, image, damage, speed, direction, pierce):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        # CORREÇÃO: Garante que TODOS os projéteis têm uma hitbox por padrão.
        self.hitbox = self.rect.copy()
        
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.pierce = pierce

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        # Garante que a hitbox se move juntamente com a imagem
        self.hitbox.center = self.rect.center

    def draw(self, screen, offset=[0, 0]):
        screen.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))