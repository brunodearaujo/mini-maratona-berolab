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


class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, font):
        super().__init__()
        self.image = font.render(str(int(damage)), True, (255, 255, 0)) # Texto amarelo
        self.rect = self.image.get_rect(center=(x, y))
        self.creation_time = pygame.time.get_ticks()
        self.duration = 500 # Meio segundo de vida
        self.y_velocity = -2 # Sobe lentamente

    def update(self):
        self.rect.y += self.y_velocity
        if pygame.time.get_ticks() - self.creation_time > self.duration:
            self.kill() # Remove o sprite do grupo quando o tempo acabar

class PlayerDamageNumber(DamageNumber):
    def __init__(self, x, y, damage, font):
        super().__init__(x, y, damage, font)
        # Usa a cor vermelha para o dano recebido
        self.image = font.render(str(int(damage)), True, (255, 50, 50))

# --- NOVA CLASSE PARA NÚMEROS DE CURA ---
class HealNumber(DamageNumber):
    def __init__(self, x, y, amount, font):
        super().__init__(x, y, amount, font)
        display_amount = max(1, int(amount))
        self.image = font.render(str(display_amount), True, (50, 255, 50)) # Verde para cura


class RogueliteMode:
    def __init__(self, screen, high_score, assets):
        self.screen = screen
        self.initial_high_score = high_score
        self.assets = assets # Armazena o AssetManager
        
        # Pega as fontes do AssetManager
        self.title_font = self.assets.get_font("title")
        self.body_font = self.assets.get_font("body")
        self.ui_font = self.assets.get_font("ui")
        self.stats_font = self.assets.get_font("stats")
        
        self.reset()

    def reset(self):
        self.running = True
        self.player = RogueliteDino(self.assets)
        self.current_wave = 9
        self.wave_in_progress = False
        self.enemies, self.projectiles, self.enemy_projectiles = [], [], []
        self.game_state = "CHOOSE_WEAPON"
        self.score = 0
        if not hasattr(self, 'high_score') or self.initial_high_score > self.high_score:
            self.high_score = self.initial_high_score
        self.damage_numbers = pygame.sprite.Group()
        self.screen_shake = 0
        self.shake_duration = 15
        self.start_wave_button_rect, self.confirm_button_rect = None, None
        self.game_over_buttons, self.pause_buttons = {}, {}
        self.powerup_card_rects, self.powerup_options = [], []
        self.selected_option_index = None
        
        # CORREÇÃO: Atributo para controlar o feedback de cura do chefe inicializado aqui
        self.last_boss_heal_feedback_time = 0

        self.define_powerups()
        self.define_enemy_pools()
        self.class_options = [
            {'name': 'Pistoleiro', 'desc': 'Ataques a longa distância.', 'id': 'pistol'},
            {'name': 'Espadachim', 'desc': 'Mais rápido e resistente.', 'id': 'sword'}
        ]
    def define_enemy_pools(self):
        """Define os inimigos para cada classe e seus chefes."""
        self.pistol_enemies = [Cacto1, Cacto2, Cacto3, Bird1, Bird2]
        self.pistol_boss = Cacto3
        self.sword_enemies = [Bero, Miguel, Pam, Dann, Teki]
        self.sword_boss = Bero

    def define_powerups(self):
        self.powerup_pool = [
            {'name': 'Dano Aumentado', 'desc': '+10 de dano', 'effect': self.increase_damage},
            {'name': 'Cadencia de Tiro', 'desc': 'Atire 25% mais rapido', 'effect': self.increase_fire_rate},
            {'name': 'Bala Perfurante', 'desc': '+1 perfuracao', 'effect': self.increase_pierce},
            {'name': 'Vida Maxima', 'desc': '+20 de Vida Maxima', 'effect': self.increase_max_health},
            {'name': 'Roubo de Vida', 'desc': '+1% do dano em vida', 'effect': self.increase_life_steal},
        ]

    def increase_damage(self):
        if isinstance(self.player.weapon, Pistol): Bullet.BASE_DAMAGE += 10
        elif isinstance(self.player.weapon, Sword): self.player.weapon.damage += 15

    def increase_fire_rate(self):
        if self.player.weapon: self.player.weapon.attack_cooldown = int(self.player.weapon.attack_cooldown * 0.75)

    def increase_pierce(self):
        if isinstance(self.player.weapon, Pistol): Bullet.BASE_PIERCE += 1
        
    def increase_max_health(self): 
        self.player.max_health += 20
        self.player.health += 20
    
    def increase_life_steal(self):
        self.player.life_steal_percent += 0.01

    def trigger_level_up(self):
        self.game_state = "LEVEL_UP"
        self.powerup_options = random.sample(self.powerup_pool, 3)
        self.selected_option_index = None
        print(f"Jogo pausado. Estado: {self.game_state}")

    def select_class(self, class_id):
        if class_id == 'pistol':
            self.player.set_weapon(Pistol(self.player))
            # Define a aparência do Dino
            self.player.set_character("DINO_START", "DINO_RUNNING")
            self.player.speed = 5
            self.player.max_health = 100
        elif class_id == 'sword':
            self.player.set_weapon(Sword(self.player))
            # Define a aparência do Bero
            self.player.set_character("BERO_START", "BERO_RUNNING")
            self.player.speed = 7
            self.player.max_health = 200
        self.player.health = self.player.max_health
        self.game_state = "RUNNING"
        print(f"Classe {class_id} selecionada!")

    def run(self, events):
        self.handle_events(events)
        if self.game_state == "RUNNING":
            self.update()
        self.draw()
        return self.running

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: self.running = False; pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.game_state == "RUNNING": self.game_state = "PAUSED"
                elif self.game_state == "PAUSED": self.game_state = "RUNNING"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
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
        options = self.class_options if self.game_state == "CHOOSE_WEAPON" else self.powerup_options
        for i, rect in enumerate(self.powerup_card_rects):
            if rect.collidepoint(pos):
                self.selected_option_index = i; return

        if self.confirm_button_rect and self.confirm_button_rect.collidepoint(pos) and self.selected_option_index is not None:
            if self.game_state == "CHOOSE_WEAPON": self.select_class(options[self.selected_option_index]['id'])
            else: self.apply_powerup(self.selected_option_index)


    def apply_powerup(self, index):
        self.powerup_options[index]['effect']()
        self.game_state = "RUNNING"

    def update(self):
        """Atualiza a lógica de todos os elementos do jogo com as correções."""
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.player_attack_logic()
        self.player.update()
        
        # Atualiza inimigos e verifica colisão
        for enemy in self.enemies:
            enemy.update(self.player, self.enemy_projectiles)
            if self.player.rect.colliderect(enemy.rect):
                damage_taken = 1
                if self.player.take_damage(damage_taken):
                    self.set_game_over()
                    self.screen_shake = self.shake_duration
                    return
                self.damage_numbers.add(PlayerDamageNumber(self.player.rect.centerx, self.player.rect.top, damage_taken, self.ui_font))
            
            # Adiciona feedback de cura para o chefe com temporizador
            if enemy.is_boss and enemy.is_transforming:
                current_time = pygame.time.get_ticks()
                # Mostra um número de cura a cada 250ms (meio meio segundo)
                if current_time - self.last_boss_heal_feedback_time > 250:
                    self.last_boss_heal_feedback_time = current_time
                    # Calcula a cura total nesse intervalo de tempo
                    heal_amount_interval = enemy.heal_amount_per_second * 0.5 
                    self.damage_numbers.add(HealNumber(enemy.rect.centerx, enemy.rect.top, heal_amount_interval, self.ui_font))

        # Atualiza projéteis do jogador e cria números de dano/cura
        for proj in self.projectiles[:]:
            proj.update()
            if not self.screen.get_rect().colliderect(proj.rect):
                self.projectiles.remove(proj)
                continue
            
            for enemy in self.enemies[:]:
                if enemy.rect.colliderect(proj.rect):
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
                        if proj in self.projectiles: self.projectiles.remove(proj)
                        break

        # Atualiza projéteis inimigos e ativa o screen shake
        for proj in self.enemy_projectiles[:]:
            proj.update()
            if not self.screen.get_rect().colliderect(proj.rect):
                self.enemy_projectiles.remove(proj)
                continue
            
            if self.player.rect.colliderect(proj.rect):
                damage_taken = proj.damage
                if self.player.take_damage(damage_taken):
                    self.set_game_over()
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
            
    def player_attack_logic(self):
        attack_result = self.player.attack()
        if not attack_result: return
        
        if isinstance(attack_result, tuple) and attack_result[0] == "BULLET":
            _, x, y, direction = attack_result
            self.projectiles.append(Bullet(x, y, direction, self.assets))
        
        elif isinstance(self.player.weapon, Sword) and self.player.weapon.is_swinging:
            sword_hitbox = self.player.weapon.hitbox
            if sword_hitbox:
                for enemy in self.enemies[:]:
                    if sword_hitbox.colliderect(enemy.rect):
                        damage_dealt = self.player.weapon.damage
                        self.damage_numbers.add(DamageNumber(enemy.rect.centerx, enemy.rect.top, damage_dealt, self.ui_font))
                        
                        # Adiciona feedback de cura para o jogador
                        heal_amount = damage_dealt * self.player.life_steal_percent
                        if heal_amount >= 1:
                            self.player.heal(heal_amount)
                            self.damage_numbers.add(HealNumber(self.player.rect.centerx, self.player.rect.top, heal_amount, self.ui_font))

                        if enemy.take_damage(damage_dealt):
                            self.handle_enemy_death(enemy)

    def handle_enemy_death(self, enemy):
        """Lida com a lógica de quando um inimigo é derrotado."""
        self.score += enemy.max_health
        if self.player.gain_exp(enemy.exp_value):
            self.trigger_level_up()
        if enemy.is_boss:
            print("CHEFE DERROTADO! Recompensa: +5 de Velocidade!")
            self.player.speed += 5
        if enemy in self.enemies:
            self.enemies.remove(enemy)

            
    def set_game_over(self):
        self.game_state = "GAME_OVER"
        if self.score > self.high_score: self.high_score = self.score
        print(f"Game Over! Pontuação final: {self.score}")

    def draw(self):
        """Desenha tudo na tela com a lógica de hitboxes corrigida."""
        render_offset = [0, 0]
        if self.screen_shake > 0 and self.game_state == "RUNNING":
            render_offset[0] = random.randint(-5, 5)
            render_offset[1] = random.randint(-5, 5)

        if self.game_state != "CHOOSE_WEAPON":
            self.screen.fill((128, 128, 128))
            self.player.draw(self.screen, render_offset)
            
            # --- GARANTIA DE TODAS AS HITBOXES ---
            pygame.draw.rect(self.screen, (0, 255, 0), self.player.rect.move(render_offset), 2)
            
            for enemy in self.enemies: 
                enemy.draw(self.screen, render_offset)
                pygame.draw.rect(self.screen, (255, 0, 0), enemy.rect.move(render_offset), 2)

            for proj in self.projectiles: 
                proj.draw(self.screen, render_offset)
                pygame.draw.rect(self.screen, (255, 255, 0), proj.rect.move(render_offset), 2)
            
            for proj in self.enemy_projectiles:
                proj.draw(self.screen, render_offset)
                pygame.draw.rect(self.screen, (255, 0, 255), proj.rect.move(render_offset), 2)
            
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
        button_text = self.title_font.render(f"Iniciar Wave ({self.current_wave + 1})", True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.start_wave_button_rect = self.draw_button(button_text, button_rect, (20, 80, 20))


    def draw_pause_screen(self):
        """Desenha a tela de pausa com os status do jogador."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # --- PAINEL DE STATUS ---
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
        # CORREÇÃO APLICADA AQUI: mudamos 'stats' para 'stats_to_show'
        for name, value in stats_to_show.items():
            line_text = self.stats_font.render(f"{name}: {value}", True, (255, 255, 255))
            self.screen.blit(line_text, (stats_bg_rect.x + 20, y_offset))
            y_offset += 30

        # --- BOTÕES DE PAUSA ---
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
        bg_rect = text_rect.inflate(20, 10); pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=10); self.screen.blit(text_surf, text_rect); return bg_rect


    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); self.screen.blit(overlay, (0, 0))
        title_text = self.title_font.render("GAME OVER", True, (255, 0, 0)); self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=150))
        score_text = self.title_font.render(f"Pontuacao: {self.score}", True, (255, 255, 255)); highscore_text = self.body_font.render(f"Recorde: {self.high_score}", True, (200, 200, 200))
        self.screen.blit(score_text, score_text.get_rect(centerx=SCREEN_WIDTH/2, y=220)); self.screen.blit(highscore_text, highscore_text.get_rect(centerx=SCREEN_WIDTH/2, y=270))
        restart_text = self.body_font.render("Jogar Novamente", True, (255, 255, 255)); restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, 350)); self.game_over_buttons['restart'] = self.draw_button(restart_text, restart_rect, (0, 150, 0))
        menu_text = self.body_font.render("Voltar ao Menu", True, (255, 255, 255)); menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH/2, 410)); self.game_over_buttons['menu'] = self.draw_button(menu_text, menu_rect, (150, 0, 0))

    def draw_class_choice_screen(self): self.draw_card_screen("Escolha sua Classe", self.class_options)

    def draw_level_up_screen(self): self.draw_card_screen("Escolha um Power-up", self.powerup_options)


    def draw_card_screen(self, title, options):
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
        hp_bar_rect_bg = pygame.Rect(10, 10, 200, 25); health_ratio = self.player.health / self.player.max_health; hp_bar_rect_fg = pygame.Rect(10, 10, 200 * health_ratio, 25)
        pygame.draw.rect(self.screen, (180, 0, 0), hp_bar_rect_bg); pygame.draw.rect(self.screen, (0, 200, 0), hp_bar_rect_fg)
        hp_text = self.ui_font.render(f"HP: {int(self.player.health)}/{self.player.max_health}", True, (255, 255, 255)); self.screen.blit(hp_text, hp_text.get_rect(center=hp_bar_rect_bg.center))
        exp_bar_rect_bg = pygame.Rect(10, 40, 200, 25); exp_ratio = self.player.exp / self.player.exp_to_next_level; exp_bar_rect_fg = pygame.Rect(10, 40, 200 * exp_ratio, 25)
        pygame.draw.rect(self.screen, (50, 50, 50), exp_bar_rect_bg); pygame.draw.rect(self.screen, (50, 150, 255), exp_bar_rect_fg)
        exp_text = self.ui_font.render(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", True, (255, 255, 255)); self.screen.blit(exp_text, exp_text.get_rect(center=exp_bar_rect_bg.center))
        
        wave_text = self.ui_font.render(f"Wave: {self.current_wave}", True, (255, 255, 255)); score_text = self.ui_font.render(f"Score: {self.score}", True, (255, 255, 255)); highscore_text = self.ui_font.render(f"Recorde: {self.high_score}", True, (255, 255, 0))
        self.screen.blit(wave_text, wave_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))); self.screen.blit(score_text, score_text.get_rect(topright=(SCREEN_WIDTH - 10, 30))); self.screen.blit(highscore_text, highscore_text.get_rect(topright=(SCREEN_WIDTH - 10, 50)))

    def player_attack_logic(self):
        """Lógica de ataque unificada e corrigida."""
        attack_result = self.player.attack()
        if not attack_result: return

        # CORREÇÃO DA PISTOLA: Esta é a lógica correta que verifica a tupla.
        if isinstance(attack_result, tuple) and attack_result[0] == "BULLET":
            _, x, y, direction = attack_result
            self.projectiles.append(Bullet(x, y, direction, self.assets))
        
        elif isinstance(self.player.weapon, Sword) and self.player.weapon.is_swinging:
            sword_hitbox = self.player.weapon.hitbox
            if sword_hitbox:
                for enemy in self.enemies[:]:
                    if sword_hitbox.colliderect(enemy.rect):
                        damage_dealt = self.player.weapon.damage
                        self.player.heal(damage_dealt * self.player.life_steal_percent)
                        if enemy.take_damage(damage_dealt):
                            self.score += enemy.max_health
                            if self.player.gain_exp(enemy.exp_value):
                                self.trigger_level_up()
                            if enemy in self.enemies: self.enemies.remove(enemy)


    def start_next_wave(self):
        self.current_wave += 1; self.wave_in_progress = True; self.spawn_enemies_for_wave()
    
    def spawn_enemies_for_wave(self):
        """
        Cria os inimigos para a wave atual com estrutura progressiva e spawn distante.
        """
        self.enemies.clear()
        
        enemy_pool = self.sword_enemies if isinstance(self.player.weapon, Sword) else self.pistol_enemies
        boss_class = self.sword_boss if isinstance(self.player.weapon, Sword) else self.pistol_boss

        if self.current_wave == 10:
            print("!!! BOSS WAVE !!!")
            x = SCREEN_WIDTH / 2
            y = -100
            self.enemies.append(boss_class(x, y, self.assets, is_boss=True))
            return

        num_enemies = 3 + self.current_wave
        enemy_class_to_spawn = None

        # Define qual classe de inimigo usar
        if 1 <= self.current_wave <= 5:
            enemy_index = self.current_wave - 1
            if enemy_index < len(enemy_pool):
                enemy_class_to_spawn = enemy_pool[enemy_index]
                print(f"--- Wave de Introdução {self.current_wave}: Apenas {enemy_class_to_spawn.__name__} ---")
        
        # Se não for uma wave de introdução ou se o pool for menor que 5, usa inimigos aleatórios
        if not enemy_class_to_spawn:
            print(f"--- Wave Mista {self.current_wave}: Inimigos Aleatórios ---")
            # Deixamos enemy_class_to_spawn como None para que seja escolhido aleatoriamente dentro do loop

        # Loop de criação unificado
        for _ in range(num_enemies):
            # Se uma classe específica foi definida, usa-a. Senão, escolhe uma aleatória.
            chosen_class = enemy_class_to_spawn or random.choice(enemy_pool)
            
            edge = random.choice(['left', 'right', 'top', 'bottom'])
            
            # Lógica de spawn distante
            if edge == 'left':
                x = random.randint(-150, -50)
                y = random.randint(0, SCREEN_HEIGHT)
            elif edge == 'right':
                x = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 150)
                y = random.randint(0, SCREEN_HEIGHT)
            elif edge == 'top':
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(-150, -50)
            else: # bottom
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 150)
                
            self.enemies.append(chosen_class(x, y, self.assets))
