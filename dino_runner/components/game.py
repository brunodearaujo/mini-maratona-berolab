# dino_runner/components/game.py

import pygame
from dino_runner.components.modes.endless_runner import EndlessRunner
from dino_runner.components.modes.roguelite_mode import RogueliteMode
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS
from dino_runner.utils.text_utils import draw_message_component
# 1. Importa o AssetManager
from dino_runner.utils.asset_manager import AssetManager

class GameController:
    # 2. O __init__ não recebe mais 'assets' como argumento
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 3. Cria a instância do AssetManager AQUI, depois de inicializar a tela
        self.assets = AssetManager()
        
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(self.assets.get_image("ICON"))
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.game_state = "MENU"
        self.game_mode_instance = None
        self.game_mode_type = "NORMAL"
        
        self.first_run = True
        self.high_score_normal = 0
        self.high_score_roguelite = 0
        self.last_score = 0
        self.load_high_scores()

        # 4. Usa a imagem correta do AssetManager
        self.menu_dino_image = pygame.transform.scale(self.assets.get_image("DINO_START"), (120, 120))

    def execute(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

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
        if not self.game_mode_instance:
            if self.game_mode_type == "NORMAL":
                # 5. Passa o AssetManager para os modos de jogo
                self.game_mode_instance = EndlessRunner(self.screen, self.high_score_normal, self.assets, self.first_run)
                self.first_run = False
            elif self.game_mode_type == "ROGUELITE":
                # 5. Passa o AssetManager para os modos de jogo
                self.game_mode_instance = RogueliteMode(self.screen, self.high_score_roguelite, self.assets)

        run_result = self.game_mode_instance.run(events)

        if not run_result or run_result == "MENU":
            if self.game_mode_type == "NORMAL":
                self.last_score = self.game_mode_instance.score
                if self.last_score > self.high_score_normal:
                    self.high_score_normal = self.last_score
                    self.save_high_score("NORMAL")
            elif self.game_mode_type == "ROGUELITE":
                if self.game_mode_instance.score > self.high_score_roguelite:
                    self.high_score_roguelite = self.game_mode_instance.score
                    self.save_high_score("ROGUELITE")
            
            if run_result == "MENU":
                self.game_state = "MENU"
                self.game_mode_instance = None
            else:
                self.game_state = "GAME_OVER"

    def show_menu(self, events):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.menu_dino_image, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 250))
        draw_message_component("Dino Runner", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        
        normal_button = draw_message_component("Normal Mode", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        roguelite_button = draw_message_component("Roguelite Mode", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if normal_button.collidepoint(event.pos):
                    self.game_mode_type = "NORMAL"
                    self.game_mode_instance = None
                    self.game_state = "RUNNING"
                elif roguelite_button.collidepoint(event.pos):
                    self.game_mode_type = "ROGUELITE"
                    self.game_mode_instance = None
                    self.game_state = "RUNNING"

    def show_game_over_screen(self, events):
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
                    self.game_mode_instance = None
                    self.game_state = "RUNNING"
                elif menu_button_rect.collidepoint(event.pos):
                    self.game_mode_instance = None
                    self.game_state = "MENU"

    def load_high_scores(self):
        try:
            with open("highscore_normal.txt", "r") as f:
                self.high_score_normal = int(f.read())
        except (FileNotFoundError, ValueError): self.high_score_normal = 0
        try:
            with open("highscore_roguelite.txt", "r") as f:
                self.high_score_roguelite = int(f.read())
        except (FileNotFoundError, ValueError): self.high_score_roguelite = 0
    
    def save_high_score(self, mode):
        if mode == "NORMAL":
            filename, score = "highscore_normal.txt", self.high_score_normal
        elif mode == "ROGUELITE":
            filename, score = "highscore_roguelite.txt", self.high_score_roguelite
        else: return
            
        with open(filename, "w") as f:
            f.write(str(score))
