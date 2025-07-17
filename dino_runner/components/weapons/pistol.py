import pygame
from dino_runner.components.weapons.weapon import Weapon
from dino_runner.components.weapons.bullet import Bullet

class Pistol(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.attack_cooldown = 300

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            
            mouse_pos = pygame.mouse.get_pos()
            player_pos = self.player.rect.center
            direction = pygame.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]).normalize()
            
            # Retorna a bala criada para que o modo de jogo possa gerenciá-la
            return Bullet(player_pos[0], player_pos[1], direction)
        return None