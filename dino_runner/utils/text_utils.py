import pygame
import os
from dino_runner.utils.constants import SCREEN_HEIGHT, SCREEN_WIDTH

FONT_COLOR = (83, 83, 83)
FONT_SIZE = 22
# CORREÇÃO: O caminho agora aponta para 'font' (minúsculo) para corresponder à sua estrutura de ficheiros.
# Esta linha torna o ficheiro independente, resolvendo o erro de importação.
FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'font', 'PressStart2P-Regular.ttf')

def draw_message_component(
    message,
    screen,
    font_color=FONT_COLOR,
    font_size=FONT_SIZE,
    pos_y_center=SCREEN_HEIGHT // 2,
    pos_x_center=SCREEN_WIDTH // 2,
    has_background=False,
    bg_color=(0, 0, 0), 
    return_rect=False 
):
    try:
        # Usa o FONT_PATH definido neste ficheiro.
        font = pygame.font.Font(FONT_PATH, font_size)
    except pygame.error:
        print(f"Aviso: Fonte em '{FONT_PATH}' não encontrada. Usando fonte padrão.")
        # Usa uma fonte padrão do Pygame como alternativa segura.
        font = pygame.font.Font(None, int(font_size * 1.5))
        
    text = font.render(message, True, font_color)
    text_rect = text.get_rect(center=(pos_x_center, pos_y_center))

    if has_background:
        button_padding = 10
        button_rect = text_rect.inflate(button_padding * 2, button_padding * 2)
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=5)
    
    screen.blit(text, text_rect)

    if return_rect:
        if has_background:
            return button_rect
        return text_rect
