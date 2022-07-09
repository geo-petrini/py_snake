from pickletools import UP_TO_NEWLINE
from tkinter import RIGHT
from turtle import position
import pygame
from pygame import Surface, transform
import pygame_gui
import logging
import random
import logmanager

#import sys
#logging.basicConfig(datefmt = '%Y-%m-%d %H:%M:%S', filename = 'app.log', format = '[%(asctime)s][%(levelname)s] %(message)s', level = logging.DEBUG)
#logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S', format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.DEBUG, stream=sys.stdout)
#logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s %(levelname)s %(process)s %(thread)s %(filename)s %(funcName)s():%(lineno)d %(message)s', level=logging.DEBUG, stream=sys.stdout)
logmanager.get_configured_logger()

#https://www.pygame.org/docs/ref/color_list.html
BACKGROUND_COLOR = pygame.Color('whitesmoke')
HELPER_COLOR = pygame.Color('wheat4')
SNAKE_1_COLOR = pygame.Color('royalblue4')
SNAKE_2_COLOR = pygame.Color('darkolivegreen4')
SNAKE_3_COLOR = pygame.Color('tomato3')
SNAKE_4_COLOR = pygame.Color('slateblue3')
FOOD_COLOR = pygame.Color('orangered2')
FONT_COLOR = pygame.Color('gray23')

SNAKE_1_HEAD_COLOR= pygame.Color('royalblue')
SNAKE_2_HEAD_COLOR = pygame.Color('darkolivegreen')

DEBUG_COLOR = pygame.Color("orchid")

BLOCK_SIZE = 10

FPS = 15

surface = None

class Position():
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        #logging.debug(f'{self}')
    
    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( x: {self.x}, y: {self.y} )'

    def as_list(self):
        return [self.x, self.y]

    def as_dict(self):
        return {'x':self.x, 'y':self.y}

    def as_tuple(self):
        return (self.x, self.y)

