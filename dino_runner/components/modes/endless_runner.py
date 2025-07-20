import pygame
import random
from dino_runner.components.dinos.endless_runner_dino import EndlessRunnerDino
from dino_runner.components.obstacles.cactus import Cactus
from dino_runner.components.obstacles.bird import Bird
from dino_runner.utils.constants import SCREEN_WIDTH
from dino_runner.utils.text_utils import draw_message_component

class Cloud:
    def __init__(self, assets):
        self.image = assets.get_image("CLOUD")
        self.x = SCREEN_WIDTH + random.randint(300, 1000)
        self.y = random.randint(50, 250)

    def update(self, game_speed):
        self.x -= game_speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class EndlessRunner:
    def __init__(self, screen, high_score, assets, sounds, settings, first_run=False):
        self.screen = screen
        self.high_score = high_score
        self.assets = assets
        self.sounds = sounds
        self.settings = settings
        
        self.bg_image = self.assets.get_image("BG")
        self.player = EndlessRunnerDino(self.assets, first_run=first_run)
        self.obstacle_list = []
        self.clouds = []
        for i in range(3):
            cloud = Cloud(self.assets)
            cloud.x = random.randint(0, SCREEN_WIDTH)
            self.clouds.append(cloud)
            
        self.game_speed = 13
        self.score = 0
        self.x_pos_bg = 0
        self.y_pos_bg = 380

    def handle_events(self, events):
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
        if self.player.is_dead: return False

        if not self.player.is_waiting:
            self.score += 1
            if self.score % 100 == 0 and self.score > 0:
                self.game_speed += 1
            self.update_background()
            if len(self.obstacle_list) == 0:
                self.spawn_obstacle()
            for obstacle in self.obstacle_list:
                obstacle.update(self.game_speed, self.obstacle_list)
                
                player_hitbox = self.player.dino_rect.inflate(-40, -20)
                
                # CORREÇÃO: A colisão agora usa a hitbox justa do obstáculo
                if player_hitbox.colliderect(obstacle.hitbox):
                    self.player.die()
                    return False
        return True

    def update_background(self):
        image_width = self.bg_image.get_width()
        self.x_pos_bg -= self.game_speed
        if self.x_pos_bg <= -image_width:
            self.x_pos_bg = 0
        
        for cloud in self.clouds:
            cloud.update(self.game_speed / 2)
            if cloud.x < -cloud.image.get_width():
                cloud.x = SCREEN_WIDTH + random.randint(200, 500)
                cloud.y = random.randint(50, 250)

    def draw(self):
        self.screen.fill((255, 255, 255))
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        image_width = self.bg_image.get_width()
        self.screen.blit(self.bg_image, (self.x_pos_bg, self.y_pos_bg))
        self.screen.blit(self.bg_image, (self.x_pos_bg + image_width, self.y_pos_bg))
        
        self.player.draw(self.screen)
        for obstacle in self.obstacle_list:
            obstacle.draw(self.screen)
        
        # CORREÇÃO: O desenho da hitbox agora mostra a hitbox de colisão real
        #player_hitbox_debug = self.player.dino_rect.inflate(-40, -20)
        #pygame.draw.rect(self.screen, (255, 0, 0), player_hitbox_debug, 2)
        #for obstacle in self.obstacle_list:
        #    pygame.draw.rect(self.screen, (0, 0, 255), obstacle.hitbox, 2)

        score_text = f"{self.score:05d}"
        draw_message_component(score_text, self.screen, pos_x_center=1000, pos_y_center=50)
        high_score_text = f"HI {self.high_score:05d}"
        draw_message_component(high_score_text, self.screen, pos_x_center=800, pos_y_center=50)

    def spawn_obstacle(self):
        if random.randint(0, 1) == 0:
            self.obstacle_list.append(Cactus(self.assets))
        else:
            self.obstacle_list.append(Bird(self.assets))

    def run(self, events):
        self.handle_events(events)
        is_running = self.update()
        self.draw()
        return is_running
