import pygame
import random
import math
from dino_runner.components.dinos.roguelite_dino import RogueliteDino
from dino_runner.components.enemies.zumbi import Zumbi
from dino_runner.components.weapons.bullet import Bullet
from dino_runner.components.weapons.projectile import Projectile
from dino_runner.components.weapons.pistol import Pistol
from dino_runner.components.weapons.sword import Sword
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class RogueliteMode:
    def __init__(self, screen, high_score):
        self.screen = screen
        self.initial_high_score = high_score
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.stats_font = pygame.font.Font(None, 24)
        self.reset()

    def reset(self):
        """Reseta o estado do jogo para uma nova partida."""
        print("Iniciando/Resetando o modo Roguelite...")
        self.running = True
        self.player = RogueliteDino()
        self.current_wave = 0
        self.wave_in_progress = False
        self.enemies = []
        self.projectiles = []
        self.game_state = "CHOOSE_WEAPON"
        self.score = 0
        self.high_score = self.initial_high_score
        
        self.start_wave_button_rect = None
        self.confirm_button_rect = None
        self.game_over_buttons = {}
        self.pause_buttons = {}
        self.powerup_card_rects = []
        self.powerup_options = []
        self.selected_option_index = None

        self.define_powerups()
        self.class_options = [
            {'name': 'Pistoleiro', 'desc': 'Ataques a longa distância.', 'id': 'pistol'},
            {'name': 'Espadachim', 'desc': 'Mais rápido e resistente.', 'id': 'sword'}
        ]

    def define_powerups(self):
        self.powerup_pool = [
            {'name': 'Dano Aumentado', 'desc': '+10 de dano', 'effect': self.increase_damage},
            {'name': 'Cadência de Tiro', 'desc': 'Atire 25% mais rápido', 'effect': self.increase_fire_rate},
            {'name': 'Bala Perfurante', 'desc': '+1 perfuração', 'effect': self.increase_pierce},
            {'name': 'Vida Máxima', 'desc': '+20 de Vida Máxima', 'effect': self.increase_max_health},
            {'name': 'Roubo de Vida', 'desc': '+1% do dano convertido em vida', 'effect': self.increase_life_steal},
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
            self.player.speed = 5
            self.player.max_health = 100
        elif class_id == 'sword':
            self.player.set_weapon(Sword(self.player))
            self.player.speed = 7
            self.player.max_health = 120
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
                if self.game_state == "CHOOSE_WEAPON":
                    self.handle_card_selection(pos, self.class_options, self.select_class)
                elif self.game_state == "LEVEL_UP":
                    self.handle_card_selection(pos, self.powerup_options, self.apply_powerup)
                elif self.game_state == "GAME_OVER":
                    if 'restart' in self.game_over_buttons and self.game_over_buttons['restart'].collidepoint(pos): self.reset()
                    if 'menu' in self.game_over_buttons and self.game_over_buttons['menu'].collidepoint(pos): self.running = False
                elif self.game_state == "PAUSED":
                    if 'resume' in self.pause_buttons and self.pause_buttons['resume'].collidepoint(pos): self.game_state = "RUNNING"
                    if 'restart' in self.pause_buttons and self.pause_buttons['restart'].collidepoint(pos): self.reset()
                    if 'menu' in self.pause_buttons and self.pause_buttons['menu'].collidepoint(pos): self.running = False
                elif self.game_state == "RUNNING" and not self.wave_in_progress and self.start_wave_button_rect:
                    if self.start_wave_button_rect.collidepoint(pos): self.start_next_wave()

    def handle_card_selection(self, pos, options, on_confirm_action):
        for i, rect in enumerate(self.powerup_card_rects):
            if rect.collidepoint(pos):
                self.selected_option_index = i
                return

        if self.confirm_button_rect and self.confirm_button_rect.collidepoint(pos):
            if self.selected_option_index is not None:
                if self.game_state == "CHOOSE_WEAPON":
                    on_confirm_action(options[self.selected_option_index]['id'])
                else: # LEVEL_UP
                    on_confirm_action(self.selected_option_index)
                self.selected_option_index = None

    def apply_powerup(self, index):
        self.powerup_options[index]['effect']()
        self.game_state = "RUNNING"

    def update(self):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: self.player_attack_logic()

        self.player.update()
        
        for enemy in self.enemies:
            enemy.update(self.player)
            if self.player.rect.colliderect(enemy.rect):
                if self.player.take_damage(0.5):
                    self.set_game_over(); return

        for proj in self.projectiles[:]:
            proj.update()
            if not self.screen.get_rect().colliderect(proj.rect):
                self.projectiles.remove(proj); continue
            for enemy in self.enemies[:]:
                if enemy.rect.colliderect(proj.rect):
                    damage_dealt = proj.damage
                    self.player.heal(damage_dealt * self.player.life_steal_percent)
                    if enemy.take_damage(damage_dealt):
                        self.score += enemy.max_health
                        if self.player.gain_exp(enemy.exp_value): self.trigger_level_up()
                        if enemy in self.enemies: self.enemies.remove(enemy)
                    proj.pierce -= 1
                    if proj.pierce <= 0:
                        if proj in self.projectiles: self.projectiles.remove(proj)
                        break
        
        if self.wave_in_progress and not self.enemies:
            self.wave_in_progress = False
            self.projectiles.clear()
            
    def set_game_over(self):
        self.game_state = "GAME_OVER"
        if self.score > self.high_score:
            self.high_score = self.score
        print(f"Game Over! Pontuação final: {self.score}")

    def draw(self):
        self.screen.fill((128, 128, 128))
        if self.game_state != "CHOOSE_WEAPON":
            self.player.draw(self.screen)
            pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect, 2)
            for enemy in self.enemies: enemy.draw(self.screen)
            for proj in self.projectiles: 
                proj.draw(self.screen)
                pygame.draw.rect(self.screen, (255, 255, 0), proj.rect, 2)
            if self.player.weapon and isinstance(self.player.weapon, Sword): self.player.weapon.draw(self.screen)
            if self.game_state == "RUNNING" and not self.wave_in_progress: self.draw_start_wave_button()
            self.draw_ui()

        if self.game_state == "CHOOSE_WEAPON": self.draw_class_choice_screen()
        elif self.game_state == "LEVEL_UP": self.draw_level_up_screen()
        elif self.game_state == "PAUSED": self.draw_pause_screen()
        elif self.game_state == "GAME_OVER": self.draw_game_over_screen()

    def draw_start_wave_button(self):
        button_text = self.font.render(f"Iniciar Próxima Wave ({self.current_wave + 1})", True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.start_wave_button_rect = self.draw_button(button_text, button_rect, (20, 80, 20))

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        stats_bg_rect = pygame.Rect(50, 100, 300, 400)
        pygame.draw.rect(self.screen, (20, 20, 50), stats_bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 255), stats_bg_rect, 3, 15)
        title = self.font.render("STATUS", True, (255, 255, 0))
        self.screen.blit(title, title.get_rect(centerx=stats_bg_rect.centerx, y=120))
        
        stats_to_show = {
            "Nível": self.player.level,
            "Vida": f"{int(self.player.health)} / {self.player.max_health}",
            "Velocidade": self.player.speed,
            "Dano da Arma": getattr(self.player.weapon, 'damage', 'N/A') if self.player.weapon else 'N/A',
            "Cadência (ms)": getattr(self.player.weapon, 'attack_cooldown', 'N/A') if self.player.weapon else 'N/A',
            "Roubo de Vida": f"{self.player.life_steal_percent * 100:.1f}%"
        }
        
        y_offset = 180
        for name, value in stats_to_show.items():
            line_text = self.stats_font.render(f"{name}: {value}", True, (255, 255, 255))
            self.screen.blit(line_text, (stats_bg_rect.x + 20, y_offset))
            y_offset += 30

        title_text = self.font.render("JOGO PAUSADO", True, (255, 255, 0))
        self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH / 2 + 150, y=180))

        resume_text = self.small_font.render("Retomar (ESC)", True, (255, 255, 255))
        restart_text = self.small_font.render("Reiniciar Partida", True, (255, 255, 255))
        menu_text = self.small_font.render("Menu Principal", True, (255, 255, 255))
        
        center_x_buttons = SCREEN_WIDTH / 2 + 150
        self.pause_buttons['resume'] = self.draw_button(resume_text, resume_text.get_rect(center=(center_x_buttons, 280)), (0, 150, 0))
        self.pause_buttons['restart'] = self.draw_button(restart_text, restart_text.get_rect(center=(center_x_buttons, 340)), (150, 150, 0))
        # CORREÇÃO APLICADA AQUI:
        self.pause_buttons['menu'] = self.draw_button(menu_text, menu_text.get_rect(center=(center_x_buttons, 400)), (150, 0, 0))

    def draw_button(self, text_surf, text_rect, bg_color):
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=10)
        self.screen.blit(text_surf, text_rect)
        return bg_rect

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=150))
        
        score_text = self.font.render(f"Pontuação: {self.score}", True, (255, 255, 255))
        highscore_text = self.small_font.render(f"Recorde: {self.high_score}", True, (200, 200, 200))
        self.screen.blit(score_text, score_text.get_rect(centerx=SCREEN_WIDTH/2, y=220))
        self.screen.blit(highscore_text, highscore_text.get_rect(centerx=SCREEN_WIDTH/2, y=270))

        restart_text = self.small_font.render("Jogar Novamente", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, 350))
        self.game_over_buttons['restart'] = self.draw_button(restart_text, restart_rect, (0, 150, 0))

        menu_text = self.small_font.render("Voltar ao Menu", True, (255, 255, 255))
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH/2, 410))
        self.game_over_buttons['menu'] = self.draw_button(menu_text, menu_rect, (150, 0, 0))

    def draw_class_choice_screen(self):
        self.draw_card_screen("Escolha sua Classe Inicial", self.class_options)

    def draw_level_up_screen(self):
        self.draw_card_screen("Subiu de Nível! Escolha um Power-up:", self.powerup_options)

    def draw_card_screen(self, title, options):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        title_text = self.font.render(title, True, (255, 255, 0))
        self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=100))
        
        self.powerup_card_rects.clear()
        num_cards = len(options)
        card_width, card_height = 250, 180
        total_width = (card_width * num_cards) + (50 * (num_cards - 1))
        start_x = (SCREEN_WIDTH - total_width) / 2
        card_y = SCREEN_HEIGHT / 2 - (card_height / 2)

        for i, option in enumerate(options):
            card_x = start_x + (i * (card_width + 50))
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.powerup_card_rects.append(card_rect)
            
            pygame.draw.rect(self.screen, (30, 30, 80), card_rect, border_radius=15)
            pygame.draw.rect(self.screen, (200, 200, 255), card_rect, 3, 15)
            
            name_text = self.font.render(option['name'], True, (255, 255, 255))
            desc_text = self.small_font.render(option['desc'], True, (200, 200, 200))
            self.screen.blit(name_text, name_text.get_rect(centerx=card_rect.centerx, y=card_y + 40))
            self.screen.blit(desc_text, desc_text.get_rect(centerx=card_rect.centerx, y=card_y + 90))
        
        if self.selected_option_index is not None:
            selected_rect = self.powerup_card_rects[self.selected_option_index]
            pygame.draw.rect(self.screen, (255, 255, 0), selected_rect, 4, 15)

            confirm_text = self.font.render("Confirmar", True, (255, 255, 255))
            confirm_rect = confirm_text.get_rect(centerx=SCREEN_WIDTH / 2, y=card_y + card_height + 40)
            self.confirm_button_rect = self.draw_button(confirm_text, confirm_rect, (0, 150, 0))
        else:
            self.confirm_button_rect = None

    def draw_ui(self):
        hp_text = self.font.render("HP", True, (255, 255, 255))
        self.screen.blit(hp_text, (10, 10))
        health_ratio = self.player.health / self.player.max_health
        hp_bar_rect_bg = pygame.Rect(60, 10, 200, 25)
        hp_bar_rect_fg = pygame.Rect(60, 10, 200 * health_ratio, 25)
        pygame.draw.rect(self.screen, (180, 0, 0), hp_bar_rect_bg)
        pygame.draw.rect(self.screen, (0, 200, 0), hp_bar_rect_fg)

        exp_text = self.font.render("EXP", True, (255, 255, 255))
        self.screen.blit(exp_text, (10, 45))
        exp_ratio = self.player.exp / self.player.exp_to_next_level
        exp_bar_rect_bg = pygame.Rect(60, 45, 200, 25)
        exp_bar_rect_fg = pygame.Rect(60, 45, 200 * exp_ratio, 25)
        pygame.draw.rect(self.screen, (50, 50, 50), exp_bar_rect_bg)
        pygame.draw.rect(self.screen, (50, 150, 255), exp_bar_rect_fg)

        wave_text = self.font.render(f"Wave: {self.current_wave}", True, (255, 255, 255))
        self.screen.blit(wave_text, wave_text.get_rect(topright=(SCREEN_WIDTH - 20, 10)))
        
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, score_text.get_rect(topright=(SCREEN_WIDTH - 20, 50)))

    def player_attack_logic(self):
        attack_result = self.player.attack()
        if not attack_result: return
        
        if isinstance(attack_result, Projectile):
            self.projectiles.append(attack_result)
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
        self.current_wave += 1
        self.wave_in_progress = True
        self.spawn_enemies_for_wave()
    
    def spawn_enemies_for_wave(self):
        self.enemies.clear()
        num_enemies = 2 + self.current_wave 
        for _ in range(num_enemies):
            edge = random.choice(['left', 'right', 'top'])
            if edge == 'left': x, y = -50, random.randint(0, SCREEN_HEIGHT)
            elif edge == 'right': x, y = SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)
            else: x, y = random.randint(0, SCREEN_WIDTH), -50
            self.enemies.append(Zumbi(x, y))
