# Ficheiro: dino_runner/components/enemies/enemy.py
# Autor: [O Seu Nome]
# Descrição: Classe base para todos os inimigos do modo Roguelite.
#            Gereia os status, movimento, animação, habilidades e estados (Rage, Lento, etc.).

import pygame
import random
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from dino_runner.components.weapons.shard import Shard

class Enemy:
    """
    Representa um inimigo genérico no jogo, servindo como base para todos os tipos de monstros.
    """
    def __init__(self, x, y, image, health, damage, speed, exp_value, is_boss=False, rage_chance=0.1):
        """
        Inicializa um inimigo com todos os seus atributos.

        Args:
            x (int), y (int): Posições iniciais.
            image (Surface or list): A imagem ou lista de imagens para animação.
            health (int), damage (int), speed (float), exp_value (int): Status base.
            is_boss (bool): Define se este inimigo é um chefe.
            rage_chance (float): A probabilidade (0.0 a 1.0) de um inimigo normal nascer em modo "Rage".
        """
        # --- Atributos de Animação e Imagem ---
        self.is_animated = isinstance(image, list)
        if self.is_animated:
            self.animation_frames = image
            self.image_index = 0
            self.image = self.animation_frames[self.image_index]
        else:
            self.animation_frames = None
            self.image = image
        
        self.original_image = self.image # Guarda a imagem do primeiro frame como base para efeitos.
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.copy()

        # --- Atributos de Status e Combate ---
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.original_speed = speed # Guarda a velocidade original para reverter efeitos.
        self.exp_value = exp_value
        self.damage_resistance = 0.0

        # --- Atributos de Estado ---
        self.is_boss = is_boss
        self.is_in_rage = False
        self.is_transforming = False
        self.is_invulnerable = False
        self.is_slowed = False
        self.is_flashing = False
        self.is_entering = False
        self.is_casting = False
        self.show_image = True

        # --- Temporizadores e Contadores ---
        self.slow_duration = 0
        self.slow_start_time = 0
        self.transformation_start_time = 0
        self.flash_timer = 0
        self.flash_duration = 100
        self.flash_start_time = 0
        self.cast_count = 0
        self.time_between_casts = 600
        self.last_cast_time = 0
        self.skill_cooldown = 8000
        self.last_skill_time = 0
        self.heal_amount_per_second = 0

        # --- Lógica de Inicialização para Chefes ---
        if self.is_boss:
            self.health *= 5; self.damage *= 2; self.exp_value *= 10
            scaled_image = pygame.transform.scale_by(self.original_image, 2)
            self.image = scaled_image
            self.original_image = scaled_image
            self.rect = self.image.get_rect(center=self.rect.center)
            self.is_entering = True
            self.entry_target_pos = (SCREEN_WIDTH / 2, 150)
        
        # A chance de "Rage" só se aplica a inimigos normais.
        if not self.is_boss and random.random() < rage_chance:
            self.activate_rage()

    def update(self, player, enemy_projectiles):
        """Atualiza o estado e a posição do inimigo a cada frame."""
        # A máquina de estados do inimigo: cada estado tem prioridade sobre o seguinte.
        if self.is_entering:
            self.handle_entrance()
            return

        if self.is_transforming:
            self.handle_transformation()
            return
        
        if self.is_casting:
            self.handle_casting(enemy_projectiles)
            return

        # Lógicas de estado que podem ocorrer durante o movimento
        self.handle_status_effects()
        
        # Lógica de movimento padrão (perseguir jogador)
        self.handle_movement(player)

        # Garante que a hitbox se move juntamente com a imagem.
        self.hitbox.center = self.rect.center

    def handle_entrance(self):
        """Move o chefe para a sua posição inicial na arena."""
        target_x, target_y = self.entry_target_pos
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        if distance > self.speed:
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed
        else:
            self.rect.center = self.entry_target_pos
            self.is_entering = False

    def handle_transformation(self):
        """Gereia a animação e a cura do chefe durante a transformação."""
        current_time = pygame.time.get_ticks()
        self.health += self.heal_amount_per_second / FPS
        if self.health > self.max_health: self.health = self.max_health
        self.flash_timer += 1
        self.show_image = self.flash_timer % 10 >= 5
        if current_time - self.transformation_start_time > 3000:
            self.finish_transformation()

    def handle_casting(self, enemy_projectiles):
        """Gereia o combo de ataques da habilidade do chefe."""
        current_time = pygame.time.get_ticks()
        if self.cast_count < 3 and current_time - self.last_cast_time > self.time_between_casts:
            self.use_ground_slam(enemy_projectiles, self.assets)
            self.cast_count += 1
            self.last_cast_time = current_time
        elif self.cast_count >= 3:
            self.is_casting = False
            self.last_skill_time = current_time

    def handle_status_effects(self):
        """Atualiza os temporizadores de todos os efeitos de estado (lento, flash)."""
        current_time = pygame.time.get_ticks()
        if self.is_slowed and current_time - self.slow_start_time > self.slow_duration:
            self.is_slowed = False
            self.speed = self.original_speed
        if self.is_flashing and current_time - self.flash_start_time > self.flash_duration:
            self.is_flashing = False
        if self.is_animated:
            self.image_index = (self.image_index + 0.1) % len(self.animation_frames)
            self.image = self.animation_frames[int(self.image_index)]

    def handle_movement(self, player):
        """Gereia o movimento de perseguição e os limites do ecrã."""
        current_time = pygame.time.get_ticks()
        if self.is_boss and not self.is_transforming and not self.is_casting:
            if current_time - self.last_skill_time > self.skill_cooldown:
                self.is_casting = True
                self.cast_count = 0
                self.last_cast_time = current_time
        
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            dx /= distance; dy /= distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, screen, offset=[0, 0]):
        """Desenha o inimigo no ecrã, aplicando os efeitos visuais necessários."""
        image_to_draw = self.image
        if self.is_flashing:
            flash_image = self.image.copy()
            flash_image.fill((200, 200, 200), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = flash_image
        elif self.is_slowed:
            slow_image = self.image.copy()
            slow_image.fill((100, 100, 255), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = slow_image
        
        if self.show_image:
            screen.blit(image_to_draw, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
        self.draw_health_bar(screen, offset)

    def draw_health_bar(self, screen, offset=[0, 0]):
        """Desenha a barra de vida do inimigo."""
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.rect.width * 0.8
            bar_height = 5
            bar_x = self.rect.centerx - (bar_width / 2) + offset[0]
            bar_y = self.rect.bottom + 5 + offset[1]
            pygame.draw.rect(screen, (180, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

    def take_damage(self, amount):
        """Aplica dano ao inimigo, gereia a transformação do chefe e o feedback visual."""
        if self.is_invulnerable: return False
        if self.is_boss and not self.is_in_rage and (self.health - amount) / self.max_health <= 0.3:
            self.start_transformation()
            return False
        
        actual_damage = amount * (1 - self.damage_resistance)
        self.health -= actual_damage
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()
        return self.health <= 0

    def apply_slow(self, slow_factor, duration):
        """Aplica um efeito de lentidão ao inimigo."""
        if not self.is_slowed:
            self.speed *= (1 - slow_factor)
            self.is_slowed = True
            self.slow_duration = duration
            self.slow_start_time = pygame.time.get_ticks()
    
    def use_ground_slam(self, enemy_projectiles, assets):
        """Habilidade do chefe: lança estilhaços em 8 direções."""
        print(f"CHEFE usou Ground Slam #{self.cast_count + 1}!")
        angle_offset = random.uniform(-15, 15)
        directions = [
            pygame.math.Vector2(1, 0), pygame.math.Vector2(-1, 0),
            pygame.math.Vector2(0, 1), pygame.math.Vector2(0, -1),
            pygame.math.Vector2(1, 1).normalize(), pygame.math.Vector2(1, -1).normalize(),
            pygame.math.Vector2(-1, 1).normalize(), pygame.math.Vector2(-1, -1).normalize()
        ]
        for direction in directions:
            rotated_direction = direction.rotate(angle_offset)
            shard = Shard(self.rect.centerx, self.rect.centery, rotated_direction, assets)
            enemy_projectiles.append(shard)

    def start_transformation(self):
        """Inicia a sequência de transformação do chefe."""
        if self.is_transforming or self.is_in_rage: return
        self.is_transforming = True
        self.is_invulnerable = True
        self.transformation_start_time = pygame.time.get_ticks()
        self.heal_amount_per_second = self.max_health / 3.0

    def finish_transformation(self):
        """Finaliza a transformação e ativa o modo rage."""
        self.is_transforming = False
        self.is_invulnerable = False
        self.health = self.max_health
        self.damage_resistance = 0.3
        self.show_image = True
        self.activate_rage()

    def activate_rage(self):
        """Ativa o modo "Rage", aumentando status e mudando a aparência."""
        if self.is_in_rage: return
        self.is_in_rage = True
        self.speed *= 1.5
        self.health = int(self.health * 1.5)
        self.max_health = self.health
        rage_image = self.original_image.copy()
        mask = pygame.mask.from_surface(rage_image)
        mask_surf = mask.to_surface(setcolor=(255, 0, 0), unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0, 0, 0))
        rage_image.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.image = rage_image
