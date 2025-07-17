import pygame
import random
from dino_runner.components.dinos.roguelite_dino import RogueliteDino
# --- NOVOS IMPORTS ---
from dino_runner.components.enemies.zumbi import Zumbi
from dino_runner.utils.constants import SCREEN_WIDTH, FPS

class RogueliteMode:
    def __init__(self, screen, high_score):
        # ... (código existente em __init__)
        self.screen = screen
        self.high_score = high_score
        self.running = True
        self.player = RogueliteDino()
        self.font = pygame.font.Font(None, 36)
        self.current_wave = 0
        self.wave_in_progress = False
        self.enemies = []
        self.start_wave_button_rect = None

        # --- NOVOS ATRIBUTOS PARA O TIMER DA WAVE ---
        self.wave_duration = 10 * FPS # Duração da wave em frames (10 segundos)
        self.wave_timer = 0


    def handle_events(self, events):
        # ... (código existente)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.wave_in_progress and self.start_wave_button_rect:
                    if self.start_wave_button_rect.collidepoint(event.pos):
                        self.start_next_wave()


    def start_next_wave(self):
        self.current_wave += 1
        self.wave_in_progress = True
        self.wave_timer = 0 # Reseta o timer da wave
        print(f"--- Iniciando Wave {self.current_wave} (Duração: {self.wave_duration / FPS}s) ---")
        self.spawn_enemies_for_wave()


    def spawn_enemies_for_wave(self):
        """Cria os inimigos para a wave atual."""
        # Limpa a lista de inimigos da wave anterior
        self.enemies.clear()
        
        # A dificuldade aumenta a cada wave
        num_enemies = 2 + self.current_wave 

        for _ in range(num_enemies):
            # Spawna inimigos em posições aleatórias fora da tela
            edge = random.choice(['left', 'right', 'top'])
            if edge == 'left':
                x = -50
                y = random.randint(0, self.screen.get_height())
            elif edge == 'right':
                x = self.screen.get_width() + 50
                y = random.randint(0, self.screen.get_height())
            else: # top
                x = random.randint(0, self.screen.get_width())
                y = -50
            
            self.enemies.append(Zumbi(x, y))


    def update(self):
        self.player.update()
        
        if self.wave_in_progress:
            # Atualiza todos os inimigos
            for enemy in self.enemies:
                enemy.update(self.player)
                
                # Verifica colisão entre inimigo e jogador
                if self.player.rect.colliderect(enemy.rect):
                    self.player.take_damage(0.5) # Dano contínuo enquanto houver contato

            # Atualiza o timer da wave
            self.wave_timer += 1

            # Verifica se o tempo da wave acabou
            if self.wave_timer >= self.wave_duration:
                print(f"Wave {self.current_wave} concluída por tempo!")
                self.wave_in_progress = False
                self.enemies.clear() # Limpa os inimigos restantes


    def draw(self):
        self.screen.fill((128, 128, 128))
        self.player.draw(self.screen)
        
        # Desenha todos os inimigos
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # ... (código existente para desenhar o botão e a UI)
        if not self.wave_in_progress:
            text = f"Iniciar Próxima Wave ({self.current_wave + 1})"
            button_text = self.font.render(text, True, (255, 255, 255))
            button_rect = button_text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
            button_bg_rect = button_rect.inflate(20, 20)
            pygame.draw.rect(self.screen, (20, 80, 20), button_bg_rect, border_radius=10)
            self.screen.blit(button_text, button_rect)
            self.start_wave_button_rect = button_bg_rect
        else:
            self.start_wave_button_rect = None

        self.draw_ui()


    # ... (código existente de draw_ui e run)

    def draw_ui(self):
        # ... (seu código da draw_ui existente)
        # Nenhuma alteração necessária aqui
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
        wave_rect = wave_text.get_rect(topright=(self.screen.get_width() - 20, 10))
        self.screen.blit(wave_text, wave_rect)


    def run(self, events):
        """O loop principal que orquestra o modo de jogo."""
        self.handle_events(events)
        if self.running:
            self.update()
            self.draw()
        
        return self.running