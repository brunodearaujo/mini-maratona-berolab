import pygame
import random
import math
from dino_runner.components.dinos.roguelite_dino import RogueliteDino
from dino_runner.components.enemies.zumbi import Zumbi
from dino_runner.components.weapons.bullet import Bullet
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class RogueliteMode:
    def __init__(self, screen, high_score):
        self.screen = screen
        self.high_score = high_score
        self.running = True
        self.player = RogueliteDino()

        # Fontes
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Atributos do jogo
        self.current_wave = 0
        self.wave_in_progress = False
        self.enemies = []
        self.projectiles = []
        self.start_wave_button_rect = None

        # Atributos de combate
        self.last_attack_time = 0
        self.attack_cooldown = 300 # em milissegundos

        # Atributos de estado e power-ups
        self.game_state = "RUNNING" # Estados: RUNNING, LEVEL_UP, GAME_OVER
        self.powerup_options = []
        self.powerup_card_rects = []
        self.define_powerups()

    def define_powerups(self):
        """Define a lista de todos os power-ups possíveis no jogo."""
        self.powerup_pool = [
            {'name': 'Dano Aumentado', 'desc': '+10 de dano para as balas', 'effect': self.increase_damage},
            {'name': 'Cadência de Tiro', 'desc': 'Atire 25% mais rápido', 'effect': self.increase_fire_rate},
            {'name': 'Bala Perfurante', 'desc': 'Sua bala atravessa +1 inimigo', 'effect': self.increase_pierce},
            {'name': 'Vida Máxima', 'desc': '+20 de Vida Máxima', 'effect': self.increase_max_health},
        ]

    # --- Funções de Efeito dos Power-ups ---
    def increase_damage(self): Bullet.BASE_DAMAGE += 10
    def increase_fire_rate(self): self.attack_cooldown = int(self.attack_cooldown * 0.75)
    def increase_pierce(self): Bullet.BASE_PIERCE += 1
    def increase_max_health(self): 
        self.player.max_health += 20
        self.player.health += 20

    def trigger_level_up_screen(self):
        """Pausa o jogo e prepara as opções de power-up."""
        self.game_state = "LEVEL_UP"
        self.powerup_options = random.sample(self.powerup_pool, 3)
        print("Jogo pausado para escolha de Power-up.")

    def run(self, events):
        """O loop principal agora é uma máquina de estados."""
        self.handle_events(events)
        if self.game_state == "RUNNING":
            self.update()
        self.draw()
        return self.running

    def handle_events(self, events):
        """Processa os inputs do jogador de forma organizada."""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False; pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            
            # Lógica de clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Botão esquerdo
                    if self.game_state == "RUNNING":
                        self.attempt_attack()
                    elif self.game_state == "LEVEL_UP":
                        # Verifica clique nas cartas de power-up
                        for i, rect in enumerate(self.powerup_card_rects):
                            if rect.collidepoint(event.pos):
                                selected_powerup = self.powerup_options[i]
                                print(f"Power-up selecionado: {selected_powerup['name']}")
                                selected_powerup['effect']()
                                self.game_state = "RUNNING"
                                break
                
                # Verifica clique no botão de iniciar wave (qualquer botão do mouse)
                if not self.wave_in_progress and self.start_wave_button_rect:
                    if self.start_wave_button_rect.collidepoint(event.pos):
                        self.start_next_wave()

    def attempt_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            mouse_pos = pygame.mouse.get_pos()
            player_pos = self.player.rect.center
            direction = pygame.math.Vector2(mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]).normalize()
            self.projectiles.append(Bullet(player_pos[0], player_pos[1], direction))

    def start_next_wave(self):
        self.current_wave += 1
        self.wave_in_progress = True
        print(f"--- Iniciando Wave {self.current_wave} ---")
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

    def update(self):
        """Atualiza a lógica de todos os elementos do jogo."""
        self.player.update()
        
        # --- ATUALIZAÇÃO E COLISÃO DE INIMIGOS COM O JOGADOR ---
        for enemy in self.enemies:
            enemy.update(self.player)
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(0.5)

        # --- ATUALIZAÇÃO E COLISÃO DE PROJÉTEIS ---
        for proj in self.projectiles[:]:
            proj.update()

            if not self.screen.get_rect().colliderect(proj.rect):
                self.projectiles.remove(proj)
                continue

            # LOOP ANINHADO CORRETO: Para cada projétil, verificamos cada inimigo
            for enemy in self.enemies[:]:
                if enemy.rect.colliderect(proj.rect):
                    if enemy.take_damage(proj.damage):
                        if self.player.gain_exp(enemy.exp_value):
                            self.trigger_level_up_screen()
                        self.enemies.remove(enemy)
                    
                    proj.pierce -= 1
                    if proj.pierce <= 0:
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        break
        
        # A wave termina quando não há mais inimigos
        if self.wave_in_progress and not self.enemies:
            print(f"Wave {self.current_wave} concluída!")
            self.wave_in_progress = False
            self.projectiles.clear()

    def draw(self):
        """Desenha tudo na tela."""
        self.screen.fill((128, 128, 128))
        
        self.player.draw(self.screen)
        pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect, 2)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
            pygame.draw.rect(self.screen, (0, 0, 255), enemy.rect, 2)
            
        for proj in self.projectiles:
            proj.draw(self.screen)
            pygame.draw.rect(self.screen, (255, 255, 0), proj.rect, 2)
        
        if not self.wave_in_progress:
            text = f"Iniciar Próxima Wave ({self.current_wave + 1})"
            button_text = self.font.render(text, True, (255, 255, 255))
            button_rect = button_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            button_bg_rect = button_rect.inflate(20, 20)
            pygame.draw.rect(self.screen, (20, 80, 20), button_bg_rect, border_radius=10)
            self.screen.blit(button_text, button_rect)
            self.start_wave_button_rect = button_bg_rect
        else:
            self.start_wave_button_rect = None
            
        self.draw_ui()

        if self.game_state == "LEVEL_UP":
            self.draw_level_up_screen()
            
    def draw_ui(self):
        # ... (código existente da draw_ui)
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
        wave_rect = wave_text.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        self.screen.blit(wave_text, wave_rect)

    def draw_level_up_screen(self):
        # ... (código existente da draw_level_up_screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        title_text = self.font.render("Subiu de Nível! Escolha um Power-up:", True, (255, 255, 0))
        self.screen.blit(title_text, title_text.get_rect(centerx=SCREEN_WIDTH/2, y=50))
        self.powerup_card_rects.clear()
        card_width, card_height = 250, 150
        total_width = (card_width * 3) + 100
        start_x = (SCREEN_WIDTH - total_width) / 2
        for i, powerup in enumerate(self.powerup_options):
            card_x = start_x + (i * (card_width + 50))
            card_y = SCREEN_HEIGHT / 2 - (card_height / 2)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            self.powerup_card_rects.append(card_rect)
            pygame.draw.rect(self.screen, (30, 30, 80), card_rect, border_radius=15)
            pygame.draw.rect(self.screen, (200, 200, 255), card_rect, 3, 15)
            name_text = self.font.render(powerup['name'], True, (255, 255, 255))
            desc_text = self.small_font.render(powerup['desc'], True, (200, 200, 200))
            self.screen.blit(name_text, name_text.get_rect(centerx=card_rect.centerx, y=card_y + 20))
            self.screen.blit(desc_text, desc_text.get_rect(centerx=card_rect.centerx, y=card_y + 70))