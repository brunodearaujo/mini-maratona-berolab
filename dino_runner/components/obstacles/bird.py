# dino_runner/components/obstacles/bird.py
import pygame
import random
from dino_runner.components.obstacles.obstacle import Obstacle

class Bird(Obstacle):
    def __init__(self, assets):
        bird_images = assets.get_image("BIRD")
        # O 'type' é usado apenas para a imagem inicial
        super().__init__(assets, bird_images, 0)
        
        # CORREÇÃO: O pássaro agora pode aparecer em duas alturas diferentes.
        self.rect.y = random.choice([250, 300])
        
        # CORREÇÃO: Cria uma hitbox personalizada e mais justa para o pássaro.
        self.hitbox = self.rect.inflate(-20, -20)
        
        self.image_index = 0

    def update(self, game_speed, obstacle_list):
        """Atualiza a animação e a posição do pássaro."""
        # A animação agora é atualizada aqui, na lógica do jogo.
        self.image_index = (self.image_index + 0.1) % len(self.image)
        
        # Chama o update da classe pai para mover o obstáculo e a hitbox.
        super().update(game_speed, obstacle_list)

    def draw(self, screen):
        """Desenha o frame de animação atual do pássaro."""
        # O método draw agora apenas desenha a imagem do frame correto.
        screen.blit(self.image[int(self.image_index)], self.rect)