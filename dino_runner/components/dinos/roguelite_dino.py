import pygame
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from dino_runner.components.weapons.pistol import Pistol
from dino_runner.components.weapons.sword import Sword

class RogueliteDino:
    def __init__(self, assets, sounds):
        self.assets = assets
        self.running_images = []
        self.start_image = pygame.Surface((80, 90), pygame.SRCALPHA)
        self.current_image = self.start_image
        self.rect = self.current_image.get_rect(center=(SCREEN_WIDTH / 2, 380))
        self.hitbox = self.rect.inflate(-20, -10)
        self.image_index = 0
        self.sounds = sounds # Armazena a referência para o SoundManager
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
        self.is_flashing = False
        self.flash_duration = 150
        self.flash_start_time = 0

        self.special_ability_cooldown = 10000 # 10s de cooldown para a habilidade
        self.last_special_ability_time = -10000 # Permite o uso imediato
        self.shot_quantity = 1 # Quantidade de ataques por clique

    def use_special_ability(self):
        """Tenta ativar a habilidade especial da arma equipada."""
        current_time = pygame.time.get_ticks()
        if self.weapon and current_time - self.last_special_ability_time > self.special_ability_cooldown:
            if hasattr(self.weapon, 'activate_special'):
                self.weapon.activate_special()
                self.last_special_ability_time = current_time
                print(f"Habilidade especial '{self.weapon.__class__.__name__}' ativada!")


    def set_character(self, start_asset, running_asset):
        """Define as imagens do personagem e atualiza o rect/hitbox."""
        self.start_image = self.assets.get_image(start_asset)
        self.running_images = self.assets.get_image(running_asset)

        # --- CORREÇÃO: REDIMENSIONAMENTO PARA O GUERREIRO (BERO) ---
        if start_asset == "BERO_START":
            # Altere (largura, altura) para o tamanho que desejar.
            new_size = (65, 80) 
            self.start_image = pygame.transform.scale(self.start_image, new_size)
            # Redimensiona cada imagem da animação de corrida
            self.running_images = [pygame.transform.scale(img, new_size) for img in self.running_images]

        self.current_image = self.start_image
        
        old_center = self.rect.center
        self.rect = self.current_image.get_rect(center=old_center)
        # A hitbox agora é baseada na nova imagem, já menor
        self.hitbox = self.rect.inflate(-20, -15) # Reduz ainda mais para ser justo


    def set_weapon(self, weapon_instance):
        self.weapon = weapon_instance

    def attack(self):
        if self.weapon:
            return self.weapon.attack()
        return None

    def update(self):
        """Atualiza o jogador e retorna o resultado de um ataque, se houver."""
        attack_result = None
        if self.weapon:
            # O update da arma agora pode retornar um projétil
            attack_result = self.weapon.update()

        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_start_time > self.flash_duration:
                self.is_flashing = False
        
        keys = pygame.key.get_pressed()
        vel_x, vel_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: vel_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vel_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: vel_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: vel_y = 1
        if vel_x != 0 and vel_y != 0:
            vel_x /= 1.414; vel_y /= 1.414
        
        self.rect.x += vel_x * self.speed
        self.rect.y += vel_y * self.speed
        self.hitbox.center = self.rect.center
        
        self.is_moving = (vel_x != 0 or vel_y != 0)
        
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.rect.centerx: self.facing_right = True
        else: self.facing_right = False
            
        self.animate()

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        
        self.hitbox.center = self.rect.center

        return attack_result

    def animate(self):
        # CORREÇÃO: O 'else' foi removido. A imagem só muda se o personagem
        # estiver em movimento. Se ele parar, a imagem permanece a última da animação.
        if self.running_images:
            if self.is_moving:
                self.image_index = (self.image_index + 0.25) % len(self.running_images)
                self.current_image = self.running_images[int(self.image_index)]

    def draw(self, screen, offset=[0, 0]):
        image_to_draw = pygame.transform.flip(self.current_image, not self.facing_right, False)
        if self.is_flashing:
            red_tint = image_to_draw.copy()
            red_tint.fill((180, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = red_tint
        screen.blit(image_to_draw, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
    def take_damage(self, amount):

        if isinstance(self.weapon, Sword) and self.weapon.shield_active:
            amount *= 0.3 # Reduz o dano em 70%

        self.health -= amount
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()
        if self.health <= 0:
            self.health = 0
            return True
        return False

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            return self.level_up()
        return False

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.heal(25)
        print(f"LEVEL UP! Você alcançou o nível {self.level}!")
        return True
