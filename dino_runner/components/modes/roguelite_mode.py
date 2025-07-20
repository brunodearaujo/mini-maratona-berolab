# Ficheiro: dino_runner/components/modes/roguelite_mode.py
# Autor: Bero
# Descrição: Gereia toda a lógica, estados e elementos do modo de jogo Roguelite.
#            É a classe central que orquestra o jogador, inimigos, power-ups e a interface.

import pygame
import random
import math
from dino_runner.components.dinos.roguelite_dino import RogueliteDino
from dino_runner.components.enemies.bero_run.bero import Bero
from dino_runner.components.enemies.dino_run.cacto1 import Cacto1
from dino_runner.components.enemies.bero_run.miguel import Miguel
from dino_runner.components.enemies.dino_run.cacto2 import Cacto2
from dino_runner.components.enemies.bero_run.pam import Pam
from dino_runner.components.enemies.dino_run.cacto3 import Cacto3
from dino_runner.components.enemies.bero_run.dann import Dann
from dino_runner.components.enemies.dino_run.bird1 import Bird1
from dino_runner.components.enemies.bero_run.teki import Teki
from dino_runner.components.enemies.dino_run.bird2 import Bird2
from dino_runner.components.weapons.bullet import Bullet
from dino_runner.components.weapons.projectile import Projectile
from dino_runner.components.weapons.enemy_projectile import EnemyProjectile
from dino_runner.components.weapons.pistol import Pistol
from dino_runner.components.weapons.sword import Sword
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# --- Classes Auxiliares para Feedback Visual ---

