import pygame
import random
import logging

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

    def get_item(col, row):
        return Grid._GRID[col][row] if col > 0 and col < Grid.GRID_SIZE and row > 0 and row < Grid.GRID_SIZE and Grid._GRID else None
    
    def set_item(x, y, type):
        col = Grid.px_to_pos(x)
        row = Grid.px_to_pos(y)
        if Grid._GRID == None: Grid.initialize
        Grid._GRID[col][row] = type

    def set_g_item(col, row, type):
        if Grid._GRID == None: Grid.initialize
        Grid._GRID[col][row] = type

    '''
    converts pixels to grid position (grid row or column)
    returns -1 if px < 0 or > Grid.GRID_SIZE * Grid.BLOCK_SIZE
    '''
    def px_to_pos(px):
        if px == 0:
            return 0
        if px > 0 and px <= Grid.GRID_SIZE * Grid.BLOCK_SIZE:
            return px % Grid.BLOCK_SIZE
        return -1

    '''
    convert grid position (row or col) to pixels
    returns -1 if pos < 0 or pos > Grid.GRID_SIZE
    '''
    def pos_to_px(pos):
        if pos < 0 or pos > Grid.GRID_SIZE:
            return -1
        return pos * Grid.BLOCK_SIZE

    def get_items_rects():
        rects = []
        for col in range(Grid.GRID_SIZE):
            for row in range(Grid.GRID_SIZE):
                cell = Grid._GRID[col][row]
                if cell != None:
                    r = pygame.Rect(Grid.pos_to_px(col), Grid.pos_to_px(row), Grid.BLOCK_SIZE, Grid.BLOCK_SIZE)
                    rects.append(r)
        return rects
    '''
    find an empty position in the grid for the given object near the target coordinates
    '''    
    def get_position_near(object_rect, target_coords, max_distance = 100):
        grid_items = Grid.get_items_rects()
        max = Grid.BLOCK_SIZE * Grid.GRID_SIZE
        max_attempts = 1000
        attempts = 0
        if max_distance == None:
            max_distance = max
        while attempts < max_attempts:
            #find an empty grid position for placing food
            rndx = round(random.randrange(-max_distance, max_distance) + target_coords[0])
            rndy = round(random.randrange(-max_distance, max_distance) + target_coords[1])

            if rndx < 0 or rndx + object_rect.width > max:
                continue
            if rndy < 0 or rndy + object_rect.height > max:
                continue

            new_rect = pygame.Rect(rndx, rndy, object_rect.width, object_rect.height)
            collide = new_rect.collidelist(grid_items)
            if collide == -1:
                return (rndx, rndy)
            else:
                logging.debug(f'rnd coords: {rndx}, {rndy}, rect: {new_rect}, collide: {collide} = {grid_items[collide]}')
            
            attempts+=1
            
        return None



    def __repr__(self):
        return f'{Grid._GRID}'


