# dino_runner/components/game.py

import pygame
from dino_runner.components.modes.endless_runner import EndlessRunner
from dino_runner.components.modes.roguelite_mode import RogueliteMode
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, ICON, FPS, RUNNING
from dino_runner.utils.text_utils import draw_message_component

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(ICON)
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.game_state = "MENU"
        self.game_mode_instance = None
        self.game_mode_type = "NORMAL"
        
        self.first_run = True
        self.high_score = 0
        self.last_score = 0
        self.load_high_score()

        self.menu_dino_image = pygame.transform.scale(RUNNING[0], (120, 120))

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
                self.show_game_over_screen(events)

            pygame.display.update()
            self.clock.tick(FPS)
        
        pygame.quit()

    def run_gameplay(self, events):
        # A lógica de criação da instância agora é mais flexível
        if not self.game_mode_instance:
            if self.game_mode_type == "NORMAL": # <-- 3. ALTERAR ESTA SEÇÃO
                self.game_mode_instance = EndlessRunner(self.screen, self.high_score, self.first_run)
                self.first_run = False
            elif self.game_mode_type == "ROGUELITE":
                self.game_mode_instance = RogueliteMode(self.screen, self.high_score)

        is_still_running = self.game_mode_instance.run(events)

        if not is_still_running:
            # A lógica de high score precisará ser diferente para o modo roguelite,
            # mas podemos ajustar isso depois.
            if self.game_mode_type == "NORMAL":
                self.last_score = self.game_mode_instance.score
                if self.last_score > self.high_score:
                    self.high_score = self.last_score
                    self.save_high_score()
            
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
                    self.game_mode_type = "NORMAL" # <-- 4. DEFINIR O TIPO DE MODO
                    self.game_state = "RUNNING"
                elif roguelite_button.collidepoint(event.pos):
                    self.game_mode_type = "ROGUELITE" # <-- 5. DEFINIR O TIPO DE MODO
                    self.game_state = "RUNNING"
                    print("Iniciando o modo Roguelite...")

    def show_game_over_screen(self, events):
        # A instância do jogo anterior é desenhada por trás do menu
        self.game_mode_instance.draw()

        score_text = f"Sua Pontuacao: {self.last_score:05d}"
        draw_message_component("GAME OVER", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        draw_message_component(score_text, self.screen, font_size=30, pos_y_center=SCREEN_HEIGHT // 2 - 50)
        
        retry_button_rect = draw_message_component("Jogar Novamente", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        menu_button_rect = draw_message_component("Menu Principal", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button_rect.collidepoint(event.pos):
                    self.game_mode_instance = None # Limpa o jogo antigo
                    self.game_state = "RUNNING"
                elif menu_button_rect.collidepoint(event.pos):
                    self.game_mode_instance = None
                    self.game_state = "MENU"

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())
        except (FileNotFoundError, ValueError):
            self.high_score = 0
    
    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))