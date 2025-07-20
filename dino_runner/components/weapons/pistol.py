import pygame
from dino_runner.components.weapons.weapon import Weapon
from dino_runner.components.weapons.bullet import Bullet

class Pistol(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.attack_cooldown = 300
        self.is_frozen_shot_active = False
        self.shots_to_fire = 0
        self.time_between_shots = 80
        self.last_burst_shot_time = 0

    def activate_special(self):
        self.is_frozen_shot_active = True

    def attack(self):
        """Inicia a sequência de ataque em rajada."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            self.shots_to_fire = self.player.shot_quantity

    def update(self):
        """Verifica se deve disparar um tiro da rajada e retorna o projétil."""
        if self.shots_to_fire > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_burst_shot_time > self.time_between_shots:
                self.last_burst_shot_time = current_time
                self.shots_to_fire -= 1
                return self.fire_bullet() # Retorna a tupla da bala para o RogueliteMode
        return None

    def fire_bullet(self):
        """Cria e retorna as informações de uma bala."""
        mouse_pos = pygame.mouse.get_pos()
        player_pos = self.player.rect.center
        direction = pygame.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]).normalize()
        
        is_frozen = self.is_frozen_shot_active
        if is_frozen:
            self.is_frozen_shot_active = False
        
        return ("BULLET", player_pos[0], player_pos[1], direction, is_frozen)