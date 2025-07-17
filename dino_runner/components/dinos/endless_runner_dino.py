# dino_runner/components/dinos/endless_runner_dino.py

import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING, DEAD, START_IMAGE

class EndlessRunnerDino:
    # --- Constantes de Física ---
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VELOCITY = 36.5
    GRAVITY = 3
    FAST_FALL_GRAVITY = 3 # Gravidade extra para a queda rápida

    def __init__(self, first_run=False):
        # --- Carregando as imagens ---
        self.running_img = RUNNING
        self.jumping_img = JUMPING
        self.ducking_img = DUCKING
        self.dead_img = DEAD
        self.start_img = START_IMAGE

        # --- Estado Inicial ---
        self.is_waiting = first_run
        self.is_running = not first_run
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False

        # --- Atributos de Movimento ---
        self.jump_vel = self.JUMP_VELOCITY
        self.image = self.start_img if self.is_waiting else self.running_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.step_index = 0

    def update(self):
        if self.is_dead or self.is_waiting:
            return

        # --- Gerenciamento de Animação e Estado ---
        if self.is_jumping:
            self.image = self.jumping_img
            # LÓGICA DE HITBOX NO AR (do seu código antigo)
            if self.is_ducking:
                original_center = self.dino_rect.center
                self.image = self.ducking_img[1] # Imagem agachado no ar
                self.dino_rect = self.image.get_rect()
                self.dino_rect.center = original_center
        elif self.is_ducking:
            self.duck_animation()
        elif self.is_running:
            self.run_animation()
        
        # --- Física do Pulo ---
        if self.is_jumping:
            self.dino_rect.y -= self.jump_vel
            self.jump_vel -= self.GRAVITY
            if self.is_ducking:
                self.jump_vel -= self.FAST_FALL_GRAVITY

        # --- Lógica de Pouso ---
        if self.is_jumping and self.dino_rect.y >= self.Y_POS:
            self.is_jumping = False
            self.jump_vel = self.JUMP_VELOCITY
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.set_duck_state()
            else:
                self.set_run_state()

    def run_animation(self):
        self.image = self.running_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.step_index = (self.step_index + 1) % 10

    def duck_animation(self):
        self.image = self.ducking_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS_DUCK)
        self.step_index = (self.step_index + 1) % 10

    # --- Métodos de Estado ---
    def set_run_state(self):
        self.image = self.running_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS)
        self.is_running = True
        self.is_ducking = False

    def set_duck_state(self):
        self.image = self.ducking_img[0]
        self.dino_rect = self.image.get_rect(x=self.X_POS, y=self.Y_POS_DUCK)
        self.is_ducking = True
        self.is_running = False

    def jump(self):
        if self.is_waiting:
            self.is_waiting = False
        
        if not self.is_jumping:
            self.jump_vel = self.JUMP_VELOCITY
            self.is_jumping = True
            self.is_running = False
            self.is_ducking = False

    def duck(self):
        if self.is_jumping:
            self.is_ducking = True
            if self.jump_vel > 0:
                self.jump_vel = 0
        elif self.is_running:
            self.set_duck_state()

    def unduck(self):
        if self.is_jumping:
            self.is_ducking = False
            original_center = self.dino_rect.center
            self.image = self.jumping_img
            self.dino_rect = self.image.get_rect()
            self.dino_rect.center = original_center
        else:
            self.set_run_state()

    def die(self):
        self.image = self.dead_img
        self.is_dead = True

    def draw(self, screen):
        screen.blit(self.image, self.dino_rect)