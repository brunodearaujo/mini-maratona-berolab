# dino_runner/components/dinosaur.py
import pygame
from dino_runner.utils.constants import RUNNING, JUMPING, DUCKING, DEAD

# Em dinosaur.py

class Dinosaur:
    # --- Constantes de Física (RESTAURANDO SEUS VALORES) ---
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    
    JUMP_VELOCITY = 36.5 # <-- Seu valor para um pulo alto e rápido
    GRAVITY = 3          # <-- Sua gravidade forte para compensar
    FAST_FALL_GRAVITY = 3
    # --- Fim das constantes ---

    def __init__(self):
        # O resto da classe continua exatamente igual...
        # --- Carregando as imagens ---
        self.running_img = RUNNING
        self.jumping_img = JUMPING
        self.ducking_img = DUCKING
        self.dead_img = DEAD

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

    def update(self):
        if self.is_dead:
            return # Se estiver morto, não faz mais nada

        if self.is_jumping:
            self.image = self.jumping_img
            if self.is_ducking:
                original_center = self.dino_rect.center
                self.image = self.ducking_img[1]
                self.dino_rect = self.image.get_rect()
                self.dino_rect.center = original_center
                self.jump_vel -= self.FAST_FALL_GRAVITY
            
            self.jump_vel -= self.GRAVITY
            self.dino_rect.y -= self.jump_vel
        
        elif self.is_ducking:
            self.duck_animation()
        
        elif self.is_running:
            self.run_animation()

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
            if self.jump_vel > 0:
                self.jump_vel = 0 
        else:
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

    def reset(self):
        # Este é o método que faltava
        self.is_running = True
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False
        self.jump_vel = self.JUMP_VELOCITY
        self.set_run_state() # set_run_state já redefine a imagem e a posição

    def draw(self, screen):
        screen.blit(self.image, self.dino_rect)