# dino_runner/components/game.py

import pygame
import random

from dino_runner.components.dinosaur import Dinosaur
from dino_runner.components.obstacles.cactus import Cactus
from dino_runner.components.obstacles.bird import Bird
from dino_runner.utils.text_utils import draw_message_component
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, ICON, BG, RUNNING

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(ICON)
        self.clock = pygame.time.Clock()

        # Variáveis do jogo
        self.player = Dinosaur()
        self.obstacle_list = []
        self.game_speed = 13
        self.score = 0
        self.death_count = 0
        self.x_pos_bg = 0
        self.y_pos_bg = 380

        # Variáveis de controle
        self.running = True
        self.game_state = "MENU"

        # Carrega a imagem do dino para o menu
        self.menu_dino_image = RUNNING[0]
        # Redimensiona a imagem para ficar maior no menu
        self.menu_dino_image = pygame.transform.scale(self.menu_dino_image, (120, 120))

    def show_menu(self):
        self.screen.fill((255, 255, 255))
    
        # --- POSIÇÕES CORRIGIDAS ---
        # 1. Desenha o dinossauro um pouco mais para cima
        self.screen.blit(self.menu_dino_image, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 250))
        
        # 2. Desenha o título abaixo do dinossauro
        draw_message_component("Dino Runner", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        
        # 3. Desenha os botões mais para baixo, deixando espaço para o título
        play_button_rect = draw_message_component("Jogar", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        exit_button_rect = draw_message_component("Sair", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)
        # --- FIM DAS CORREÇÕES ---
    
        # O loop de eventos continua o mesmo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    self.game_state = "RUNNING"
                elif exit_button_rect.collidepoint(event.pos):
                    self.running = False
    
        pygame.display.update()
        self.clock.tick(FPS)

    def reset_game(self):
        self.obstacle_list.clear()
        self.player.reset()
        self.score = 0
        self.game_speed = 13

    def show_game_over_screen(self):
        self.screen.fill((255, 255, 255))
        score_text = f"Sua Pontuacao: {self.score:05d}"
        draw_message_component("GAME OVER", self.screen, font_size=50, pos_y_center=SCREEN_HEIGHT // 2 - 100)
        draw_message_component(score_text, self.screen, font_size=30, pos_y_center=SCREEN_HEIGHT // 2 - 50)

        retry_button_rect = draw_message_component("Jogar Novamente", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 50, has_background=True, return_rect=True)
        menu_button_rect = draw_message_component("Menu Principal", self.screen, pos_y_center=SCREEN_HEIGHT // 2 + 120, has_background=True, return_rect=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button_rect.collidepoint(event.pos):
                    self.reset_game()
                    self.game_state = "RUNNING"
                elif menu_button_rect.collidepoint(event.pos):
                    self.reset_game()
                    self.game_state = "MENU"
        pygame.display.update()
        self.clock.tick(FPS)

    def spawn_obstacle(self):
        if random.randint(0, 1) == 0:
            self.obstacle_list.append(Cactus())
        else:
            self.obstacle_list.append(Bird())

    def run_gameplay(self):
        # A lógica que já tínhamos para rodar o jogo
        self.events()
        self.update()
        self.draw()

    def execute(self):
        while self.running:
            if self.game_state == "MENU":
                # Nosso próximo passo será criar este método
                self.show_menu() 
            elif self.game_state == "RUNNING":
                # A lógica que já temos de eventos, update e draw
                self.run_gameplay() 
            elif self.game_state == "GAME_OVER":
                # Outro método que criaremos
                self.show_game_over_screen() 

        pygame.quit()

    def events(self):
        for event in pygame.event.get():
            # Fecha o game ao fechar o executável
            if event.type == pygame.QUIT:
                self.running = False # <--- CORREÇÃO AQUI (era self.playing)

            # Eventos de TECLA PRESSIONADA
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_DOWN:
                    self.player.duck()

            # Evento de TECLA SOLTA
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.player.unduck()

    def update(self):
        self.player.update()
        self.score += 1

        # A cada 100 pontos, aumenta a velocidade do jogo
        if self.score % 100 == 0 and self.score > 0:
            self.game_speed += 1

        if len(self.obstacle_list) == 0:
            self.spawn_obstacle()

        # Atualiza todos os obstáculos na lista
        for obstacle in self.obstacle_list:
            obstacle.update(self.game_speed, self.obstacle_list)

            # --- Bloco de Colisão Completo e Corrigido ---
            # Cria as hitboxes encolhidas para uma colisão justa
            player_hitbox = self.player.dino_rect.inflate(-25, -5)
            obstacle_hitbox = obstacle.rect.inflate(-20, -10)

            # A verificação de colisão usa as hitboxes justas
            if player_hitbox.colliderect(obstacle_hitbox):
                # Chama o método de morte do jogador
                self.player.die()
                # Muda o estado do jogo para GAME_OVER
                self.game_state = "GAME_OVER"
                # Para o loop assim que encontrar a primeira colisão
                break
            # --- Fim do Bloco de Colisão ---

        # Movimentação do chão
        image_width = BG.get_width()
        self.x_pos_bg -= self.game_speed
        if self.x_pos_bg <= -image_width:
            self.x_pos_bg = 0

    def draw(self):
        self.screen.fill((255, 255, 255))
        image_width = BG.get_width()
        self.screen.blit(BG, (self.x_pos_bg, self.y_pos_bg))
        self.screen.blit(BG, (self.x_pos_bg + image_width, self.y_pos_bg))

        self.player.draw(self.screen)

        for obstacle in self.obstacle_list:
            obstacle.draw(self.screen)

        # --- CORREÇÃO AQUI ---
        # 1. Formata a pontuação para ter 5 dígitos (ex: 00100)
        score_text = f"{self.score:05d}"
        # 2. Desenha APENAS os números formatados na tela
        draw_message_component(score_text, self.screen, pos_x_center=1000, pos_y_center=50)
        # --- FIM DA CORREÇÃO ---

        # Lógica do Game Over
        if self.death_count > 0:
            draw_message_component("GAME OVER", self.screen)

        # Não se esqueça de desenhar as hitboxes se você ainda as estiver usando para debug
        pygame.draw.rect(self.screen, (255, 0, 0), self.player.dino_rect, 2)
        for obstacle in self.obstacle_list:
             pygame.draw.rect(self.screen, (0, 0, 255), obstacle.rect, 2)

        pygame.display.update()
        self.clock.tick(FPS)