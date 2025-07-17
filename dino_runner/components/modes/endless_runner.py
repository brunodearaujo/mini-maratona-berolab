# dino_runner/components/modes/endless_runner.py

import pygame
import random
from dino_runner.components.dinos.endless_runner_dino import EndlessRunnerDino
from dino_runner.components.obstacles.cactus import Cactus
from dino_runner.components.obstacles.bird import Bird
from dino_runner.utils.constants import BG, SCREEN_WIDTH
from dino_runner.utils.text_utils import draw_message_component

class EndlessRunner:
    def __init__(self, screen, high_score, first_run=False):
        self.screen = screen
        self.high_score = high_score
        self.player = EndlessRunnerDino(first_run=first_run)
        self.obstacle_list = []
        self.game_speed = 13
        self.score = 0
        self.x_pos_bg = 0
        self.y_pos_bg = 380

    def handle_events(self, events):
        # Este método processa a lista de eventos recebida do GameController
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
        self.player.update()

        if self.player.is_dead:
            return False # Indica Game Over

        if not self.player.is_waiting:
            self.score += 1
            if self.score % 100 == 0 and self.score > 0:
                self.game_speed += 1

            self.update_background()

            if len(self.obstacle_list) == 0:
                self.spawn_obstacle()

            for obstacle in self.obstacle_list:
                obstacle.update(self.game_speed, self.obstacle_list)
                player_hitbox = self.player.dino_rect.inflate(-25, -5)
                obstacle_hitbox = obstacle.rect.inflate(-20, -10)
                if player_hitbox.colliderect(obstacle_hitbox):
                    self.player.die()
                    return False # Indica Game Over

        return True # Indica que o jogo continua

    def update_background(self):
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
        
        score_text = f"{self.score:05d}"
        draw_message_component(score_text, self.screen, pos_x_center=1000, pos_y_center=50)
        high_score_text = f"HI {self.high_score:05d}"
        draw_message_component(high_score_text, self.screen, pos_x_center=800, pos_y_center=50)

        # Desenhando as hitboxes de debug
        player_hitbox_debug = self.player.dino_rect.inflate(-25, -5)
        pygame.draw.rect(self.screen, (255, 0, 0), player_hitbox_debug, 2)
        for obstacle in self.obstacle_list:
            obstacle_hitbox_debug = obstacle.rect.inflate(-20, -10)
            pygame.draw.rect(self.screen, (0, 0, 255), obstacle_hitbox_debug, 2)

    def spawn_obstacle(self):
        if random.randint(0, 1) == 0:
            self.obstacle_list.append(Cactus())
        else:
            self.obstacle_list.append(Bird())

    def run(self, events):
        # O método run agora orquestra as chamadas
        self.handle_events(events)
        is_running = self.update()
        self.draw()
        return is_running