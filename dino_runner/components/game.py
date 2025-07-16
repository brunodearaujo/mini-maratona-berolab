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
        self.game_speed = 10
        self.x_pos_bg = 0
        self.y_pos_bg = 380
        self.obstacle_list = []
        self.death_count = 0 

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

    # Em game.py, substitua seu método update() por este:
    def update(self):
        self.player.update()

        if len(self.obstacle_list) == 0:
            self.spawn_obstacle()

        for obstacle in self.obstacle_list:
            obstacle.update(self.game_speed, self.obstacle_list)
            # --- LÓGICA DE COLISÃO ---
            # cria uma cópia da hitbox do jogador e a encolhe
            player_hitbox = self.player.dino_rect.inflate(-25, -5) # Encolhe 25px na largura e 15px na altura

             # Cria uma cópia da hitbox do obstáculo e a encolhe
            obstacle_hitbox = obstacle.rect.inflate(-20, -10)


            if player_hitbox.colliderect(obstacle_hitbox):
                self.player.die()
                pygame.time.delay(500)
                self.playing = False
                self.death_count += 1
                break
            # --- FIM DA LÓGICA ---

        # Movimentação do chão
        image_width = BG.get_width()
        self.x_pos_bg -= self.game_speed
        if self.x_pos_bg <= -image_width:
            self.x_pos_bg = 0

    def draw(self):
        # Pinta a tela de branco
        self.screen.fill((255, 255, 255))

        # Pega a largura da imagem do chão
        image_width = BG.get_width()

        # Desenha a primeira imagem do chão
        self.screen.blit(BG, (self.x_pos_bg, self.y_pos_bg))
        # Desenha a segunda imagem do chão, logo após a primeira
        self.screen.blit(BG, (self.x_pos_bg + image_width, self.y_pos_bg))

        self.player.draw(self.screen)

        # desenha o hitbox do jogador para testes
        pygame.draw.rect(self.screen, (255, 0, 0), self.player.dino_rect, 2)

        # Desenha todos os obstáculos na lista
        for obstacle in self.obstacle_list:
            obstacle.draw(self.screen)
            # desenhar hitbox do obstáculo para testes
            pygame.draw.rect(self.screen, (0, 0, 255), obstacle.rect, 2)

        if self.death_count > 0:
            draw_message_component("GAME OVER", self.screen)

        # Atualiza a tela para mostrar o que foi desenhado
        pygame.display.update()
        # Garante que o jogo rode no FPS definido
        self.clock.tick(FPS)