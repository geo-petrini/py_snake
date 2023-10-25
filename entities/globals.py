import pygame

DIRECTION_UP = 0        #snake direction up
DIRECTION_RIGHT = 1     #snake direction right
DIRECTION_DOWN = 2      #snake direction down
DIRECTION_LEFT = 3      #snake direction left

class GameColor:
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

class GameConfig:
    TIMER_TICK_EVENT = pygame.USEREVENT + 1
    FPS = 15
    WINDOW = pygame.Surface( (10,10) )  #readable also with pygame.display.get_surface()


class Grid:
    #maybe change to singleton
    _GRID = None         #the grid, initialized as 2 dimesnional list
    GRID_SIZE = 35      #size of the grid, same for x and y
    GRID_ITEM_SNAKE = 1 #grid cell contains a snake
    GRID_ITEM_FOOD = 10 #grid cell contains food
    BLOCK_SIZE = 10     #size in pixels of a grid block

    def initialize():
        filler = None
        cols = Grid.GRID_SIZE
        rows = Grid.GRID_SIZE
        Grid._GRID = [[filler for c in range(cols)] for r in range(rows)]

    def reset():
        Grid.initialize()

    def get_item(x, y):
        return Grid._GRID[x][y] if x > 0 and x < Grid.GRID_SIZE and y > 0 and y < Grid.GRID_SIZE and Grid._GRID else None
    
    def set_item(x, y, type):
        if Grid._GRID == None: Grid.initialize
        Grid._GRID[x][y] = type

    def __repr__(self):
        return f'{Grid._GRID}'


