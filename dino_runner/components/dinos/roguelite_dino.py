# Arquivo: dino_runner/components/dinos/roguelite_dino.py

import pygame
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from dino_runner.components.weapons.pistol import Pistol
from dino_runner.components.weapons.sword import Sword

class RogueliteDino:
    def __init__(self, assets):
        self.assets = assets

        self.running_images = []
        self.start_image = None
        self.image_index = 0
        self.current_image = pygame.Surface((80, 90), pygame.SRCALPHA)

        self.rect = self.current_image.get_rect(center=(SCREEN_WIDTH / 2, 380))
        self.speed = 5
        self.is_moving = False

        self.health = 100
        self.max_health = 100
        self.exp = 0
        self.exp_to_next_level = 100
        self.level = 1
        self.weapon = None
        self.facing_right = True
        self.life_steal_percent = 0.0

        # --- ATRIBUTOS PARA O FLASH DE DANO ---
        self.is_flashing = False
        self.flash_duration = 150 # Duração do flash em milissegundos
        self.flash_start_time = 0

    def set_character(self, start_asset, running_asset):
        """Define as imagens do personagem (Dino ou Bero)."""
        self.start_image = self.assets.get_image(start_asset)
        self.running_images = self.assets.get_image(running_asset)
        self.current_image = self.start_image
        # Atualiza o rect com a nova imagem
        old_center = self.rect.center if hasattr(self, 'rect') else (SCREEN_WIDTH / 2, 380)
        self.rect = self.current_image.get_rect(center=old_center)

    def set_weapon(self, weapon_instance):
        """Equipa uma arma no dinossauro."""
        self.weapon = weapon_instance

    def attack(self):
        """Tenta executar um ataque com a arma equipada."""
        if self.weapon:
            return self.weapon.attack()
        return None

    def update(self):
        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start_time > self.flash_duration:
                self.is_flashing = False

        # Pega o estado das teclas
        keys = pygame.key.get_pressed()
        
        # --- LÓGICA DE MOVIMENTO EM 8 DIREÇÕES ---
        # Reseta a velocidade para este frame
        vel_x, vel_y = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vel_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vel_y = 1

        # Normaliza o vetor de movimento para que a velocidade diagonal não seja maior
        if vel_x != 0 and vel_y != 0:
            vel_x /= 1.414 # Aproximadamente a raiz quadrada de 2
            vel_y /= 1.414

        # Aplica a velocidade ao movimento
        self.rect.x += vel_x * self.speed
        self.rect.y += vel_y * self.speed
        
        # Verifica se o jogador está se movendo para controlar a animação
        self.is_moving = (vel_x != 0 or vel_y != 0)

        # --- LÓGICA DE MIRA E SPRITE FLIP ---
        mouse_pos = pygame.mouse.get_pos()
        # Vira o sprite para a direita se o mouse estiver à direita do centro do dino
        if mouse_pos[0] > self.rect.centerx:
            self.facing_right = True
        # Vira para a esquerda se o mouse estiver à esquerda
        else:
            self.facing_right = False
            
        # --- LÓGICA DE ANIMAÇÃO ---
        self.animate()

        if self.weapon:
            self.weapon.update()

        # Limites da tela
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        # --- CORREÇÃO DO CHÃO INVISÍVEL ---
        # O limite inferior agora é a parte de baixo da tela
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

    def animate(self):
        if self.is_moving:
            self.image_index = (self.image_index + 0.25) % len(self.running_images)
            self.current_image = self.running_images[int(self.image_index)]

    def draw(self, screen, offset=[0, 0]):
        """Desenha o personagem, aplicando o flash de dano se necessário."""
        image_to_draw = pygame.transform.flip(self.current_image, not self.facing_right, False)
        
        # Se estiver a piscar, desenha uma versão avermelhada da imagem
        if self.is_flashing:
            red_tint = image_to_draw.copy()
            # O modo BLEND_RGB_ADD cria um efeito de brilho vermelho
            red_tint.fill((180, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = red_tint
            
        screen.blit(image_to_draw, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
    def take_damage(self, amount):
       """Reduz a vida, ativa o flash de dano e retorna True se morreu."""
       self.health -= amount
       
       # Ativa o flash
       self.is_flashing = True
       self.flash_start_time = pygame.time.get_ticks()
       if self.health <= 0:
           self.health = 0
           return True
       return False


    def heal(self, amount):
        """Aumenta a vida do dinossauro, sem ultrapassar a vida máxima."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def gain_exp(self, amount):
        """Aumenta a EXP do jogador e verifica se ele subiu de nível."""
        self.exp += amount
        print(f"Ganhou {amount} de EXP! Total: {self.exp}/{self.exp_to_next_level}")

        if self.exp >= self.exp_to_next_level:
            return self.level_up() # Retorna True para sinalizar que subiu de nível
        return False

    def level_up(self):
        """Processa a lógica de subir de nível."""
        self.level += 1
        # Leva o excesso de EXP para o próximo nível
        self.exp -= self.exp_to_next_level
        # Aumenta a quantidade de EXP necessária para o próximo nível
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Recupera um pouco de vida ao subir de nível
        self.health = min(self.max_health, self.health + 25)

        print(f"LEVEL UP! Você alcançou o nível {self.level}!")
        return True