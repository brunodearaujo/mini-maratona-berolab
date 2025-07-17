import pygame
from dino_runner.utils.constants import START_IMAGE, RUNNING, SCREEN_WIDTH, SCREEN_HEIGHT

class RogueliteDino:
    def __init__(self):
        # Carregando as imagens de animação
        self.running_images = RUNNING
        self.start_image = START_IMAGE
        self.image_index = 0
        self.current_image = self.running_images[0]
        
        # Atributos de posição e movimento
        self.rect = self.current_image.get_rect(center=(SCREEN_WIDTH / 2, 380))
        self.speed = 5 # Ajustei a velocidade para 8 direções
        self.weapon = None
        self.is_moving = False
        
        # Atributos de combate e progressão
        self.health = 100
        self.max_health = 100
        self.exp = 0
        self.exp_to_next_level = 100
        self.level = 1

        # Guarda a direção para virar o sprite
        self.facing_right = True
        
        # --- NOVO ATRIBUTO PARA ROUBO DE VIDA ---
        self.life_steal_percent = 0.0 # Começa com 0%

    def set_weapon(self, weapon_instance):
        """Equipa uma arma no dinossauro."""
        self.weapon = weapon_instance

    def attack(self):
        """Tenta executar um ataque com a arma equipada."""
        if self.weapon:
            return self.weapon.attack()
        return None

    def update(self):
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

    def draw(self, screen):
        # Vira a imagem horizontalmente se não estiver virado para a direita
        image_to_draw = pygame.transform.flip(self.current_image, not self.facing_right, False)
        screen.blit(image_to_draw, self.rect)  
        
    def take_damage(self, amount):
        """Reduz a vida do dinossauro e retorna True se ele morreu."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True # Sinaliza que o jogador morreu
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