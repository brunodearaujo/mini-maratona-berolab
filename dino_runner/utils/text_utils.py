# Em utils/text_utils.py

import pygame
import os
from dino_runner.utils.constants import SCREEN_HEIGHT, SCREEN_WIDTH

FONT_COLOR = (83, 83, 83)
FONT_SIZE = 22
FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'font', 'PressStart2P-Regular.ttf')
FONT_STYLE = FONT_PATH

def draw_message_component(
    message,
    screen,
    font_color=FONT_COLOR,
    font_size=FONT_SIZE,
    pos_y_center=SCREEN_HEIGHT // 2,
    pos_x_center=SCREEN_WIDTH // 2,
    has_background=False,
    return_rect=False 
):
    font = pygame.font.Font(FONT_STYLE, font_size)
    text = font.render(message, True, font_color)
    text_rect = text.get_rect(center=(pos_x_center, pos_y_center))

    if has_background:
        button_padding = 10
        button_rect = text_rect.inflate(button_padding * 2, button_padding * 2)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, border_radius=5)
    
    screen.blit(text, text_rect)

    if return_rect:
        # Se for um botão, precisamos retornar seu retângulo para a detecção de cliques
        if has_background:
            return button_rect
        return text_rect