import pygame
#https://www.pygame.org/docs/ref/color_list.html
# BACKGROUND_COLOR = pygame.Color('whitesmoke')
BACKGROUND_COLOR = pygame.Color('antiquewhite')
HELPER_COLOR = pygame.Color('wheat4')
SNAKE_1_COLOR = pygame.Color('royalblue4')
SNAKE_2_COLOR = pygame.Color('darkolivegreen4')
SNAKE_3_COLOR = pygame.Color('tomato3')
SNAKE_4_COLOR = pygame.Color('slateblue3')
FOOD_COLOR = pygame.Color('orangered2')
FONT_COLOR = pygame.Color('gray23')

#SNAKE_1_HEAD_COLOR = pygame.Color('royalblue')
#SNAKE_2_HEAD_COLOR = pygame.Color('darkolivegreen')

DEBUG_COLOR = pygame.Color("orchid")

BLOCK_SIZE = 10

TIMER_TICK_EVENT = pygame.USEREVENT + 1

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

FPS = 15

WINDOW = pygame.Surface( (10,10))