class Food():

    def __init__(self, position, color=FOOD_COLOR, size=BLOCK_SIZE):
        self.color = color
        self.position = position
        self.size = size
        self.width = self.size
        self.height = self.size        
        self.surface = Surface((self.width+4, self.height+4))
        self.surface.set_colorkey((0, 0, 0))
        self.surface.fill(color)
        self.rect = self.surface.get_rect() 
        self.rotation = 0        
        #logging.debug(f'{self}')
        
    @property
    def x(self):
        return self.position.x if self.position else None

    @property
    def y(self):
        return self.position.y if self.position else None

    @x.setter
    def x(self, value):
        self.position.x = value

    @y.setter
    def y(self, value):
        self.position.y = value


    def draw(self):
        self.surface.fill( self.color.correct_gamma(0.1) )  # refill the surface color if you change it somewhere in the program
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x + self.size//2, self.y + self.size//2)    
    
        self.rotation = self.rotation + 2
        old_center = self.rect.center
        new = transform.rotate(self.surface, self.rotation)
        self.rect = new.get_rect()
        self.rect.center = old_center
        surface.blit(new, self.rect)   
        '''
        if self.frame <= 3:
            self.frame = self.frame+1
            pygame.draw.rect(surface,self.color.correct_gamma(0.2),[self.position.x-self.frame, self.position.y-self.frame, self.size+self.frame*2, self.size+self.frame*2])
        else:
            self.frame = 0
            '''
        
        pygame.draw.rect(surface,self.color,[self.position.x, self.position.y, self.size, self.size])

    def reload(self):
        (w, h) = surface.get_size()
        self.position.x = round(random.randrange(0, w - BLOCK_SIZE) / 10.0) * 10.0
        self.position.y = round(random.randrange(0, h - BLOCK_SIZE) / 10.0) * 10.0  
        #logging.debug(f'{self}')

    def _info_str(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

class Segment():
    _position = None
    def __init__(self, position, index = None, size=10, color=pygame.Color("black")):
        self.color = color
        self.size = size
        self.index = index
        self.position = position    #uses @position.setter which does a deep copy
        #logging.debug(f'{self}')

    def draw(self):
        pygame.draw.rect(surface, self.color, [self.x, self.y, self.size, self.size])

    @property
    def position(self):
        return self._position if self._position else None

    @position.setter
    def position(self, value):
        #logging.debug(f'{self} new position {value}')
        self._position = Position(*value.as_list())
        #self.x = self.position.x
        #self.y = self.position.y   
        #logging.debug(f'new position {self.position}, {self.x}, {self.y}')

    @property
    def x(self):
        return self.position.x if self.position else None

    @property
    def y(self):
        return self.position.y if self.position else None

    @x.setter
    def x(self, value):
        #logging.debug(f'{self} new x {value}')
        self.position.x = value

    @y.setter
    def y(self, value):
        #logging.debug(f'{self} new y {value}')
        self.position.y = value             

    def _info_str(self) -> str:
        return f'{self}'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(position: {self.position}, x: {self.x}, y: {self.y}, color: {self.color}, index: {self.index})'

class Snake():
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP = 'UP'
    DOWN = 'DOWN'
    direction = None

    size = BLOCK_SIZE
    step = BLOCK_SIZE
    lenght = 1
    body = None

    def __init__(self, position, color=SNAKE_1_COLOR, head_color=SNAKE_1_HEAD_COLOR, name='Player 1'):
        self.name = name
        self.color = color
        self.head_color = head_color
        #self.head = SnakeSegment(position, color=self.head_color, size=self.size)
        #self.body.append(self.head)
        head_segment = Segment(position, index=f'{self.name}:head', color=self.head_color, size=self.size)
        self.body = [ head_segment ]
        
    def draw(self):
        for i, segment in enumerate(self.body):
            segment.draw()
            #if i == 0:
            #    pygame.draw.rect(DISPLAY, self.head_color, [segment.x, segment.y, self.size, self.size])
            #else:
            #    pygame.draw.rect(DISPLAY, self.color, [segment.x, segment.y, self.size, self.size])
            #DISPLAY.fill(self.color,  [segment.x, segment.y, self.size, self.size])
            #pygame.draw.rect(DISPLAY, segment.color, [segment.x, segment.y, segment.size, segment.size])

    def set_direction(self, direction):
        self.direction = direction

    def eat(self, quantity=1):
        self.lenght += quantity

    @property
    def head(self):
        if self.body and len(self.body)>0:
            return self.body[0]
        else:
            return None

    @property
    def position(self):
        return self.head.position if self.head else None

    @property
    def x(self):
        return self.head.x if self.head else None

    @property
    def y(self):
        return self.head.y if self.head else None     

    def update(self):
        self._update_body_by_insert()
        self._update_head()


    def _update_body_by_insert(self):
        '''
        insert an element at current head position to the beginning of the body
        head will be moved afterwards
        extra tailing body segments will be cut at lenght
        '''
        new_segment = Segment( self.position, color=self.color, size=self.size )
        self.body.insert(1, new_segment )
        #logging.debug(f'{self}')
        if len(self.body) > self.lenght:
            #self.body.pop( len(self.body)-1 )
            #self.body.pop(-1)
            del self.body[-1]        
    
    def _update_head(self):
        if self.direction == self.LEFT:
            self.head.x += -self.step
            #self.head.y += 0
        elif self.direction == self.RIGHT:
            self.head.x += self.step
            #self.head.y += 0
        elif self.direction == self.UP:
            #self.head.x += 0
            self.head.y += -self.step      
        elif self.direction == self.DOWN:
            #self.head.x += 0
            self.head.y += self.step

        #check border collisions and wraparound
        if self.head.x >= surface.get_size()[0]: self.head.x = 0
        if self.head.x < 0: self.head.x = surface.get_size()[0] - self.step
        if self.head.y >= surface.get_size()[1]: self.head.y = 0
        if self.head.y < 0: self.head.y = surface.get_size()[1] - self.step

    def _info_str(self) -> str:
        s = ''
        s += f'{self.__class__.__name__}(name: {self.name}, lenght: {self.lenght}, body lenght: {len(self.body)}'
        for i, segment in enumerate(self.body):
            try:
                s += f'\n{i}:{segment}'
            except Exception as e:
                logging.exception(f'error extracting segment from body')
        return s

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name: {self.name}, lenght: {self.lenght}, body lenght: {len(self.body)}, position: {self.position}, x: {self.x}, y: {self.y}), color: {self.color}'

