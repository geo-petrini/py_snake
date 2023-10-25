from pickletools import UP_TO_NEWLINE
from tkinter import RIGHT
from turtle import position
import pygame
from pygame import Surface, transform, Rect
import pygame_gui
import logging
import random
import math
import logmanager

from entities.globals import *
from entities.food import *
from entities.snake import *
from entities.position import Position

#import sys
#logging.basicConfig(datefmt = '%Y-%m-%d %H:%M:%S', filename = 'app.log', format = '[%(asctime)s][%(levelname)s] %(message)s', level = logging.DEBUG)
#logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S', format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.DEBUG, stream=sys.stdout)
#logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s %(levelname)s %(process)s %(thread)s %(filename)s %(funcName)s():%(lineno)d %(message)s', level=logging.DEBUG, stream=sys.stdout)
logmanager.get_configured_logger()

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def blit_rotate_center(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def _test_snake_add_lenght(snake: Snake, len: int):
    for _ in range(len):    
        snake.eat()


class Game():

    def __init__(self):
        
        self.window_width = 800
        self.window_height = 600
        
        self.__game_over = False
        self.__pause = False
        self.__display_debug = False  
        self.__game_initialized = False

        self.__snakes = []
        self.__foods = []
        self.__players_number = 4

        self.__matrix = None

        pygame.init()

        self.setup_window_size()
        Grid.initialize()
        
        self.__ui_manager = pygame_gui.UIManager(GameConfig.WINDOW.get_size())
        self.__ui_manager.set_visual_debug_mode(True)
        #pygame.display.update()
        pygame.display.set_caption('Snake game')


        pygame.time.set_timer(GameConfig.TIMER_TICK_EVENT, 1000)
        self.countdown_timer = 5

        try:
            icon = pygame.image.load('res/icon.png')
            pygame.display.set_icon(icon)
        except:
            pass

    def setup_window_size(self):
        #min size 800x600
        #min blocks 35x35
        #max size screen width height
        #window must be multiple of BLOCK_SIZE
        screen_info = pygame.display.Info() #Required to set a good resolution for the game screen
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        first_screen = (screen_width, screen_height) #Take 120 pixels from the height because the menu bar, window bar and dock takes space 
        
        min_screen_size = min(screen_height, screen_width)
        if min_screen_size <= 600:
            max_block_size = math.floor(min_screen_size //  Grid.GRID_SIZE)
            Grid.BLOCK_SIZE = max_block_size
            self.window_width =  Grid.BLOCK_SIZE *  Grid.GRID_SIZE
            self.window_height =  Grid.BLOCK_SIZE *  Grid.GRID_SIZE

        else:
            max_block_size = math.floor(min_screen_size //  Grid.GRID_SIZE)
            Grid.BLOCK_SIZE = max_block_size
            self.window_width =  Grid.BLOCK_SIZE *  Grid.GRID_SIZE
            self.window_height =  Grid.BLOCK_SIZE *  Grid.GRID_SIZE
        
        GameConfig.WINDOW = pygame.display.set_mode((self.window_width, self.window_height))
        logging.debug(f'grid: { Grid.GRID_SIZE}, block: { Grid.BLOCK_SIZE}, w: {self.window_width}, h: {self.window_height}, sw: {screen_width}, sh: {screen_height}')
    
    @property
    def width(self):
        return self.window_width
    
    @property
    def height(self):
        return self.window_height
        
    @property
    def snakes(self):
        return self.__snakes
        
    @property
    def foods(self):
        return self.__foods

    def add_snakes(self, n = 1):
        for i in range(n):
            index = i+1
            
            color = vars(GameColor)[f'SNAKE_{index}_COLOR'] if f'SNAKE_{index}_COLOR' in vars(GameColor) else GameColor.DEBUG_COLOR
            #head_color = color.correct_gamma(0.5) #globals()[f'SNAKE_{index}_HEAD_COLOR'] if f'SNAKE_{index}_HEAD_COLOR' in globals() else DEBUG_COLOR
            name = f'Player {index}'
            # x = window.get_size()[0]//2 + index * BLOCK_SIZE * 2
            # y = window.get_size()[1]//2 + index * BLOCK_SIZE * 2
            #p = Position( x, y )
            #s = Snake(p, color=color, head_color=head_color, name=name)
            if i == 0: keys = {'left':pygame.K_LEFT, 'right':pygame.K_RIGHT}
            if i == 1: keys = {'left':pygame.K_a, 'right':pygame.K_s}
            if i == 2: keys = {'left':pygame.K_k, 'right':pygame.K_l}
            if i == 3: keys = {'left':pygame.K_b, 'right':pygame.K_n}

            position, direction = self.__init_snake_position(index)
            
            self.snakes.append( Snake( position=position, color=color, head_color=None, name=name, keys=keys, direction=direction) )

    def __init_snake_position(self, index):
        '''
          3
        1   2  
          4
        '''
        surface_width = GameConfig.WINDOW.get_size()[0]
        surface_height = GameConfig.WINDOW.get_size()[1]
        if index == 1:
            x = (Grid.GRID_SIZE //2 - 3) * Grid.BLOCK_SIZE
            y = (Grid.GRID_SIZE //2 +1) * Grid.BLOCK_SIZE
            direction = DIRECTION_LEFT

        if index == 2:
            x = (Grid.GRID_SIZE //2 + 3) * Grid.BLOCK_SIZE
            y = (Grid.GRID_SIZE //2 -1) * Grid.BLOCK_SIZE
            direction = DIRECTION_RIGHT    

        if index == 3:
            x = (Grid.GRID_SIZE //2 -1 ) * Grid.BLOCK_SIZE            
            y = (Grid.GRID_SIZE //2 -3) * Grid.BLOCK_SIZE
            direction = DIRECTION_UP           

        if index == 4:
            x = (Grid.GRID_SIZE //2 +1) * Grid.BLOCK_SIZE            
            y = (Grid.GRID_SIZE //2 +3) * Grid.BLOCK_SIZE
            direction = DIRECTION_DOWN

        logging.debug(f'{index}, position: {x},{y}, direction: {direction}, screen {surface_width},{surface_height}')
        return ( Position(x, y), direction  )            

    def add_food(self, items = 1):
        (w, h) = GameConfig.WINDOW.get_size()
        
        for _ in range(items):
            while True:
                foodx = round(random.randrange(0, w - Grid.BLOCK_SIZE) // Grid.BLOCK_SIZE) * Grid.BLOCK_SIZE
                foody = round(random.randrange(0, h - Grid.BLOCK_SIZE) // Grid.BLOCK_SIZE) * Grid.BLOCK_SIZE
                if Grid.get_item(foodx, foody) == None:
                    break

            f = Food( position=Position(foodx, foody) ) 
            self.foods.append(f)
            logging.debug(f'new food {f}')

    def chk_collision(self, item, target):
        if isinstance(target, list):
            for t in target:
                if item != t:
                    self.chk_collision(item, t)

        #collision snake and food
        if isinstance(item, Snake) and isinstance(target, Food):
            if item.position == target.position:
                item.eat()
                logging.debug(f'eat: {item}, {target}')
                target.status = STATUS_EATEN

        if isinstance(item, Snake) and isinstance(target, Snake) :
            if item.collide_vs_snake(target):
                item.die()
                logging.debug(f'die: {item}')

    def _display_pause(self):
        if self.__pause:
            font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
            pause_text = font.render('PAUSE', True, GameColor.FONT_COLOR)
            pause_text_rect = pause_text.get_rect()
            pause_text_rect.center = (self.width//2, self.height//2)
            GameConfig.WINDOW.blit(pause_text, pause_text_rect)

    def _display_helpers(self, s, f):
        if s.x == f.x or s.y == f.y:
            if s.x == f.x:
                if s.y < f.y:
                    helpery = s.y + Grid.BLOCK_SIZE 
                else:
                    helpery = f.y + Grid.BLOCK_SIZE 

                if s.y < f.y:
                    helperh = f.y - helpery 
                else:
                    helperh = s.y - helpery 
                helperx = s.x
                helperw = Grid.BLOCK_SIZE

            if s.y == f.y:
                if s.x < f.x:
                    helperx = s.x + Grid.BLOCK_SIZE  
                else:
                    helperx = f.x + Grid.BLOCK_SIZE  

                if s.x < f.x:
                    helperw = f.x - helperx 
                else:
                    helperw = s.x - helperx 
                helpery = s.y
                helperh = Grid.BLOCK_SIZE            

            '''
            helperx = min(s.x, f.x)
            helpery = min(s.y, f.y)
            helperw = max(max(s.x, f.x) - helperx, BLOCK_SIZE)
            helperh = max(max(s.y, f.y) - helpery, BLOCK_SIZE)
            '''
            #logging.debug(f'helpers: x: {helperx}, y: {helpery}, w: {helperw}, h: {helperh}')
            pygame.draw.rect(GameConfig.WINDOW, GameColor.HELPER_COLOR, [helperx, helpery, helperw, helperh], 3)
        
    def _display_countdown(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
        if self.countdown_timer > 0:
            countdown_text = font.render(f'{ self.countdown_timer }', True, GameColor.FONT_COLOR)
            countdown_text_rect = countdown_text.get_rect()
            countdown_text_rect.center = (self.width//2, self.height//2)
            GameConfig.WINDOW.blit(countdown_text, countdown_text_rect)        

    def _display_score(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
        for i, s in enumerate(self.snakes):
            score_text = font.render(f'{ (s.lenght-1) * 10 }', True, s.color)
            #score_text_rect = score_text.get_rect()
            GameConfig.WINDOW.blit(score_text, ( 20, 10 +(i*50)) )

    def _display_grid(self):
        for x in range(0, GameConfig.WINDOW.get_size()[0], Grid.BLOCK_SIZE ):
            for y in range(0, GameConfig.WINDOW.get_size()[1], Grid.BLOCK_SIZE):
                width = 3 if ((x % 100 == 0) and (y % 100 == 0)) else 1
                pygame.draw.line(GameConfig.WINDOW, pygame.Color('gray30'), (x, 0), (x, GameConfig.WINDOW.get_size()[1]), width)
                pygame.draw.line(GameConfig.WINDOW, pygame.Color('gray30'), (0, y), (GameConfig.WINDOW.get_size()[0], y), width)

    def _display_mouse_coordinates(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
        mouse_text = font.render(f'{ pygame.mouse.get_pos() }', True, GameColor.DEBUG_COLOR)
        GameConfig.WINDOW.blit(mouse_text, ( pygame.mouse.get_pos() )) 

    def _display_time(self, t):
    # change milliseconds into minutes, seconds, milliseconds
        t_minutes = str(t/60000).zfill(2)
        t_seconds = str( (t%60000)/1000 ).zfill(2)
        t_millisecond = str(t%1000).zfill(3)

        #t_string = f'{t_minutes}:{t_seconds}:{t_millisecond}'
        t_string = f'{t}'
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
        t_string_rect = font.render( t_string, True, GameColor.DEBUG_COLOR)
        GameConfig.WINDOW.blit(t_string_rect, (GameConfig.WINDOW.get_size()[0]//2, GameConfig.WINDOW.get_size()[1]//2-30))     

    def _display_debug_info(self, objects):
        
        for i, o in enumerate(objects):
            font = pygame.font.Font('./asset/Fipps-Regular.otf', 10)
            text = font.render(f'{ o.position }', True, o.color if o.color else GameColor.DEBUG_COLOR)
            GameConfig.WINDOW.blit(text, ( 100, 20+(i*24) ))

            if isinstance(o, Snake):
                font = pygame.font.Font('./asset/Fipps-Regular.otf', 8)
                for sn, segment in enumerate(o.body):
                    if sn == 0:
                        text = font.render(f'{segment.x}\n{segment.y}', True, o.color if o.color else GameColor.DEBUG_COLOR)
                    else:
                        text = font.render(f'{segment.x}\n{segment.y}', True, o.head_color if o.head_color else GameColor.DEBUG_COLOR)
                    GameConfig.WINDOW.blit(text, ( segment.x, segment.y ))                    

    def _print_debug_info(self, objects):
        for i, o in enumerate(objects):
            logging.debug(f'{o._info_str()}')

    def _update_snakes(self):
        for snake in self.snakes:
            snake.update()

    def _handle_events(self):
        for event in pygame.event.get():
            #logging.debug(event)   #prints out all the actions that take place on the screen
            if event.type == pygame.QUIT:
                self.__game_over=True    
            if event.type == pygame.KEYDOWN:

                for snake in self.snakes:       
                    try:
                        if event.key == snake.left_key: snake.rotate_left()
                        if event.key == snake.right_key: snake.rotate_right()
                    except:
                        logging.exception(f'error handling event {event.key} for snake {snake}')                   
                    
                #elif event.key == pygame.K_UP:
                #    snakes[0].set_direction(Snake.UP)
                #elif event.key == pygame.K_DOWN:
                #    snakes[0].set_direction(Snake.DOWN)    
                 
                #elif event.key == pygame.K_w:
                #    snakes[1].set_direction(Snake.UP)
                #elif event.key == pygame.K_s:
                #    snakes[1].set_direction(Snake.DOWN)                      
    
                if event.key == pygame.K_F12:
                    self.__display_debug = not self.__display_debug

                if event.key == pygame.K_F12 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self._print_debug_info( [*self.snakes, *self.foods] )

                if event.key == pygame.K_SPACE:
                    self.__pause = not self.__pause
                if event.key == pygame.K_ESCAPE:
                    self.__game_over = True 
            
            if event.type == GameConfig.TIMER_TICK_EVENT:
                if self.countdown_timer > 0: self.countdown_timer -= 1
             
            self.__ui_manager.process_events(event)        

    def update_grid(self):
        #TODO move to GameConfig
        Grid.reset()

        for snake in self.snakes:
            for segment in snake.body:
                Grid.set_item(segment.gx, segment.gy, Grid.GRID_ITEM_SNAKE)
        for food in self.foods:
            Grid.set_item(food.position.gx, food.position.gy, Grid.GRID_ITEM_FOOD)

        print(Grid)


    def start(self):
        #TODO refactor, too much going on in one single method
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks() 

        while not self.__game_over:
            time_delta = clock.tick(GameConfig.FPS)
            GameConfig.WINDOW.fill(GameColor.BACKGROUND_COLOR)
            self._handle_events()
            
            if self.countdown_timer == 5 and not self.__game_initialized:
                self.add_snakes( self.__players_number )
                self.add_food( self.__players_number )

                _test_snake_add_lenght(self.snakes[0], 50)
                _test_snake_add_lenght(self.snakes[1], 20)
                self.__game_initialized = True

            self._display_score()

            if not self.__pause and self.countdown_timer <= 0: 
                self._update_snakes()

            count_time = pygame.time.get_ticks() - start_time
            #self._display_time(count_time)

            for snake in self.snakes:
                snake.draw()
                self.chk_collision(snake, self.snakes)
                for food in self.foods:
                    food.draw()
                    self.chk_collision(snake, food)
                    self._display_helpers(snake, food)

            #do this loop after collisions to ensure collision check and make sure that all DEAD snakes are removed
            for snake in self.snakes:
                if snake.status == STATUS_DEAD:
                    self.snakes.remove(snake)

            for food in self.foods:
                if food.status == STATUS_EATEN:
                    self.foods.remove(food)
                    self.add_food()

            #self.update_grid()

            if self.__display_debug:
                self._display_grid()
                self._display_mouse_coordinates()
                self._display_debug_info( [*self.snakes, *self.foods] )        
            
            self._display_pause()
            self._display_countdown()
            
            self.__ui_manager.update(time_delta)
            self.__ui_manager.draw_ui(GameConfig.WINDOW)
            pygame.display.update()

        pygame.quit()
        quit()    

