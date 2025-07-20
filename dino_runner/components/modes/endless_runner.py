# Ficheiro: dino_runner/components/modes/endless_runner.py
# Autor: [O Seu Nome]
# Descrição: Define a lógica principal para o modo de jogo clássico "Endless Runner".
#            Esta classe gereia o jogador, os obstáculos, a pontuação e o cenário em movimento.

import pygame
import random
from dino_runner.components.dinos.endless_runner_dino import EndlessRunnerDino
from dino_runner.components.obstacles.cactus import Cactus
from dino_runner.components.obstacles.bird import Bird
from dino_runner.utils.constants import SCREEN_WIDTH
from dino_runner.utils.text_utils import draw_message_component

class Cloud:
    """Representa uma nuvem decorativa que se move no fundo do cenário."""
    def __init__(self, assets):
        """
        Inicializa a nuvem.
        
        Args:
            assets (AssetManager): O gestor de assets para carregar a imagem da nuvem.
        """
        self.image = assets.get_image("CLOUD")
        self.x = SCREEN_WIDTH + random.randint(300, 1000)
        self.y = random.randint(50, 250)

    def update(self, game_speed):
        """Move a nuvem para a esquerda com base na velocidade do jogo."""
        self.x -= game_speed
    
    def draw(self, screen):
        """Desenha a nuvem no ecrã."""
        screen.blit(self.image, (self.x, self.y))

class EndlessRunner:
    """
    Gereia toda a lógica e os elementos do modo de jogo Endless Runner.
    """
    def __init__(self, screen, high_score, assets, sounds, settings, first_run=False):
        """
        Inicializa o modo de jogo.

        Args:
            screen (pygame.Surface): A superfície principal do ecrã para desenhar.
            high_score (int): O recorde atual para este modo.
            assets (AssetManager): O gestor de todos os assets visuais.
            sounds (SoundManager): O gestor de todos os efeitos sonoros.
            settings (dict): As configurações do jogo (som, música, etc.).
            first_run (bool): Indica se é a primeira execução para o dinossauro começar parado.
        """
        self.screen = screen
        self.high_score = high_score
        self.assets = assets
        self.sounds = sounds
        self.settings = settings
        
        # Carrega os assets necessários para este modo
        self.bg_image = self.assets.get_image("BG")
        self.player = EndlessRunnerDino(self.assets, first_run=first_run)
        
        # Listas para gerir os objetos no jogo
        self.obstacle_list = []
        self.clouds = []
        for i in range(3):
            cloud = Cloud(self.assets)
            cloud.x = random.randint(0, SCREEN_WIDTH)
            self.clouds.append(cloud)
            
        # Variáveis de estado do jogo
        self.game_speed = 13
        self.score = 0
        self.x_pos_bg = 0
        self.y_pos_bg = 380

    def handle_events(self, events):
        """Processa os inputs do jogador (pulo e agachar)."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_DOWN:
                    self.player.duck()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.player.unduck()

    def update(self):
        """Atualiza a lógica de todos os elementos do jogo a cada frame."""
        self.player.update()
        if self.player.is_dead:
            return False # Sinaliza o fim do jogo

        if not self.player.is_waiting:
            # Aumenta a pontuação e a velocidade do jogo progressivamente
            self.score += 1
            if self.score % 100 == 0 and self.score > 0:
                self.game_speed += 1
            
            self.update_background()
            
            # Gera novos obstáculos se a lista estiver vazia
            if len(self.obstacle_list) == 0:
                self.spawn_obstacle()
            
            # Atualiza os obstáculos e verifica a colisão
            for obstacle in self.obstacle_list:
                obstacle.update(self.game_speed, self.obstacle_list)
                
                # Define uma hitbox mais justa para o jogador
                player_hitbox = self.player.dino_rect.inflate(-40, -20)
                
                if player_hitbox.colliderect(obstacle.hitbox):
                    self.player.die()
                    return False # Fim do jogo
                    
        return True # O jogo continua

    def update_background(self):
        """Move o chão e as nuvens para criar a ilusão de movimento."""
        image_width = self.bg_image.get_width()
        self.x_pos_bg -= self.game_speed
        if self.x_pos_bg <= -image_width:
            self.x_pos_bg = 0
        
        for cloud in self.clouds:
            # As nuvens movem-se mais devagar para um efeito de paralaxe
            cloud.update(self.game_speed / 2)
            if cloud.x < -cloud.image.get_width():
                cloud.x = SCREEN_WIDTH + random.randint(200, 500)
                cloud.y = random.randint(50, 250)

    def draw(self):
        """Desenha todos os elementos do jogo no ecrã."""
        self.screen.fill((255, 255, 255))
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        # Desenha duas imagens do chão para criar um loop contínuo
        image_width = self.bg_image.get_width()
        self.screen.blit(self.bg_image, (self.x_pos_bg, self.y_pos_bg))
        self.screen.blit(self.bg_image, (self.x_pos_bg + image_width, self.y_pos_bg))
        
        self.player.draw(self.screen)
        for obstacle in self.obstacle_list:
            obstacle.draw(self.screen)
        
        # Comentado para a versão final, mas útil para depuração
        # player_hitbox_debug = self.player.dino_rect.inflate(-40, -20)
        # pygame.draw.rect(self.screen, (255, 0, 0), player_hitbox_debug, 2)
        # for obstacle in self.obstacle_list:
        #     pygame.draw.rect(self.screen, (0, 0, 255), obstacle.hitbox, 2)

        # Desenha a pontuação e o recorde
        score_text = f"{self.score:05d}"
        draw_message_component(score_text, self.screen, pos_x_center=1000, pos_y_center=50)
        high_score_text = f"HI {self.high_score:05d}"
        draw_message_component(high_score_text, self.screen, pos_x_center=800, pos_y_center=50)

    def spawn_obstacle(self):
        """Escolhe e cria aleatoriamente um novo obstáculo (cacto ou pássaro)."""
        if random.randint(0, 1) == 0:
            self.obstacle_list.append(Cactus(self.assets))
        else:
            self.obstacle_list.append(Bird(self.assets))

    def run(self, events):
        """
        O método principal do modo de jogo, chamado a cada frame pelo GameController.
        
        Returns:
            bool: True se o jogo deve continuar, False se for Game Over.
        """
        self.handle_events(events)
        is_running = self.update()
        self.draw()
        return is_running