def add_snakes(n = 4):
    snakes = []
    for i in range(n):
        index = i+1
        color = globals()[f'SNAKE_{index}_COLOR'] if f'SNAKE_{index}_COLOR' in globals() else DEBUG_COLOR
        head_color = color.correct_gamma(0.5) #globals()[f'SNAKE_{index}_HEAD_COLOR'] if f'SNAKE_{index}_HEAD_COLOR' in globals() else DEBUG_COLOR
        name = f'Player {index}'
        x = surface.get_size()[0]//2 + index * BLOCK_SIZE * 2
        y = surface.get_size()[1]//2 + index * BLOCK_SIZE * 2
        #p = Position( x, y )
        #s = Snake(p, color=color, head_color=head_color, name=name)
        snakes.append( Snake(Position( x, y ), color=color, head_color=head_color, name=name) )
    return snakes


def add_food(items = 1):
    (w, h) = surface.get_size()
    foods = []
    for n in range(items):
        foodx = round(random.randrange(0, w - BLOCK_SIZE) / 10.0) * 10.0
        foody = round(random.randrange(0, h - BLOCK_SIZE) / 10.0) * 10.0   

        f = Food( Position(foodx, foody) ) 
        foods.append(f)
    return foods

def chk_collision(s, f):
    #TODO collision display and snake
    #TODO collision snake and snake

    #collision snake and food
    if s.position == f.position:
        s.eat()
        logging.debug(f'eat: {s}, {f}')
        f.reload()

