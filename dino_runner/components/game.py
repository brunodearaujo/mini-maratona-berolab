# Ficheiro: dino_runner/components/game.py
# Autor: [O Seu Nome]
# Descrição: Classe principal que gereia os estados do jogo (Menu, Jogo, Game Over)
# e a transição entre os diferentes modos de jogo.

import pygame
from dino_runner.components.modes.endless_runner import EndlessRunner
from dino_runner.components.modes.roguelite_mode import RogueliteMode
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS
from dino_runner.utils.asset_manager import AssetManager
from dino_runner.utils.sound_manager import SoundManager
from dino_runner.utils.text_utils import draw_message_component

class GameController:
    """
    Controla o fluxo geral do jogo, incluindo o menu principal,
    a seleção de modos e o ecrã de opções.
    """
    def __init__(self):
        """Inicializa o Pygame, a tela, os gestores e as configurações."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Configurações do jogo que podem ser alteradas pelo jogador
        self.settings = {"music": True, "sfx": True, "shake": True}
        
        # Gestores de recursos
        self.assets = AssetManager()
        self.sounds = SoundManager(self.settings)
        
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(self.assets.get_image("ICON"))
        self.clock = pygame.time.Clock()
        
        # Variáveis de estado do jogo
        self.running = True
        self.game_state = "MENU"
        self.game_mode_instance = None
        self.game_mode_type = "NORMAL"
        
        # Pontuações e recordes
        self.high_score_normal = 0
        self.high_score_roguelite = 0
        self.load_high_scores()

        # Assets específicos do menu
        self.menu_dino_image = pygame.transform.scale(self.assets.get_image("DINO_START"), (120, 120))
        self.option_button_rects = {}

    def execute(self):
        """Inicia e mantém o loop principal do jogo."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Máquina de estados principal
            if self.game_state == "RUNNING":
                self.run_gameplay(events)
            elif self.game_state == "MENU":
                self.show_menu(events)
            elif self.game_state == "GAME_OVER":
                if self.game_mode_type == "NORMAL":
                    self.show_game_over_screen(events)
                else:
                    self.game_state = "MENU"

            pygame.display.update()
            self.clock.tick(FPS)
        
        pygame.quit()

    def run_gameplay(self, events):
        """Gereia a criação e execução do modo de jogo selecionado."""
        if not self.game_mode_instance:
            self.sounds.stop_music()
            
            if self.game_mode_type == "NORMAL":
                self.sounds.play_music("normal_theme.mp3")
                self.game_mode_instance = EndlessRunner(self.screen, self.high_score_normal, self.assets, self.sounds, self.settings)
            elif self.game_mode_type == "ROGUELITE":
                self.sounds.play_music("roguelite_theme.mp3")
                self.game_mode_instance = RogueliteMode(self.screen, self.high_score_roguelite, self.assets, self.sounds, self.settings)

        run_result = self.game_mode_instance.run(events)

        if not run_result or run_result == "MENU":
            self.sounds.stop_music()
            self.update_and_save_highscore()
            
            if run_result == "MENU":
                self.game_state = "MENU"
            else:
                self.game_state = "GAME_OVER"
            

    def show_menu(self, events):
        """Desenha e gerencia o menu"""
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.menu_dino_image, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 250))
        draw_message_component("Dino Runner", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        
        normal_button = draw_message_component("Normal Mode", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        roguelite_button = draw_message_component("Roguelite Mode", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)

        self.draw_options_buttons()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if normal_button.collidepoint(event.pos):
                    # CORREÇÃO: Garante um estado limpo antes de iniciar.
                    self.game_mode_instance = None
                    self.game_mode_type = "NORMAL"
                    self.game_state = "RUNNING"
                elif roguelite_button.collidepoint(event.pos):
                    # CORREÇÃO: Garante um estado limpo antes de iniciar.
                    self.game_mode_instance = None
                    self.game_mode_type = "ROGUELITE"
                    self.game_state = "RUNNING"
                
                for option, rect in self.option_button_rects.items():
                    if rect.collidepoint(event.pos):
                        self.settings[option] = not self.settings[option]
                        if option == 'music' and not self.settings['music']:
                            self.sounds.stop_music()

    def draw_options_buttons(self):
        """Desenha os botões de opções (Música, SFX, Shake)."""
        options = ["music", "sfx", "shake"]
        start_x = SCREEN_WIDTH - 150
        start_y = SCREEN_HEIGHT - 120
        
        for i, option in enumerate(options):
            y_pos = start_y + (i * 40)
            is_on = self.settings[option]
            
            text = f"{option.upper()}: {'ON' if is_on else 'OFF'}"
            color = (0, 150, 0) if is_on else (150, 0, 0)
            
            button_rect = draw_message_component(text, self.screen, pos_x_center=start_x, pos_y_center=y_pos, bg_color=color, return_rect=True)
            self.option_button_rects[option] = button_rect

    def show_game_over_screen(self, events):
        """Desenha o ecrã de Game Over para o modo Normal."""
        if self.game_mode_instance:
            self.game_mode_instance.draw()

        score_text = f"Sua Pontuacao: {self.last_score:05d}"
        draw_message_component("GAME OVER", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        draw_message_component(score_text, self.screen, font_size=30, pos_y_center=SCREEN_HEIGHT // 2 - 50)
        
        retry_button_rect = draw_message_component("Jogar Novamente", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        menu_button_rect = draw_message_component("Menu Principal", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button_rect.collidepoint(event.pos):
                    # A instância só é apagada AQUI, após o clique.
                    self.game_mode_instance = None
                    self.game_state = "RUNNING"
                elif menu_button_rect.collidepoint(event.pos):
                    # A instância só é apagada AQUI, após o clique.
                    self.game_mode_instance = None
                    self.game_state = "MENU"

    def update_and_save_highscore(self):
        """Verifica e salva o novo recorde para o modo de jogo atual."""
        if self.game_mode_type == "NORMAL":
            # Guarda a pontuação final antes que a instância seja apagada
            self.last_score = self.game_mode_instance.score
            if self.last_score > self.high_score_normal:
                self.high_score_normal = self.last_score
                self.save_high_score("NORMAL")
        elif self.game_mode_type == "ROGUELITE":
            if self.game_mode_instance.score > self.high_score_roguelite:
                self.high_score_roguelite = self.game_mode_instance.score
                self.save_high_score("ROGUELITE")

    def load_high_scores(self):
        """Carrega os recordes de ficheiros de texto."""
        try:
            with open("highscore_normal.txt", "r") as f:
                self.high_score_normal = int(f.read())
        except (FileNotFoundError, ValueError): self.high_score_normal = 0
        try:
            with open("highscore_roguelite.txt", "r") as f:
                self.high_score_roguelite = int(f.read())
        except (FileNotFoundError, ValueError): self.high_score_roguelite = 0
    
    def save_high_score(self, mode):
        """Salva o recorde num ficheiro de texto."""
        if mode == "NORMAL":
            filename, score = "highscore_normal.txt", self.high_score_normal
        elif mode == "ROGUELITE":
            filename, score = "highscore_roguelite.txt", self.high_score_roguelite
        else: return
            
        with open(filename, "w") as f:
            f.write(str(score))
