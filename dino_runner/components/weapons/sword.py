import pygame
from dino_runner.components.weapons.weapon import Weapon

class Sword(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.damage = 40
        self.attack_cooldown = 400 # Cooldown um pouco maior que a pistola
        self.swing_duration = 150 # Duração do ataque em ms
        self.is_swinging = False
        self.hitbox = None

    def attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            self.is_swinging = True
            
            # --- LÓGICA DE MIRA CORRIGIDA ---
            # 1. Pega a posição do mouse e do jogador
            mouse_pos = pygame.mouse.get_pos()
            player_pos = self.player.rect.center
            
            # 2. Calcula o vetor de direção normalizado
            direction = pygame.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]).normalize()

            # 3. Define a posição da hitbox na direção do mouse
            swing_width = 80
            swing_height = 80
            # Posiciona o centro da hitbox a uma distância de 50 pixels do jogador, na direção do mouse
            hitbox_center = (player_pos[0] + direction.x * 50, player_pos[1] + direction.y * 50)
            
            self.hitbox = pygame.Rect(0, 0, swing_width, swing_height)
            self.hitbox.center = hitbox_center
            
            return True
        return False

    def update(self):
        # Verifica se o tempo do "swing" da espada já acabou
        if self.is_swinging:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.swing_duration:
                self.is_swinging = False
                self.hitbox = None
    
    def draw(self, screen):
        # Desenha a hitbox da espada para debug quando ela está ativa
        if self.is_swinging and self.hitbox:
            pygame.draw.rect(screen, (255, 255, 255, 150), self.hitbox, 3)