def _display_pause():
    #font = pygame.font.Font('./asset/8-BIT WONDER.TTF', 32)
    font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
    pause_text = font.render('PAUSE', True, FONT_COLOR)
    pause_text_rect = pause_text.get_rect()
    pause_text_rect.center = (surface.get_size()[0]//2, surface.get_size()[1]//2)
    surface.blit(pause_text, pause_text_rect)

def _display_helpers(s, f):
    if s.x == f.x or s.y == f.y:
        if s.x == f.x:
            if s.y < f.y:
                helpery = s.y + BLOCK_SIZE 
            else:
                helpery = f.y + BLOCK_SIZE 

            if s.y < f.y:
                helperh = f.y - helpery 
            else:
                helperh = s.y - helpery 
            helperx = s.x
            helperw = BLOCK_SIZE

        if s.y == f.y:
            if s.x < f.x:
                helperx = s.x + BLOCK_SIZE  
            else:
                helperx = f.x + BLOCK_SIZE  

            if s.x < f.x:
                helperw = f.x - helperx 
            else:
                helperw = s.x - helperx 
            helpery = s.y
            helperh = BLOCK_SIZE            

        '''
        helperx = min(s.x, f.x)
        helpery = min(s.y, f.y)
        helperw = max(max(s.x, f.x) - helperx, BLOCK_SIZE)
        helperh = max(max(s.y, f.y) - helpery, BLOCK_SIZE)
        '''
        #logging.debug(f'helpers: x: {helperx}, y: {helpery}, w: {helperw}, h: {helperh}')
        pygame.draw.rect(surface, HELPER_COLOR, [helperx, helpery, helperw, helperh], 3)
    pass

def _display_score( snakes ):
    font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
    for i, s in enumerate(snakes):
        score_text = font.render(f'{ (s.lenght-1) * 10 }', True, s.color)
        #score_text_rect = score_text.get_rect()
        surface.blit(score_text, ( 20, 10 +(i*50)) )

#DEBUG only
def _display_snake(s):
    for segment in s.body:
        pygame.draw.rect(surface, s.color, [segment.x, segment.y, s.size, s.size])

def _display_grid():
    for x in range(0, surface.get_size()[0], BLOCK_SIZE ):
        for y in range(0,  surface.get_size()[1], BLOCK_SIZE):
            width = 3 if ((x % 100 == 0) and (y % 100 == 0)) else 1
            pygame.draw.line(surface, pygame.Color('gray30'), (x, 0), (x, surface.get_size()[1]), width)
            pygame.draw.line(surface, pygame.Color('gray30'), (0, y), (surface.get_size()[0], y), width)

def _display_mouse_coordinates():
    font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
    mouse_text = font.render(f'{ pygame.mouse.get_pos() }', True, DEBUG_COLOR)
    surface.blit(mouse_text, ( pygame.mouse.get_pos() )) 

def _display_time(t):
# change milliseconds into minutes, seconds, milliseconds
    t_minutes = str(t/60000).zfill(2)
    t_seconds = str( (t%60000)/1000 ).zfill(2)
    t_millisecond = str(t%1000).zfill(3)

    #t_string = f'{t_minutes}:{t_seconds}:{t_millisecond}'
    t_string = f'{t}'
    font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
    t_string_rect = font.render( t_string, True, DEBUG_COLOR)
    surface.blit(t_string_rect, (surface.get_size()[0]//2, surface.get_size()[1]//2-30))     

def _display_debug_info(objects):
    font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
    for i, o in enumerate(objects):
        text = font.render(f'{ o.position }', True, o.color if o.color else DEBUG_COLOR)
        surface.blit(text, ( 100, 20+(i*24) ))    

def _print_debug_info(objects):
    for i, o in enumerate(objects):
        logging.debug(f'{o._info_str()}')

def startgame():
    global surface
    pygame.init()
    width = 800
    height = 600
    surface = pygame.display.set_mode((width,height))
    ui_manager = pygame_gui.UIManager(surface.get_size())
    ui_manager.set_visual_debug_mode(True)
    #pygame.display.update()
    pygame.display.set_caption('Snake game')
    
    game_over = False
    pause = False
    display_debug = False
    
    snakes = add_snakes()
    foods = add_food( len(snakes) )
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks() 
    while not game_over:
        time_delta = clock.tick(FPS)
        for event in pygame.event.get():
            #logging.debug(event)   #prints out all the actions that take place on the screen
            if event.type==pygame.QUIT:
                game_over=True    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    snakes[0].set_direction(Snake.LEFT)
                elif event.key == pygame.K_RIGHT:
                    snakes[0].set_direction(Snake.RIGHT)
                elif event.key == pygame.K_UP:
                    snakes[0].set_direction(Snake.UP)
                elif event.key == pygame.K_DOWN:
                    snakes[0].set_direction(Snake.DOWN)    

                if event.key == pygame.K_a:
                    snakes[1].set_direction(Snake.LEFT)
                elif event.key == pygame.K_d:
                    snakes[1].set_direction(Snake.RIGHT)
                elif event.key == pygame.K_w:
                    snakes[1].set_direction(Snake.UP)
                elif event.key == pygame.K_s:
                    snakes[1].set_direction(Snake.DOWN)                      
    
                if event.key == pygame.K_F12:
                    display_debug = not display_debug

                if event.key == pygame.K_F12 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    _print_debug_info( [*snakes, food] )

                if event.key == pygame.K_SPACE:
                    pause = not pause
                if event.key == pygame.K_ESCAPE:
                    game_over = True 
             
            ui_manager.process_events(event)

        surface.fill(BACKGROUND_COLOR)

        if not pause: 
            for snake in snakes:
                snake.update()
                for food in foods:
                    chk_collision(snake, food)

            count_time = pygame.time.get_ticks() - start_time
            #_display_time(count_time)
        

        for snake in snakes:
            snake.draw()
            for food in foods:
                food.draw()
                _display_helpers(snake, food)
        
        
        _display_score( snakes )
        

        if pause: _display_pause()

        if display_debug:
            _display_grid()
            _display_mouse_coordinates()
            _display_debug_info( [*snakes, food] )        
        
        ui_manager.update(time_delta)
        ui_manager.draw_ui(surface)
        pygame.display.update()
        

        
    
    pygame.quit()
    quit()    


if __name__ == "__main__":
    startgame()