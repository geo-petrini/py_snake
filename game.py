from pickletools import UP_TO_NEWLINE
from tkinter import RIGHT
from turtle import position
import pygame
from pygame import Surface, transform, Rect
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

FPS = 15

window = None

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
        #self.surface = Surface((self.width+self.width//3, self.height+self.height//3))
        #self.surface.set_colorkey((0, 0, 0))
        #self.surface.fill(color)
        #self.rect = self.surface.get_rect() 
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

    @property
    def center(self):
        return ( self.x+self.width//2, self.y+self.height//2 )

    def draw(self):
        #self.OLD__draw_rotating_surface()
        self.__draw_rotating_surface()
        '''
        if self.frame <= 3:
            self.frame = self.frame+1
            pygame.draw.rect(surface,self.color.correct_gamma(0.2),[self.position.x-self.frame, self.position.y-self.frame, self.size+self.frame*2, self.size+self.frame*2])
        else:
            self.frame = 0
            '''
        
        pygame.draw.rect(window, self.color,[self.x, self.y, self.size, self.size])

    def OLD__draw_rotating_surface(self):
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x + self.size//2, self.y + self.size//2)    
    
        self.rotation = self.rotation + 2
        old_center = self.rect.center
        new = transform.rotate(self.surface, self.rotation)
        self.rect = new.get_rect()
        self.rect.center = old_center
        window.blit(new, self.rect)   

    def __draw_rotating_surface(self):
        image = pygame.Surface((self.width+self.width//3, self.height+self.height//3), pygame.SRCALPHA)
        #image = pygame.Surface( (self.size, self.size), pygame.SRCALPHA)
        image.fill( self.color.correct_gamma(0.1) )  # refill the surface color if you change it somewhere in the program
        x = 0
        y = 0
        self.rotation = self.rotation + 2
        #blit_rotate_center(window, s, (self.x, self.x), self.rotation)
        #w, h = pygame.display.get_surface().get_size()
        #new_surf, new_rect = rot_center(s, self.rotation, 0,0)
        # r = s.get_rect()
        #r.center = (self.x + self.size//2, self.y + self.size//2)    
    
        #old_center = r.center
        rotated_image = pygame.transform.rotate(image, self.rotation)
        new_rect = rotated_image.get_rect(center = image.get_rect().center)
        new_rect.center = ( self.x+self.width//2, self.y+self.height//2 )
        new_rect.center = self.center
        window.blit(rotated_image, new_rect.topleft)          

    def reload(self):
        (w, h) = window.get_size()
        self.position.x = round(random.randrange(0, w - self.size) / self.size) * self.size
        self.position.y = round(random.randrange(0, h - self.size) / self.size) * self.size
        #logging.debug(f'{self}')

    def _info_str(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

class Segment():
    _position = None
    def __init__(self, position, index = None, size=10, color=pygame.Color("darkgray")):
        self.color = color
        self.size = size
        self.index = index
        self.position = position    #uses @position.setter which does a deep copy
        #logging.debug(f'{self}')

    def draw(self, direction=None):
        pygame.draw.rect(window, self.color, [self.x, self.y, self.size, self.size])
        if self.index != None and 'head' in self.index:
            self.__render_head(window, direction)

    def __render_head(self, window, direction):
            '''
            draw a face in the head segment
            rotate the head segment by 90°
            ! the rect x,y will be the same as the original x,y as by https://camo.githubusercontent.com/e3b9946d5ecde4d11a3d4eca0b8f88bcb64969acd8621891a6868faaa0bef1e0/68747470733a2f2f692e737461636b2e696d6775722e636f6d2f76726867742e676966
            '''
            try:
                if self.head_animation_opening and self.head_animation_frame < 4:
                    self.head_animation_frame += 1
                else:
                    self.head_animation_opening = False

                if not self.head_animation_opening and self.head_animation_frame > 0:
                    self.head_animation_frame -= 1
                else:
                    self.head_animation_opening = True

            except Exception as e:
                self.head_animation_frame = 0
                self.head_animation_opening = True

            head_surface = pygame.Surface( (self.size, self.size) )
            pygame.draw.rect(head_surface, self.color, [0, 0, self.size, self.size])    #draw background

            mouth_color = pygame.Color("black")
            mouth_line_width = self.size // 10
            mouth_x1 = self.size // 4
            mouth_y1 = self.size // 8
            mouth_x2 = self.size - mouth_x1
            mouth_y2 = mouth_y1 + mouth_line_width*self.head_animation_frame
            mouth_start = (mouth_x1 , mouth_y1)
            mouth_end = (mouth_x2, mouth_y2)

            pygame.draw.ellipse(head_surface, mouth_color, pygame.Rect( mouth_x1, mouth_y1, mouth_x2-mouth_x1, mouth_y2-mouth_y1), width=mouth_line_width)    #draw mouth
            
            #pygame.draw.line(head_surface, mouth_color, mouth_start, mouth_end, mouth_line_width)
            new = head_surface
            if direction == Snake.UP:
                pass
            if direction == Snake.RIGHT:
                #rotate 90deg 
                new = pygame.transform.rotate(head_surface, -90)
            if direction == Snake.DOWN:
                #rotate 180deg
                new = pygame.transform.rotate(head_surface, 90*2)
            if direction == Snake.LEFT:
                #rotate 270deg
                new = pygame.transform.rotate(head_surface, -90*3)
            #pygame.transform.rotate(head_surface, angle)
            draw_area = head_surface.get_rect().move(self.x, self.y)        
            window.blit(new, draw_area)

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
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    direction = None

    size = BLOCK_SIZE
    step = BLOCK_SIZE
    lenght = 1
    body = None

    def __init__(self, position, color=SNAKE_1_COLOR, head_color=None, name='Player 1', keys={'left':None, 'right':None}, direction=None):
        self.name = name
        self.color = color
        self.head_color = head_color if head_color else self.color.correct_gamma(0.5)
        self.left_key = keys['left']
        self.right_key = keys['right']
        self.direction = direction
        #self.head = SnakeSegment(position, color=self.head_color, size=self.size)
        #self.body.append(self.head)
        head_segment = Segment(position, index=f'{self.name}:head', color=self.head_color, size=self.size)
        self.body = [ head_segment ]
        
    def draw(self):
        for i, segment in enumerate(self.body):
            segment.draw(self.direction)
            #if i == 0:
            #    pygame.draw.rect(DISPLAY, self.head_color, [segment.x, segment.y, self.size, self.size])
            #else:
            #    pygame.draw.rect(DISPLAY, self.color, [segment.x, segment.y, self.size, self.size])
            #DISPLAY.fill(self.color,  [segment.x, segment.y, self.size, self.size])
            #pygame.draw.rect(DISPLAY, segment.color, [segment.x, segment.y, segment.size, segment.size])

    def set_direction(self, direction):
        self.direction = direction
        
    def rotate_left(self):
        if self.direction == None: self.direction = Snake.LEFT
    
        if self.direction == Snake.UP:
            self.direction = Snake.LEFT
        else:
            self.direction = self.direction -1
        
    def rotate_right(self):
        if self.direction == None: self.direction = Snake.RIGHT
        if self.direction == Snake.LEFT:
            self.direction = Snake.UP
        else:
            self.direction = self.direction +1

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
        if self.head.x >= window.get_size()[0]: self.head.x = 0
        if self.head.x < 0: self.head.x = window.get_size()[0] - self.step
        if self.head.y >= window.get_size()[1]: self.head.y = 0
        if self.head.y < 0: self.head.y = window.get_size()[1] - self.step

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

class Game():

    def __init__(self):
        global window
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        
        self.__game_over = False
        self.__pause = False
        self.__display_debug = False  

        self.__snakes = []
        self.__foods = []
        self.__players_number = 4

        pygame.init()

        self.__window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        window = self.__window
        self.__ui_manager = pygame_gui.UIManager(self.__window.get_size())
        self.__ui_manager.set_visual_debug_mode(True)
        #pygame.display.update()
        pygame.display.set_caption('Snake game')    

        try:
            icon = pygame.image.load('res/icon.png')
            pygame.display.set_icon(icon)
        except:
            pass

    def NOT_IMPLEMENTED__calc_window_size():
        global BLOCK_SIZE
        #min size 800x600
        #min blocks 21x21
        #max size screen width height
        #window must be multiple of BLOCK_SIZE
        screen_info = pygame.display.Info() #Required to set a good resolution for the game screen
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        first_screen = (screen_width, screen_height) #Take 120 pixels from the height because the menu bar, window bar and dock takes space 
        if screen_width < 800 or screen_height < 600:
            pygame.QUIT

        if screen_width == 800 and screen_height == 600:
            #adjust block size so that min blocks 21x21 is satisfied
            pass

        #check if min blocks 21x21 is < thand screen size

        #else
        width = BLOCK_SIZE * 21
        height = BLOCK_SIZE * 21


    
    @property
    def width(self):
        return self.WINDOW_WIDTH
    
    @property
    def height(self):
        return self.WINDOW_HEIGHT
        
    @property
    def snakes(self):
        return self.__snakes
        
    @property
    def foods(self):
        return self.__foods

    def add_snakes(self, n = 1):
        for i in range(n):
            index = i+1
            color = globals()[f'SNAKE_{index}_COLOR'] if f'SNAKE_{index}_COLOR' in globals() else DEBUG_COLOR
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
        if index == 1:
            x = window.get_size()[0]//2 - 3*BLOCK_SIZE 
            y = window.get_size()[1]//2
            direction = Snake.LEFT

        if index == 2:
            x = window.get_size()[0]//2 + 3*BLOCK_SIZE 
            y = window.get_size()[1]//2
            direction = Snake.RIGHT     

        if index == 3:
            x = window.get_size()[0]//2
            y = window.get_size()[1]//2 - 3*BLOCK_SIZE 
            direction = Snake.UP            

        if index == 4:
            x = window.get_size()[0]//2 
            y = window.get_size()[1]//2 + 3*BLOCK_SIZE 
            direction = Snake.DOWN

        return ( Position(x, y), direction  )            

    def add_food(self, items = 1):
        (w, h) = window.get_size()
        
        for n in range(items):
            # foodx = round(random.randrange(0, w - BLOCK_SIZE) / 10.0) * 10.0
            # foody = round(random.randrange(0, h - BLOCK_SIZE) / 10.0) * 10.0   
            foodx = round(random.randrange(0, w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            foody = round(random.randrange(0, h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE

            f = Food( position=Position(foodx, foody) ) 
            self.foods.append(f)
            logging.debug(f'new food {f}')

    def chk_collision(self, s, f):
        #TODO collision display and snake
        #TODO collision snake and snake

        #collision snake and food
        if s.position == f.position:
            s.eat()
            logging.debug(f'eat: {s}, {f}')
            f.reload()

    def _display_pause(self):
        #font = pygame.font.Font('./asset/8-BIT WONDER.TTF', 32)
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
        pause_text = font.render('PAUSE', True, FONT_COLOR)
        pause_text_rect = pause_text.get_rect()
        pause_text_rect.center = (self.width//2, self.height//2)
        self.__window.blit(pause_text, pause_text_rect)

    def _display_helpers(self, s, f):
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
            pygame.draw.rect(self.__window, HELPER_COLOR, [helperx, helpery, helperw, helperh], 3)
        

    def _display_score(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 32)
        for i, s in enumerate(self.snakes):
            score_text = font.render(f'{ (s.lenght-1) * 10 }', True, s.color)
            #score_text_rect = score_text.get_rect()
            self.__window.blit(score_text, ( 20, 10 +(i*50)) )

    def _display_grid(self):
        for x in range(0, self.__window.get_size()[0], BLOCK_SIZE ):
            for y in range(0, self.__window.get_size()[1], BLOCK_SIZE):
                width = 3 if ((x % 100 == 0) and (y % 100 == 0)) else 1
                pygame.draw.line(self.__window, pygame.Color('gray30'), (x, 0), (x, self.__window.get_size()[1]), width)
                pygame.draw.line(self.__window, pygame.Color('gray30'), (0, y), (self.__window.get_size()[0], y), width)

    def _display_mouse_coordinates(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
        mouse_text = font.render(f'{ pygame.mouse.get_pos() }', True, DEBUG_COLOR)
        self.__window.blit(mouse_text, ( pygame.mouse.get_pos() )) 

    def _display_time(self, t):
    # change milliseconds into minutes, seconds, milliseconds
        t_minutes = str(t/60000).zfill(2)
        t_seconds = str( (t%60000)/1000 ).zfill(2)
        t_millisecond = str(t%1000).zfill(3)

        #t_string = f'{t_minutes}:{t_seconds}:{t_millisecond}'
        t_string = f'{t}'
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
        t_string_rect = font.render( t_string, True, DEBUG_COLOR)
        self.__window.blit(t_string_rect, (self.__window.get_size()[0]//2, self.__window.get_size()[1]//2-30))     

    def _display_debug_info(self, objects):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 18)
        for i, o in enumerate(objects):
            text = font.render(f'{ o.position }', True, o.color if o.color else DEBUG_COLOR)
            self.__window.blit(text, ( 100, 20+(i*24) ))    

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
                    self._print_debug_info( [*snakes, food] )

                if event.key == pygame.K_SPACE:
                    self.__pause = not self.__pause
                if event.key == pygame.K_ESCAPE:
                    self.__game_over = True 
             
            self.__ui_manager.process_events(event)        

    def start(self):

        self.add_snakes( self.__players_number )
        self.add_food( self.__players_number )
        
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks() 
        while not self.__game_over:
            time_delta = clock.tick(FPS)

            self.__window.fill(BACKGROUND_COLOR)
            self._handle_events()
            
            self._display_score()

            if not self.__pause: self._update_snakes()

            count_time = pygame.time.get_ticks() - start_time
            #self._display_time(count_time)

            for snake in self.snakes:
                snake.draw()
                for food in self.foods:
                    food.draw()
                    self.chk_collision(snake, food)
                    self._display_helpers(snake, food)                    

            if self.__display_debug:
                self._display_grid()
                self._display_mouse_coordinates()
                self._display_debug_info( [*self.snakes, food] )        
            
            if self.__pause: self._display_pause()
            
            self.__ui_manager.update(time_delta)
            self.__ui_manager.draw_ui(self.__window)
            pygame.display.update()

        pygame.quit()
        quit()    

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def blit_rotate_center(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

if __name__ == "__main__":
    g = Game()
    g.start()
