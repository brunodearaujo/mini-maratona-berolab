import pygame
import math
from dino_runner.components.weapons.weapon import Weapon

class Sword(Weapon):
    def __init__(self, player):
        super().__init__(player)
        # BALANCEAMENTO: Dano e velocidade de ataque iniciais reduzidos
        self.damage = 25
        self.attack_cooldown = 550 # Aprox. 1.8 ataques/s
        self.swing_duration = 100
        
        self.is_swinging = False
        self.hitbox = None
        self.size = 1.0
        
        self.shield_active = False
        self.shield_duration = 3000
        self.shield_start_time = 0

        self.swings_to_make = 0
        self.time_between_swings = 150
        self.last_burst_swing_time = 0
        
        # CORREÇÃO: Adiciona o conjunto para rastrear inimigos atingidos
        self.hit_enemies = set()

        self.slash_image_base = self.player.assets.get_image("SWORD_SLASH")
        self.slash_image_base = pygame.transform.rotate(self.slash_image_base, 135)
        self.slash_image_base = pygame.transform.scale(self.slash_image_base, (100, 100))
        self.slash_image_original = self.slash_image_base
        self.slash_image = self.slash_image_original
        self.slash_rect = self.slash_image.get_rect()

    def activate_special(self):
        self.shield_active = True
        self.shield_start_time = pygame.time.get_ticks()

    def attack(self):
        current_time = pygame.time.get_ticks()
        if self.swings_to_make > 0: return
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            self.swings_to_make = self.player.shot_quantity
            self.perform_swing()
            self.player.sounds.play("sword_slash")

    def perform_swing(self):
        """Executa um único corte da espada."""
        self.is_swinging = True
        self.last_burst_swing_time = pygame.time.get_ticks()
        self.hit_enemies.clear()
        
        swing_width = int(80 * self.size); swing_height = int(80 * self.size)
        mouse_pos = pygame.mouse.get_pos(); player_pos = self.player.rect.center
        direction = pygame.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1])
        if direction.length() > 0:
            direction.normalize_ip()

        hitbox_center = (player_pos[0] + direction.x * 50, player_pos[1] + direction.y * 50)
        self.hitbox = pygame.Rect(0, 0, swing_width, swing_height); self.hitbox.center = hitbox_center
        
        scaled_slash_image = pygame.transform.scale_by(self.slash_image_original, self.size)
        angle = math.degrees(math.atan2(player_pos[1] - mouse_pos[1], mouse_pos[0] - player_pos[0]))
        self.slash_image = pygame.transform.rotate(scaled_slash_image, angle)
        self.slash_rect = self.slash_image.get_rect(center=self.hitbox.center)

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.swings_to_make > 0:
            if current_time - self.last_burst_swing_time > self.time_between_swings:
                self.swings_to_make -= 1
                if self.swings_to_make > 0:
                    self.perform_swing()
                    self.player.sounds.play("sword_slash")

        if self.is_swinging and current_time - self.last_burst_swing_time > self.swing_duration:
            self.is_swinging = False; self.hitbox = None
        if self.shield_active and current_time - self.shield_start_time > self.shield_duration:
            self.shield_active = False
    
    def draw(self, screen, offset=[0, 0]):
        if self.is_swinging:
            screen.blit(self.slash_image, (self.slash_rect.x + offset[0], self.slash_rect.y + offset[1]))
            if self.hitbox:
                offset_hitbox = self.hitbox.move(offset[0], offset[1])
                #pygame.draw.rect(screen, (255, 255, 255), offset_hitbox, 2)
        
        if self.shield_active:
            shield_surf = pygame.Surface(self.player.rect.size, pygame.SRCALPHA)
            shield_color = (100, 100, 255, 120)
            pygame.draw.circle(shield_surf, shield_color, (self.player.rect.width / 2, self.player.rect.height / 2), 50)
            screen.blit(shield_surf, (self.player.rect.x + offset[0], self.player.rect.y + offset[1]))
