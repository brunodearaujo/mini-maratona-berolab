import pygame
from dino_runner.utils.constants import START_IMAGE, SCREEN_WIDTH

class RogueliteDino:
    def __init__(self):
            # ... (código existente: self.image, self.rect, etc.)
            self.image = START_IMAGE
            self.rect = self.image.get_rect()
            self.rect.bottom = 380
            self.rect.centerx = SCREEN_WIDTH / 2

            # Atributos de jogabilidade
            self.speed = 8
            self.health = 100
            self.max_health = 100

            # --- NOVOS ATRIBUTOS DE PROGRESSÃO ---
            self.exp = 0
            self.exp_to_next_level = 100 # A quantidade de EXP necessária para o próximo nível
            self.level = 1

    def update(self):
        """Atualiza o estado do dinossauro a cada frame."""
        # Pega um dicionário de todas as teclas que estão sendo pressionadas no momento.
        keys = pygame.key.get_pressed()
        
        # Reseta a velocidade horizontal
        vel_x = 0
        
        # Verifica as teclas de movimento para a esquerda
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x = -self.speed
            
        # Verifica as teclas de movimento para a direita
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x = self.speed
            
        # Atualiza a posição horizontal do dinossauro
        self.rect.x += vel_x
        
        # Adiciona limites para impedir que o dinossauro saia da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        # Futuramente, aqui também atualizaremos animações e outros estados.

    def take_damage(self, amount):
        """Reduz a vida do dinossauro."""
        self.health -= amount
        if self.health < 0:
            self.health = 0
        # Futuramente, aqui podemos adicionar uma animação de dano ou invencibilidade temporária.

    def draw(self, screen):
        """Desenha o dinossauro na tela."""
        screen.blit(self.image, self.rect)

