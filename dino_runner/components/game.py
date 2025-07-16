# dino_runner/components/game.py

import pygame
import random

from dino_runner.components.dinosaur import Dinosaur
from dino_runner.components.obstacles.cactus import Cactus
from dino_runner.components.obstacles.bird import Bird
from dino_runner.utils.text_utils import draw_message_component
from dino_runner.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, ICON, BG

class Game:
    def __init__(self):
        # 1. Inicializa todos os módulos do pygame que são necessários
        pygame.init()
        self.player = Dinosaur()
        
        # 2. Define a largura e altura da tela, e o título
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(ICON) # Define o ícone da janela
        
        # 3. Cria um objeto Clock para ajudar a controlar a taxa de quadros (FPS)
        self.clock = pygame.time.Clock()
        
        # 4. Variáveis importantes do jogo
        self.playing = False
        self.game_speed = 13
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.obstacle_list = []
        self.death_count = 0 
        self.score = 0

    def spawn_obstacle(self):
        if random.randint(0, 1) == 0:
            self.obstacle_list.append(Cactus())
        else:
            self.obstacle_list.append(Bird())

    def execute(self):
        # Transforma a variável self.playing em True para iniciar o jogo
        self.playing = True
        # Loop principal do jogo
        while self.playing:
            # Verifica se algum evento ocorreu
            self.events()
            # Atualiza o estado do jogo
            self.update()
            # Desenha os elementos na tela
            self.draw()
        
        # Quando o loop termina, fecha o pygame
        pygame.quit()

    def events(self):
        for event in pygame.event.get():
            # Evento para fechar a janela
            if event.type == pygame.QUIT:
                self.playing = False

            # SEÇÃO 1: VERIFICA TECLAS PRESSIONADAS
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_DOWN:
                    self.player.duck()

            # SEÇÃO 2: VERIFICA TECLAS SOLTAS (no mesmo nível do KEYDOWN)
            elif event.type == pygame.KEYUP:
                # Se a tecla que foi solta é a SETA PARA BAIXO...
                if event.key == pygame.K_DOWN:
                    # ...manda o jogador se levantar usando o método que criamos
                    self.player.unduck()

    def update(self):
        self.player.update()
        self.score += 1

        # A cada 100 pontos, aumenta a velocidade do jogo
        if self.score % 100 == 0 and self.score > 0:
            self.game_speed += 1

        if len(self.obstacle_list) == 0:
            self.spawn_obstacle()

        for obstacle in self.obstacle_list:
            obstacle.update(self.game_speed, self.obstacle_list)
            if self.player.dino_rect.colliderect(obstacle.rect):
                self.player.die()
                pygame.time.delay(500)
                self.playing = False
                self.death_count += 1
                break

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