class DamageNumber(pygame.sprite.Sprite):
    """Representa um número de dano flutuante que aparece no ecrã."""
    def __init__(self, x, y, damage, font):
        super().__init__()
        display_damage = max(1, int(damage))
        self.image = font.render(str(display_damage), True, (255, 255, 0)) # Amarelo para dano causado
        self.rect = self.image.get_rect(center=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.duration = 500 # Meio segundo de vida
        self.y_velocity = -2 # Sobe lentamente

    def update(self):
        """Move o número para cima e remove-o após a sua duração."""
        self.rect.y += self.y_velocity
        if pygame.time.get_ticks() - self.creation_time > self.duration:
            self.kill()

class PlayerDamageNumber(DamageNumber):
    """Um número de dano específico para quando o jogador é atingido, com cor vermelha."""
    def __init__(self, x, y, damage, font):
        super().__init__(x, y, damage, font)
        display_damage = max(1, int(damage))
        self.image = font.render(str(display_damage), True, (255, 50, 50))

class HealNumber(DamageNumber):
    """Um número flutuante para feedback de cura, com cor verde."""
    def __init__(self, x, y, amount, font):
        super().__init__(x, y, amount, font)
        display_amount = max(1, int(amount))
        self.image = font.render(str(display_amount), True, (50, 255, 50))

# --- Classe Principal do Modo de Jogo ---

class RogueliteMode:
    """
    Controla todo o ciclo de jogo do modo Roguelite, incluindo a máquina de estados,
    a gestão de entidades, a interface do utilizador e a lógica de progressão.
    """
    def __init__(self, screen, high_score, assets, sounds, settings):
        """Inicializa o modo de jogo, carregando assets e definindo o estado inicial."""
        self.screen = screen
        self.initial_high_score = high_score
        self.assets = assets
        self.sounds = sounds
        self.settings = settings
        
        # Carrega as fontes necessárias do AssetManager
        self.title_font = self.assets.get_font("title")
        self.body_font = self.assets.get_font("body")
        self.ui_font = self.assets.get_font("ui")
        self.stats_font = self.assets.get_font("stats")
        
        self.reset()

    def reset(self):
        """Reseta todas as variáveis para iniciar uma nova partida."""
        self.running = True
        self.player = RogueliteDino(self.assets, self.sounds)
        
        self.current_wave = 0
        self.wave_in_progress = False
        self.enemies, self.projectiles, self.enemy_projectiles = [], [], []
        self.game_state = "CHOOSE_WEAPON"
        self.score = 0
        if not hasattr(self, 'high_score') or self.initial_high_score > self.high_score:
            self.high_score = self.initial_high_score
        
        self.damage_numbers = pygame.sprite.Group()
        self.screen_shake = 0
        self.shake_duration = 15
        
        # Dicionários para os retângulos de botões clicáveis
        self.start_wave_button_rect, self.confirm_button_rect = None, None
        self.game_over_buttons, self.pause_buttons = {}, {}
        self.powerup_card_rects, self.powerup_options = [], []
        self.selected_option_index = None
        
        # Temporizadores
        self.last_boss_heal_feedback_time = 0
        self.last_player_hit_sound_time = 0
        self.player_hit_sound_cooldown = 500
        self.pause_start_time = 0

        self.define_powerups()
        self.define_enemy_pools()
        self.class_options = [
            {'name': 'Mage', 'desc': 'atira METEOROS.', 'id': 'pistol'},
            {'name': 'Warrior', 'desc': 'BERO MODE ???', 'id': 'sword'}
        ]

    def define_enemy_pools(self):
        """Define os grupos de inimigos para cada classe e os seus respetivos chefes."""
        self.pistol_enemies = [Cacto1, Cacto2, Bird1, Bird2, Cacto3]
        self.pistol_boss = Cacto3
        self.sword_enemies = [Bero, Miguel, Pam, Dann, Teki]
        self.sword_boss = Bero

    def define_powerups(self):
        """Define todos os power-ups disponíveis, separados por tipo."""
        self.powerup_pool = [
            {'name': 'Dano Aumentado', 'desc': '+5 de dano', 'effect': self.increase_damage},
            {'name': 'Cadencia de Tiro', 'desc': '+10 atkspeed', 'effect': self.increase_fire_rate},
            {'name': 'Vida Maxima', 'desc': '+20 max hp', 'effect': self.increase_max_health},
            {'name': 'Roubo de Vida', 'desc': '+1% lifesteal', 'effect': self.increase_life_steal},
            {'name': 'Quantidade de Ataques', 'desc': '+1 atk p/hit', 'effect': self.increase_quantity},
        ]
        self.mage_powerups = [
            {'name': 'Bala Perfurante', 'desc': '+1 piercing', 'effect': self.increase_pierce},
            {'name': 'Velocidade de Projetil', 'desc': '+15% proj. speed', 'effect': self.increase_bullet_speed},
            {'name': 'Ricochete', 'desc': '+1 bounce', 'effect': self.increase_bounces},
        ]
        self.warrior_powerups = [
            {'name': 'Alcance Aumentado', 'desc': '+20% atk size', 'effect': self.increase_sword_size},
        ]
    
    # --- Métodos de Efeito dos Power-ups ---
    def increase_quantity(self): self.player.shot_quantity += 1
    def increase_pierce(self): Bullet.BASE_PIERCE += 1
    def increase_bullet_speed(self): Bullet.BASE_SPEED *= 1.15
    def increase_bounces(self): Bullet.BASE_BOUNCES += 1
    def increase_sword_size(self):
        if isinstance(self.player.weapon, Sword): self.player.weapon.size += 0.2
    def increase_damage(self):
        if isinstance(self.player.weapon, Pistol): Bullet.BASE_DAMAGE += 5
        elif isinstance(self.player.weapon, Sword): self.player.weapon.damage += 8
    def increase_fire_rate(self):
        if self.player.weapon: self.player.weapon.attack_cooldown = int(self.player.weapon.attack_cooldown * 0.90)
    def increase_max_health(self): 
        self.player.max_health += 20; self.player.health += 20
    def increase_life_steal(self):
        self.player.life_steal_percent += 0.01

    def trigger_level_up(self):
        """Pausa o jogo e prepara as opções de power-up para o jogador escolher."""
        self.game_state = "LEVEL_UP"
        self.pause_start_time = pygame.time.get_ticks()
        
        current_pool = self.powerup_pool[:]
        if isinstance(self.player.weapon, Pistol):
            current_pool.extend(self.mage_powerups)
        elif isinstance(self.player.weapon, Sword):
            current_pool.extend(self.warrior_powerups)
        
        num_samples = min(3, len(current_pool))
        self.powerup_options = random.sample(current_pool, num_samples) if num_samples > 0 else []
        self.selected_option_index = None

    def select_class(self, class_id):
        """Equipa a classe escolhida no jogador, definindo a sua arma e status iniciais."""
        if class_id == 'pistol': # Classe Mage
            self.player.set_weapon(Pistol(self.player))
            self.player.weapon.attack_cooldown = 650
            self.player.set_character("DINO_START", "DINO_RUNNING")
            self.player.speed = 5
            self.player.max_health = 100
        elif class_id == 'sword': # Classe Warrior
            self.player.set_weapon(Sword(self.player))
            self.player.set_character("BERO_START", "BERO_RUNNING")
            self.player.speed = 7
            self.player.max_health = 150
        
        self.player.health = self.player.max_health
        self.game_state = "RUNNING"

    def apply_powerup(self, index):
        """Aplica o efeito do power-up escolhido e despausa o jogo."""
        paused_duration = pygame.time.get_ticks() - self.pause_start_time
        self.player.last_special_ability_time += paused_duration
        
        self.powerup_options[index]['effect']()
        self.game_state = "RUNNING"
        self.selected_option_index = None

    def run(self, events):
        """O loop principal do modo de jogo, chamado a cada frame pelo GameController."""
        self.handle_events(events)
        if self.game_state == "RUNNING":
            self.update()
        self.draw()
        return self.running

    def handle_events(self, events):
        """Processa todos os inputs do jogador com base no estado atual do jogo."""
        for event in events:
            if event.type == pygame.QUIT: self.running = False; pygame.quit(); exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.game_state == "RUNNING":
                    self.game_state = "PAUSED"
                    self.pause_start_time = pygame.time.get_ticks()
                elif self.game_state == "PAUSED":
                    paused_duration = pygame.time.get_ticks() - self.pause_start_time
                    self.player.last_special_ability_time += paused_duration
                    self.game_state = "RUNNING"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == 3 and self.game_state == "RUNNING":
                    self.player.use_special_ability()
                
                if self.game_state in ["CHOOSE_WEAPON", "LEVEL_UP"]:
                    self.handle_card_selection(pos)
                elif self.game_state == "GAME_OVER":
                    if 'restart' in self.game_over_buttons and self.game_over_buttons['restart'].collidepoint(pos): self.reset()
                    if 'menu' in self.game_over_buttons and self.game_over_buttons['menu'].collidepoint(pos): self.running = "MENU"
                elif self.game_state == "PAUSED":
                    if 'resume' in self.pause_buttons and self.pause_buttons['resume'].collidepoint(pos): self.game_state = "RUNNING"
                    if 'restart' in self.pause_buttons and self.pause_buttons['restart'].collidepoint(pos): self.reset()
                    if 'menu' in self.pause_buttons and self.pause_buttons['menu'].collidepoint(pos): self.running = "MENU"
                elif self.game_state == "RUNNING" and not self.wave_in_progress and self.start_wave_button_rect:
                    if self.start_wave_button_rect.collidepoint(pos): self.start_next_wave()

    def handle_card_selection(self, pos):
        """Gereia a lógica de clique para as telas de escolha com cartas."""
        options = self.class_options if self.game_state == "CHOOSE_WEAPON" else self.powerup_options
        for i, rect in enumerate(self.powerup_card_rects):
            if rect.collidepoint(pos):
                self.selected_option_index = i; return

        if self.confirm_button_rect and self.confirm_button_rect.collidepoint(pos) and self.selected_option_index is not None:
            if self.game_state == "CHOOSE_WEAPON": self.select_class(options[self.selected_option_index]['id'])
            else: self.apply_powerup(self.selected_option_index)

    def update(self):
        """Atualiza a lógica de todos os elementos do jogo a cada frame."""
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.game_state == "RUNNING":
            self.player.attack()

        attack_result = self.player.update()
        if attack_result:
            if isinstance(attack_result, tuple) and attack_result[0] == "BULLET":
                _, x, y, direction, is_frozen = attack_result
                self.projectiles.append(Bullet(x, y, direction, self.assets, is_frozen))
        
        if self.player.weapon and isinstance(self.player.weapon, Sword) and self.player.weapon.is_swinging:
            sword_hitbox = self.player.weapon.hitbox
            if sword_hitbox:
                for enemy in self.enemies[:]:
                    if enemy not in self.player.weapon.hit_enemies and sword_hitbox.colliderect(enemy.hitbox):
                        self.player.weapon.hit_enemies.add(enemy)
                        damage_dealt = self.player.weapon.damage
                        self.damage_numbers.add(DamageNumber(enemy.rect.centerx, enemy.rect.top, damage_dealt, self.ui_font))
                        heal_amount = damage_dealt * self.player.life_steal_percent
                        if heal_amount >= 1:
                            self.player.heal(heal_amount)
                            self.damage_numbers.add(HealNumber(self.player.rect.centerx, self.player.rect.top, heal_amount, self.ui_font))
                        if enemy.take_damage(damage_dealt):
                            self.handle_enemy_death(enemy)

        for enemy in self.enemies:
            enemy.update(self.player, self.enemy_projectiles)
            if self.player.hitbox.colliderect(enemy.hitbox):
                damage_taken = 1
                current_time = pygame.time.get_ticks()
                if current_time - self.last_player_hit_sound_time > self.player_hit_sound_cooldown:
                    self.sounds.play("player_hit")
                    self.last_player_hit_sound_time = current_time
                if self.player.take_damage(damage_taken):
                    self.set_game_over(); return
                self.damage_numbers.add(PlayerDamageNumber(self.player.rect.centerx, self.player.rect.top, damage_taken, self.ui_font))

        for proj in self.projectiles[:]:
            proj.update()
            if not self.screen.get_rect().colliderect(proj.rect):
                self.projectiles.remove(proj); continue
            for enemy in self.enemies[:]:
                if enemy.hitbox.colliderect(proj.hitbox):
                    if proj.is_frozen:
                        enemy.apply_slow(0.75, 2000)
                    damage_dealt = proj.damage
                    self.damage_numbers.add(DamageNumber(enemy.rect.centerx, enemy.rect.top, damage_dealt, self.ui_font))
                    heal_amount = damage_dealt * self.player.life_steal_percent
                    if heal_amount >= 1:
                        self.player.heal(heal_amount)
                        self.damage_numbers.add(HealNumber(self.player.rect.centerx, self.player.rect.top, heal_amount, self.ui_font))
                    if enemy.take_damage(damage_dealt):
                        self.handle_enemy_death(enemy)
                    proj.pierce -= 1
                    if proj.pierce <= 0:
                        if proj.bounces_left > 0:
                            proj.bounces_left -= 1
                            proj.pierce = 1
                            next_target = self.find_next_bounce_target(proj.rect.center, enemy)
                            if next_target:
                                new_dir = pygame.math.Vector2(next_target.rect.centerx - proj.rect.centerx, next_target.rect.centery - proj.rect.centery).normalize()
                                proj.direction = new_dir
                            else:
                                if proj in self.projectiles: self.projectiles.remove(proj)
                        else:
                            if proj in self.projectiles: self.projectiles.remove(proj)
                        break

        for proj in self.enemy_projectiles[:]:
            proj.update()
            if not self.screen.get_rect().colliderect(proj.rect):
                self.enemy_projectiles.remove(proj); continue
            if self.player.hitbox.colliderect(proj.hitbox):
                damage_taken = proj.damage
                current_time = pygame.time.get_ticks()
                if current_time - self.last_player_hit_sound_time > self.player_hit_sound_cooldown:
                    self.sounds.play("player_hit")
                    self.last_player_hit_sound_time = current_time
                if self.player.take_damage(damage_taken):
                    self.set_game_over()
                if self.settings['shake']:
                    self.screen_shake = self.shake_duration
                self.damage_numbers.add(PlayerDamageNumber(self.player.rect.centerx, self.player.rect.top, damage_taken, self.ui_font))
                self.enemy_projectiles.remove(proj)

        self.damage_numbers.update()
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        if self.wave_in_progress and not self.enemies:
            self.wave_in_progress = False
            self.projectiles.clear()
            self.enemy_projectiles.clear()
            
    def find_next_bounce_target(self, current_pos, last_hit_enemy):
        """Encontra o inimigo mais próximo para o projétil ricochetear."""
        closest_enemy = None
        min_dist = float('inf')
        for enemy in self.enemies:
            if enemy is not last_hit_enemy:
                dist = pygame.math.Vector2(enemy.rect.center).distance_to(current_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy
        return closest_enemy

    def handle_enemy_death(self, enemy):
        """Gereia a lógica de quando um inimigo é derrotado (score, exp, recompensa)."""
        self.score += enemy.max_health
        if self.player.gain_exp(enemy.exp_value):
            self.trigger_level_up()
        if enemy.is_boss:
            print("CHEFE DERROTADO! Recompensa: +5 de Velocidade!")
            self.player.speed += 5
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
    def set_game_over(self):
        """Ativa o estado de Game Over e atualiza o recorde."""
        self.game_state = "GAME_OVER"
        if self.score > self.high_score: self.high_score = self.score
        print(f"Game Over! Pontuação final: {self.score}")

    def draw(self):
        """Desenha todos os elementos no ecrã com base no estado do jogo."""
        render_offset = [0, 0]
        if self.screen_shake > 0 and self.game_state == "RUNNING":
            render_offset[0] = random.randint(-5, 5)
            render_offset[1] = random.randint(-5, 5)

        if self.game_state != "CHOOSE_WEAPON":
            self.screen.fill((128, 128, 128))
            self.player.draw(self.screen, render_offset)
            for enemy in self.enemies: enemy.draw(self.screen, render_offset)
            for proj in self.projectiles: proj.draw(self.screen, render_offset)
            for proj in self.enemy_projectiles: proj.draw(self.screen, render_offset)
            if self.player.weapon and isinstance(self.player.weapon, Sword):
                self.player.weapon.draw(self.screen, render_offset)
            for number in self.damage_numbers:
                self.screen.blit(number.image, (number.rect.x + render_offset[0], number.rect.y + render_offset[1]))
            self.draw_ui()

        if self.game_state == "RUNNING" and not self.wave_in_progress:
            self.draw_start_wave_button()
        
        if self.game_state == "CHOOSE_WEAPON":
            self.screen.fill((128, 128, 128))
            self.draw_class_choice_screen()
        elif self.game_state == "LEVEL_UP":
            self.draw_level_up_screen()
        elif self.game_state == "PAUSED":
            self.draw_pause_screen()
        elif self.game_state == "GAME_OVER":
            self.draw_game_over_screen()

    def draw_start_wave_button(self):
        """Desenha o botão para iniciar a próxima onda."""
        button_text = self.title_font.render(f"Iniciar Wave ({self.current_wave + 1})", True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.start_wave_button_rect = self.draw_button(button_text, button_rect, (20, 80, 20))

    def draw_pause_screen(self):
        """Desenha o menu de pausa, incluindo o painel de status."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        stats_bg_rect = pygame.Rect(50, 100, 350, 400)
        pygame.draw.rect(self.screen, (20, 20, 50), stats_bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 255), stats_bg_rect, 3, 15)
        
        title = self.title_font.render("STATUS", True, (255, 255, 0))
        self.screen.blit(title, title.get_rect(centerx=stats_bg_rect.centerx, y=120))
        
        stats_to_show = {
            "Classe": self.player.weapon.__class__.__name__ if self.player.weapon else "Nenhuma",
            "Nível": self.player.level,
            "Velocidade": self.player.speed,
            "Vida Máxima": self.player.max_health,
            "Roubo de Vida": f"{self.player.life_steal_percent * 100:.0f}%"
        }
        
        if isinstance(self.player.weapon, Pistol):
            stats_to_show["Dano do Tiro"] = Bullet.BASE_DAMAGE
            stats_to_show["Perfuração"] = Bullet.BASE_PIERCE
            attacks_per_sec = 1000 / self.player.weapon.attack_cooldown if self.player.weapon.attack_cooldown > 0 else float('inf')
            stats_to_show["Ataques por Seg"] = f"{attacks_per_sec:.2f}"
        elif isinstance(self.player.weapon, Sword):
            stats_to_show["Dano da Espada"] = self.player.weapon.damage
            attacks_per_sec = 1000 / self.player.weapon.attack_cooldown if self.player.weapon.attack_cooldown > 0 else float('inf')
            stats_to_show["Ataques por Seg"] = f"{attacks_per_sec:.2f}"
        
        y_offset = 180
        for name, value in stats_to_show.items():
            line_text = self.stats_font.render(f"{name}: {value}", True, (255, 255, 255))
            self.screen.blit(line_text, (stats_bg_rect.x + 20, y_offset))
            y_offset += 30

        title_text = self.title_font.render("JOGO PAUSADO", True, (255, 255, 0))
        self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH / 2 + 200, y=180))

        resume_text = self.body_font.render("Retomar (ESC)", True, (255, 255, 255))
        restart_text = self.body_font.render("Reiniciar Partida", True, (255, 255, 255))
        menu_text = self.body_font.render("Menu Principal", True, (255, 255, 255))
        
        center_x_buttons = SCREEN_WIDTH / 2 + 200
        resume_rect = resume_text.get_rect(center=(center_x_buttons, 280))
        restart_rect = restart_text.get_rect(center=(center_x_buttons, 340))
        menu_rect = menu_text.get_rect(center=(center_x_buttons, 400))
        
        self.pause_buttons['resume'] = self.draw_button(resume_text, resume_rect, (0, 150, 0))
        self.pause_buttons['restart'] = self.draw_button(restart_text, restart_rect, (150, 150, 0))
        self.pause_buttons['menu'] = self.draw_button(menu_text, menu_rect, (150, 0, 0))

    def draw_button(self, text_surf, text_rect, bg_color):
        """Função auxiliar para desenhar botões com fundo."""
        bg_rect = text_rect.inflate(20, 10); pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=10); self.screen.blit(text_surf, text_rect); return bg_rect

    def draw_game_over_screen(self):
        """Desenha o ecrã de Fim de Jogo."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); self.screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("GAME OVER", True, (255, 0, 0)); self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=150))
        score_text = self.title_font.render(f"Pontuacao: {self.score}", True, (255, 255, 255)); highscore_text = self.body_font.render(f"Recorde: {self.high_score}", True, (200, 200, 200))
        self.screen.blit(score_text, score_text.get_rect(centerx=SCREEN_WIDTH/2, y=220)); self.screen.blit(highscore_text, highscore_text.get_rect(centerx=SCREEN_WIDTH/2, y=270))
        restart_text = self.body_font.render("Jogar Novamente", True, (255, 255, 255)); restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, 350)); self.game_over_buttons['restart'] = self.draw_button(restart_text, restart_rect, (0, 150, 0))
        menu_text = self.body_font.render("Voltar ao Menu", True, (255, 255, 255)); menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH/2, 410)); self.game_over_buttons['menu'] = self.draw_button(menu_text, menu_rect, (150, 0, 0))

    def draw_class_choice_screen(self):
        """Chama a função genérica para desenhar a tela de escolha de classe."""
        self.draw_card_screen("Escolha sua Classe", self.class_options)

    def draw_level_up_screen(self):
        """Chama a função genérica para desenhar a tela de subida de nível."""
        self.draw_card_screen("Escolha um Power-up", self.powerup_options)

    def draw_card_screen(self, title, options):
        """Função genérica para desenhar telas com cartas de escolha."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0, 0))
        title_text = self.title_font.render(title, True, (255, 255, 0)); self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=100))
        
        self.powerup_card_rects.clear(); num_cards = len(options); card_width, card_height = 280, 200
        total_width = (card_width * num_cards) + (50 * (num_cards - 1)); start_x = (SCREEN_WIDTH - total_width) / 2
        card_y = SCREEN_HEIGHT / 2 - (card_height / 2)

        for i, option in enumerate(options):
            card_x = start_x + (i * (card_width + 50)); card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.powerup_card_rects.append(card_rect)
            pygame.draw.rect(self.screen, (30, 30, 80), card_rect, border_radius=15); pygame.draw.rect(self.screen, (200, 200, 255), card_rect, 3, 15)
            name_text = self.body_font.render(option['name'], True, (255, 255, 255));desc_text = self.ui_font.render(option['desc'], True, (200, 200, 200))
            self.screen.blit(name_text, name_text.get_rect(centerx=card_rect.centerx, y=card_y + 40)); self.screen.blit(desc_text, desc_text.get_rect(centerx=card_rect.centerx, y=card_y + 110))
        
        if self.selected_option_index is not None:
            selected_rect = self.powerup_card_rects[self.selected_option_index]; pygame.draw.rect(self.screen, (255, 255, 0), selected_rect, 4, 15)
            confirm_text = self.title_font.render("Confirmar", True, (255, 255, 255)); confirm_rect = confirm_text.get_rect(centerx=SCREEN_WIDTH / 2, y=card_y + card_height + 40)
            self.confirm_button_rect = self.draw_button(confirm_text, confirm_rect, (0, 150, 0))
        else: self.confirm_button_rect = None

    def draw_ui(self):
        """Desenha a interface do jogador (barras de vida, exp, cooldown e pontuação)."""
        hp_bar_rect_bg = pygame.Rect(10, 10, 200, 25)
        health_ratio = self.player.health / self.player.max_health if self.player.max_health > 0 else 0
        hp_bar_rect_fg = pygame.Rect(10, 10, 200 * health_ratio, 25)
        pygame.draw.rect(self.screen, (180, 0, 0), hp_bar_rect_bg); pygame.draw.rect(self.screen, (0, 200, 0), hp_bar_rect_fg)
        hp_text = self.ui_font.render(f"HP: {int(self.player.health)}/{self.player.max_health}", True, (255, 255, 255)); self.screen.blit(hp_text, hp_text.get_rect(center=hp_bar_rect_bg.center))
        
        exp_bar_rect_bg = pygame.Rect(10, 40, 200, 25)
        exp_ratio = self.player.exp / self.player.exp_to_next_level if self.player.exp_to_next_level > 0 else 0
        exp_bar_rect_fg = pygame.Rect(10, 40, 200 * exp_ratio, 25)
        pygame.draw.rect(self.screen, (50, 50, 50), exp_bar_rect_bg); pygame.draw.rect(self.screen, (50, 150, 255), exp_bar_rect_fg)
        exp_text = self.ui_font.render(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", True, (255, 255, 255)); self.screen.blit(exp_text, exp_text.get_rect(center=exp_bar_rect_bg.center))
        
        skill_bar_bg = pygame.Rect(10, 70, 200, 20)
        elapsed_time = pygame.time.get_ticks() - self.player.last_special_ability_time
        cooldown_ratio = min(1.0, elapsed_time / self.player.special_ability_cooldown)
        skill_bar_fg = pygame.Rect(10, 70, 200 * cooldown_ratio, 20)
        pygame.draw.rect(self.screen, (80, 80, 80), skill_bar_bg); pygame.draw.rect(self.screen, (255, 215, 0), skill_bar_fg)
        if cooldown_ratio < 1.0:
            remaining_seconds = (self.player.special_ability_cooldown - elapsed_time) / 1000
            skill_text = self.ui_font.render(f"Skill: {remaining_seconds:.1f}s", True, (0, 0, 0))
        else:
            skill_text = self.ui_font.render("Skill: PRONTO!", True, (0, 0, 0))
        self.screen.blit(skill_text, skill_text.get_rect(center=skill_bar_bg.center))

        wave_text = self.ui_font.render(f"Wave: {self.current_wave}", True, (255, 255, 255)); score_text = self.ui_font.render(f"Score: {self.score}", True, (255, 255, 255)); highscore_text = self.ui_font.render(f"Recorde: {self.high_score}", True, (255, 255, 0))
        self.screen.blit(wave_text, wave_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))); self.screen.blit(score_text, score_text.get_rect(topright=(SCREEN_WIDTH - 10, 30))); self.screen.blit(highscore_text, highscore_text.get_rect(topright=(SCREEN_WIDTH - 10, 50)))

    def start_next_wave(self):
        self.current_wave += 1; self.wave_in_progress = True; self.spawn_enemies_for_wave()
    
    def spawn_enemies_for_wave(self):
        """Cria os inimigos para a wave atual com estrutura progressiva."""
        self.enemies.clear()
        enemy_pool = self.sword_enemies if isinstance(self.player.weapon, Sword) else self.pistol_enemies
        boss_class = self.sword_boss if isinstance(self.player.weapon, Sword) else self.pistol_boss

        if self.current_wave == 10:
            self.enemies.append(boss_class(SCREEN_WIDTH / 2, -100, self.assets, is_boss=True)); return

        num_enemies = 3 + self.current_wave
        enemy_class_to_spawn = None
        if 1 <= self.current_wave <= 5:
            enemy_index = self.current_wave - 1
            if enemy_index < len(enemy_pool):
                enemy_class_to_spawn = enemy_pool[enemy_index]
        
        for _ in range(num_enemies):
            chosen_class = enemy_class_to_spawn or random.choice(enemy_pool)
            edge = random.choice(['left', 'right', 'top', 'bottom'])
            if edge == 'left': x, y = random.randint(-150, -50), random.randint(0, SCREEN_HEIGHT)
            elif edge == 'right': x, y = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 150), random.randint(0, SCREEN_HEIGHT)
            elif edge == 'top': x, y = random.randint(0, SCREEN_WIDTH), random.randint(-150, -50)
            else: x, y = random.randint(0, SCREEN_WIDTH), random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 150)
            self.enemies.append(chosen_class(x, y, self.assets))
