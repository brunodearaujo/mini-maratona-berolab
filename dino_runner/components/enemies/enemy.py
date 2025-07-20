# dino_runner/components/enemies/bero_run/enemy.py

import pygame
import random
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from dino_runner.components.weapons.shard import Shard

class Enemy:
    import pygame
import random
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from dino_runner.components.weapons.shard import Shard

class Enemy:
    def __init__(self, x, y, image, health, damage, speed, exp_value, is_boss=False, rage_chance=0.1):
        # CORREÇÃO: Lida com imagens únicas ou listas de imagens (para animação)
        self.is_animated = isinstance(image, list)
        if self.is_animated:
            self.animation_frames = image
            self.image_index = 0
            self.image = self.animation_frames[self.image_index]
        else:
            self.animation_frames = None
            self.image = image
        
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.copy()
        
        self.speed = speed
        self.original_speed = speed # Guarda a velocidade original
        self.is_slowed = False
        self.slow_duration = 0
        self.slow_start_time = 0

        self.original_image = self.image # Guarda a imagem do primeiro frame como original
        self.is_boss = is_boss
        self.is_in_rage = False
        self.is_transforming = False
        self.is_invulnerable = False
        self.damage_resistance = 0.0
        self.transformation_start_time = 0
        self.flash_timer = 0
        self.show_image = True
        self.heal_amount_per_second = 0
        self.is_flashing = False
        self.flash_duration = 100
        self.flash_start_time = 0
        self.is_casting = False
        self.cast_count = 0
        self.time_between_casts = 600
        self.last_cast_time = 0
        self.skill_cooldown = 8000
        self.last_skill_time = 0

        if self.is_boss:
            health *= 5; damage *= 2; exp_value *= 10
            scaled_image = pygame.transform.scale_by(self.original_image, 2)
            self.image = scaled_image
            self.original_image = scaled_image
            self.rect = self.image.get_rect(center=self.rect.center)
            self.is_entering = True
            self.entry_target_pos = (SCREEN_WIDTH / 2, 150)
        
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.exp_value = exp_value

        if not self.is_boss and random.random() < rage_chance:
            self.activate_rage()


    def apply_slow(self, slow_factor, duration):
        """Aplica um efeito de lentidão ao inimigo."""
        if not self.is_slowed:
            self.speed *= (1 - slow_factor)
            self.is_slowed = True
            self.slow_duration = duration
            self.slow_start_time = pygame.time.get_ticks()
    
    def use_ground_slam(self, enemy_projectiles, assets):
        """O chefe bate no chão, lançando estilhaços em 8 direções com um leve desvio."""
        print(f"CHEFE usou Ground Slam #{self.cast_count + 1}!")
        
        # Adiciona um pequeno desvio ao ângulo de cada ataque do combo
        angle_offset = random.uniform(-15, 15)
        
        directions = [
            pygame.math.Vector2(1, 0), pygame.math.Vector2(-1, 0),
            pygame.math.Vector2(0, 1), pygame.math.Vector2(0, -1),
            pygame.math.Vector2(1, 1).normalize(), pygame.math.Vector2(1, -1).normalize(),
            pygame.math.Vector2(-1, 1).normalize(), pygame.math.Vector2(-1, -1).normalize()
        ]
        
        for direction in directions:
            # Rotaciona o vetor de direção pelo desvio
            rotated_direction = direction.rotate(angle_offset)
            shard = Shard(self.rect.centerx, self.rect.centery, rotated_direction, assets)
            enemy_projectiles.append(shard)

    def start_transformation(self):
        """Inicia a sequência de transformação do chefe."""
        if self.is_transforming or self.is_in_rage: return

        print("!!! O CHEFE ESTÁ SE TRANSFORMANDO !!!")
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
        """Ativa o modo de raiva, aumentando status e mudando a aparência."""
        if self.is_in_rage: return
        self.is_in_rage = True
        self.speed *= 1.5
        self.health = int(self.health * 1.5)
        self.max_health = self.health

        # CORREÇÃO: Cria um efeito de "rage" que segue o contorno do personagem.
        # Isto evita o "quadrado vermelho" grande.
        rage_image = self.original_image.copy()
        # Cria uma máscara a partir da transparência da imagem
        mask = pygame.mask.from_surface(rage_image)
        # Converte a máscara numa superfície que podemos colorir
        mask_surf = mask.to_surface(setcolor=(255, 0, 0), unsetcolor=(0, 0, 0))
        # Define a cor preta como transparente
        mask_surf.set_colorkey((0, 0, 0))
        
        # Desenha o brilho vermelho por cima da imagem original
        rage_image.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.image = rage_image
        
    def take_damage(self, amount):
        if self.is_invulnerable: return False
        if self.is_boss and not self.is_in_rage and (self.health - amount) / self.max_health <= 0.3:
            self.start_transformation()
            return False
        
        actual_damage = amount * (1 - self.damage_resistance)
        self.health -= actual_damage
        
        # Ativa o flash de dano
        self.is_flashing = True
        self.flash_start_time = pygame.time.get_ticks()

        return self.health <= 0

    def update(self, player, enemy_projectiles):

        if self.is_slowed:
            current_time = pygame.time.get_ticks()
            if current_time - self.slow_start_time > self.slow_duration:
                self.is_slowed = False
                self.speed = self.original_speed # Restaura a velocidade
        

        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_start_time > self.flash_duration:
                self.is_flashing = False

        if self.is_animated:
            self.image_index = (self.image_index + 0.1) % len(self.animation_frames)
            self.image = self.animation_frames[int(self.image_index)]

        """Atualiza a lógica do inimigo, incluindo a transformação e o movimento."""
        if self.is_transforming:
            current_time = pygame.time.get_ticks()
            
            self.health += self.heal_amount_per_second / FPS
            if self.health > self.max_health: self.health = self.max_health

            self.flash_timer += 1
            self.show_image = self.flash_timer % 10 >= 5

            if current_time - self.transformation_start_time > 3000:
                self.finish_transformation()
            return # Para qualquer outra lógica enquanto se transforma

        # --- 2. LÓGICA DE ATIVAÇÃO E EXECUÇÃO DO COMBO DE SKILL ---
        current_time = pygame.time.get_ticks()

        # Se for um chefe, não estiver se transformando ou já castando...
        if self.is_boss and not self.is_transforming and not self.is_casting:
            # ...e o cooldown principal acabou, inicia o combo.
            if current_time - self.last_skill_time > self.skill_cooldown:
                self.is_casting = True
                self.cast_count = 0
                self.last_cast_time = current_time # Inicia o timer para o primeiro cast

        # Se estiver no meio do combo...
        if self.is_casting:
            # ...verifica se é hora de castar o próximo ataque.
            if self.cast_count < 3 and current_time - self.last_cast_time > self.time_between_casts:
                self.use_ground_slam(enemy_projectiles, self.assets)
                self.cast_count += 1
                self.last_cast_time = current_time
            
            # Se já fez os 3 ataques, termina o combo e inicia o cooldown principal.
            elif self.cast_count >= 3:
                self.is_casting = False
                self.last_skill_time = current_time
            
            
            # Fica parado enquanto estiver castando
            return

        # --- 3. LÓGICA DE MOVIMENTO (SÓ EXECUTA SE NÃO ESTIVER CASTANDO) ---
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            dx /= distance; dy /= distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        self.hitbox.center = self.rect.center


        


    def draw(self, screen, offset=[0, 0]):
        image_to_draw = self.image
        
        # Aplica o efeito visual de flash de dano
        if self.is_flashing:
            flash_image = self.image.copy()
            flash_image.fill((200, 200, 200), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = flash_image
        # CORREÇÃO: Aplica o efeito visual de lentidão (congelado)
        elif self.is_slowed:
            slow_image = self.image.copy()
            # Usa um filtro azul claro para o efeito de gelo
            slow_image.fill((100, 100, 255), special_flags=pygame.BLEND_RGB_ADD)
            image_to_draw = slow_image
        
        if self.show_image:
            screen.blit(image_to_draw, (self.rect.x + offset[0], self.rect.y + offset[1]))
        
        self.draw_health_bar(screen, offset)


    def draw_health_bar(self, screen, offset=[0, 0]):
        """Desenha a barra de vida na posição correta, considerando o offset."""
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.rect.width * 0.8
            bar_height = 5
            # Aplica o offset à posição da barra
            bar_x = self.rect.centerx - (bar_width / 2) + offset[0]
            bar_y = self.rect.bottom + 5 + offset[1]
            
            pygame.draw.rect(screen, (180, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
