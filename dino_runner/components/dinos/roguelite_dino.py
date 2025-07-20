# Ficheiro: dino_runner/components/dinos/roguelite_dino.py
# Autor: [O Seu Nome]
# Descrição: Define a classe do personagem principal para o modo de jogo "Roguelite".
#            Esta classe gereia os status, o movimento livre em 8 direções, as armas,
#            as habilidades e as animações do personagem.

import pygame
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from dino_runner.components.weapons.pistol import Pistol
from dino_runner.components.weapons.sword import Sword

class RogueliteDino:
    """
    Representa o personagem jogável no modo Roguelite, controlando todos os seus
    atributos de combate, progressão e interações.
    """
    def __init__(self, assets, sounds):
        """
        Inicializa o personagem do modo Roguelite.
        
        Args:
            assets (AssetManager): O gestor de assets para carregar as imagens.
            sounds (SoundManager): O gestor de som para reproduzir efeitos sonoros.
        """
        self.assets = assets
        self.sounds = sounds
        
        # --- Atributos Visuais e de Posição ---
        # A aparência é definida posteriormente, após a escolha da classe.
        self.running_images = []
        self.start_image = pygame.Surface((80, 90), pygame.SRCALPHA) # Imagem placeholder
        self.current_image = self.start_image
        self.rect = self.current_image.get_rect(center=(SCREEN_WIDTH / 2, 380))
        self.hitbox = self.rect.inflate(-20, -10)
        self.image_index = 0
        self.facing_right = True # Controla a direção para virar a imagem (flip).

        # --- Atributos de Movimento ---
        self.speed = 5
        self.is_moving = False

        # --- Atributos de Combate e Progressão ---
        self.health = 100
        self.max_health = 100
        self.exp = 0
        self.exp_to_next_level = 100
        self.level = 1
        self.weapon = None
        self.life_steal_percent = 0.0
        self.shot_quantity = 1 # Quantidade de ataques por clique/ativação.

        # --- Atributos de Feedback Visual ---
        self.is_flashing = False
        self.flash_duration = 150
        self.flash_start_time = 0

        # --- Atributos de Habilidade Especial (Botão Direito) ---
        self.special_ability_cooldown = 10000 # 10 segundos
        self.last_special_ability_time = -10000 # Permite o uso imediato no início.

    def set_character(self, start_asset, running_asset):
        """
        Define a aparência do personagem com base na classe escolhida (Dino ou Bero).
        Também redimensiona a imagem e a hitbox se necessário.
        """
        self.start_image = self.assets.get_image(start_asset)
        self.running_images = self.assets.get_image(running_asset)

        # Lógica para redimensionar o personagem "Bero" (Warrior)
        if start_asset == "BERO_START":
            new_size = (65, 80) 
            self.start_image = pygame.transform.scale(self.start_image, new_size)
            self.running_images = [pygame.transform.scale(img, new_size) for img in self.running_images]

        self.current_image = self.start_image
        
        old_center = self.rect.center
        self.rect = self.current_image.get_rect(center=old_center)
        # A hitbox é ajustada com base na nova imagem, para ser mais justa.
        self.hitbox = self.rect.inflate(-20, -15)

    def set_weapon(self, weapon_instance):
        """Equipa uma arma no personagem."""
        self.weapon = weapon_instance

    def attack(self):
        """Delega a ação de ataque para a arma atualmente equipada."""
        if self.weapon:
            return self.weapon.attack()
        return None

    def use_special_ability(self):
        """Tenta ativar a habilidade especial (botão direito) da arma equipada."""
        current_time = pygame.time.get_ticks()
        if self.weapon and current_time - self.last_special_ability_time > self.special_ability_cooldown:
            if hasattr(self.weapon, 'activate_special'):
                self.weapon.activate_special()
                self.last_special_ability_time = current_time
                print(f"Habilidade especial '{self.weapon.__class__.__name__}' ativada!")

    def update(self):
        """
        Atualiza o estado do personagem a cada frame, incluindo movimento, animação e armas.
        Retorna o resultado de um ataque de projétil, se houver.
        """
        attack_result = None
        if self.weapon:
            # O update da arma gereia lógicas contínuas (ex: rajadas, cooldowns internos)
            # e pode retornar um projétil para ser disparado.
            attack_result = self.weapon.update()

        # Gereia o efeito de flash de dano.
        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_start_time > self.flash_duration:
                self.is_flashing = False
        
        # --- Lógica de Movimento ---
        keys = pygame.key.get_pressed()
        vel_x, vel_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: vel_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vel_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: vel_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: vel_y = 1
        
        # Normaliza o vetor de movimento para que a velocidade diagonal não seja maior.
        if vel_x != 0 and vel_y != 0:
            vel_x /= 1.414; vel_y /= 1.414
        
        self.rect.x += vel_x * self.speed
        self.rect.y += vel_y * self.speed
        
        # Mantém a hitbox sincronizada com a posição do personagem.
        self.hitbox.center = self.rect.center
        
        self.is_moving = (vel_x != 0 or vel_y != 0)
        
        # Vira o personagem na direção do rato.
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.rect.centerx: self.facing_right = True
        else: self.facing_right = False
            
        self.animate()

        # Mantém o personagem dentro dos limites do ecrã.
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        
        self.hitbox.center = self.rect.center # Garante a posição final da hitbox.

        return attack_result

    def animate(self):
        """Gereia a animação de caminhada do personagem."""
        if self.running_images:
            if self.is_moving:
                self.image_index = (self.image_index + 0.25) % len(self.running_images)
                self.current_image = self.running_images[int(self.image_index)]
            # Se não estiver em movimento, a imagem permanece a última do ciclo,
            # criando um efeito de "parado" mais natural.

    def draw(self, screen, offset=[0, 0]):
        """Desenha o personagem no ecrã, aplicando efeitos visuais."""
        image_to_draw = pygame.transform.flip(self.current_image, not self.facing_right, False)
        
        # Aplica o efeito de flash vermelho se estiver a levar dano.
        if self.is_flashing:
            red_tint = image_to_draw.copy()
            red_tint.fill((180, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = red_tint
            
        screen.blit(image_to_draw, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
    def take_damage(self, amount):
        """Aplica dano ao personagem, considerando o escudo, e ativa o feedback visual."""
        if isinstance(self.weapon, Sword) and self.weapon.shield_active:
            amount *= 0.3 # Reduz o dano em 70%

        self.health -= amount
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.health = 0
            return True # Retorna True se o personagem morreu.
        return False

    def heal(self, amount):
        """Cura o personagem, limitado à sua vida máxima."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def gain_exp(self, amount):
        """Adiciona experiência e verifica se o personagem subiu de nível."""
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            return self.level_up()
        return False

    def level_up(self):
        """Processa a subida de nível, aumentando os status e a EXP necessária."""
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        self.heal(25) # Cura uma pequena quantidade ao subir de nível.
        print(f"LEVEL UP! Você alcançou o nível {self.level}!")
        return True
