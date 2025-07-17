import pygame

class Enemy:
    def __init__(self, x, y, image_path, health, damage, speed, exp_value):
        # Tenta carregar a imagem do inimigo. Se falhar, usa um placeholder.
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            print(f"Aviso: Imagem '{image_path}' não encontrada. Usando um placeholder.")
            self.image = pygame.Surface((30, 50)) # Largura e altura do placeholder
            self.image.fill((0, 180, 0)) # Cor verde

        self.rect = self.image.get_rect(center=(x, y))

        # Atributos de combate
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.exp_value = exp_value

    def update(self, player):
        # A lógica de movimento (IA) será implementada nas classes filhas
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True # Retorna True se o inimigo morreu
        return False