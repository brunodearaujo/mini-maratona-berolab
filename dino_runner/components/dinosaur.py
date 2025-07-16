# dino_runner/components/dinosaur.py
import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING, DEAD

# Em dinosaur.py

import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING

# Em dinosaur.py

import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING

class Dinosaur:
    # --- Constantes de Física (AJUSTADAS PARA UM JOGO MAIS RÁPIDO) ---
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VELOCITY = 17  # Aumentamos a força inicial do pulo
    GRAVITY = 1.2       # Gravidade um pouco mais forte

    def __init__(self):
        # --- Carregando as imagens ---
        self.running_img = RUNNING
        self.jumping_img = JUMPING
        self.ducking_img = DUCKING

        # --- Estado Inicial ---
        self.is_running = True
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False

        # --- Atributos de Movimento ---
        self.jump_vel = self.JUMP_VELOCITY
        self.image = self.running_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index = 0

# Em dinosaur.py

import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING

# Em dinosaur.py

import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING

class Dinosaur:
    # --- Constantes de Física, inspiradas no jogo original ---
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    
    # Valores ajustados para Pygame, mantendo a proporção do original
    JUMP_VELOCITY = 36.5
    GRAVITY = 3
    FAST_FALL_GRAVITY = 3
    
    def __init__(self):
        # --- Carregando as imagens ---
        self.running_img = RUNNING
        self.jumping_img = JUMPING
        self.ducking_img = DUCKING
        self.dead_img = DEAD

        # --- Estado Inicial ---
        self.is_running = True
        self.is_jumping = False
        self.is_ducking = False

        # --- Atributos de Movimento ---
        self.jump_vel = self.JUMP_VELOCITY
        self.image = self.running_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index = 0

    # Em dinosaur.py, substitua seu método update() inteiro por este:

    # Em dinosaur.py, substitua seu método update() inteiro:

    def update(self):
        # A ordem da checagem de estado é importante

        if self.is_jumping:
            # Por padrão, a imagem é a de pulo
            self.image = self.jumping_img

            # Se estiver agachado no ar...
            if self.is_ducking:
                # --- NOVO BLOCO PARA CORRIGIR O HITBOX AÉREO ---
                # Salva a posição central do hitbox atual (o grande)
                original_center = self.dino_rect.center
                # Muda a imagem para a de agachar
                self.image = self.ducking_img[1]
                # Cria um novo rect (hitbox) a partir da nova imagem (que é menor)
                self.dino_rect = self.image.get_rect()
                # Move o novo rect para o centro do antigo. Isso faz o dino "encolher" no lugar certo.
                self.dino_rect.center = original_center
                # --- FIM DO NOVO BLOCO ---

                # Aplica GRAVIDADE EXTRA para a queda rápida
                self.jump_vel -= self.FAST_FALL_GRAVITY

            # Aplica a gravidade NORMAL
            self.jump_vel -= self.GRAVITY
            # Aplica a velocidade final à posição Y
            self.dino_rect.y -= self.jump_vel

        elif self.is_ducking:
            self.duck_animation()

        elif self.is_running:
            self.run_animation()

        # O resto do código continua igual...
        if not self.is_running and not self.is_ducking:
            self.step_index = 0

        if self.is_jumping and self.dino_rect.y >= self.Y_POS:
            self.is_jumping = False
            self.jump_vel = self.JUMP_VELOCITY

            if self.is_ducking:
                self.set_duck_state()
            else:
                self.set_run_state()

    def run_animation(self):
        self.image = self.running_img[self.step_index // 5]
        self.dino_rect.y = self.Y_POS
        self.step_index = (self.step_index + 1) % 10

    def duck_animation(self):
        self.image = self.ducking_img[self.step_index // 5]
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index = (self.step_index + 1) % 10

    def set_run_state(self):
        self.image = self.running_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.is_running = True
        self.is_ducking = False

    def set_duck_state(self):
        self.image = self.ducking_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.is_ducking = True
        self.is_running = False

    def jump(self):
        if not self.is_jumping:
            self.jump_vel = self.JUMP_VELOCITY
            self.is_jumping = True
            self.is_running = False
            self.is_ducking = False

    def duck(self):
        if self.is_jumping:
            self.is_ducking = True
            # Se ainda estiver subindo, cancela a subida para a queda ser instantânea
            if self.jump_vel > 0:
                self.jump_vel = 0 
        else: # Se estiver no chão, apenas agacha
            self.set_duck_state()

    # Em dinosaur.py, substitua seu método unduck() inteiro por este:

    def unduck(self):
        # Se estiver no ar...
        if self.is_jumping:
            # Apenas desativa a flag de agachamento
            self.is_ducking = False
            
            # --- NOVO BLOCO PARA RESTAURAR O HITBOX NO AR ---
            # Salva a posição central do hitbox atual (o pequeno)
            original_center = self.dino_rect.center
            # Restaura a imagem para a de pulo normal
            self.image = self.jumping_img
            # Cria um novo rect grande a partir da imagem de pulo
            self.dino_rect = self.image.get_rect()
            # Posiciona o novo rect grande alinhado ao centro do antigo rect pequeno
            self.dino_rect.center = original_center
            # --- FIM DO NOVO BLOCO ---
    
        # Se estiver no chão, simplesmente volta ao estado de corrida completo
        else:
            self.set_run_state()

    def die(self):
        # define a imagem de morte e para todas as outras ações
        self.image = self.dead_img
        self.is_dead = True
        self.is_running = False
        self.is_jumping = False
        self.is_ducking = False

    def draw(self, screen):
        screen.blit(self.image, self.dino_rect)