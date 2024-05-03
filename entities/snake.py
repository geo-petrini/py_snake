from entities.globals import *
from entities.segment import Segment
import entities.position as position

import logging

STATUS_INIT = 0
STATUS_ALIVE = 1
STATUS_DEAD = 2

class Snake():

    direction = None

    lenght = 1
    body = None

    def __init__(self, position, color=GameColor.SNAKE_1_COLOR, head_color=None, name='Player 1', keys={'left':None, 'right':None}, direction=None):
        self.status = STATUS_INIT
        self.name = name
        self.color = color
        self.head_color = head_color if head_color else self.color.correct_gamma(0.5)
        self.left_key = keys['left']
        self.right_key = keys['right']
        self.direction = direction
        
        self.body = []
        self._add_head(position)
        self.status = STATUS_ALIVE
        
    def _add_head(self, position):
        head_segment = Segment(position, index=f'{self.name}:head', color=self.head_color)
        self.body.append( head_segment )

    def draw(self):
        if len(self.body) > 0:
            #paint in reverse so that head is drawn last, this allows it to be displayed above the other segments in case of overlapping
            for i, segment in enumerate(reversed(self.body)):
                if segment.is_head():
                    segment.direction = self.direction
                segment.draw()

    def _render_info(self):
        font = pygame.font.Font('./asset/Fipps-Regular.otf', 10)
        output = f'lenght: {self.lenght}\n'
        output += f'left: {pygame.key.name(self.left_key)}\n'
        output += f'right: {pygame.key.name(self.right_key)}'
        text = font.render(output, True, self.color if self.color else GameColor.DEBUG_COLOR)
        text_x = self.x
        text_y = self.y
        text_speed = self.step / 2
        text_max_distance = 100

        # TODO keep checking if the new position is valid (not overlapping with other grid items)
        try:
            dx = self.x - self._info_coords[0]
            dy = self.y - self._info_coords[1]
            distance = position.distance(self.x, self.y, int(self._info_coords[0]), int(self._info_coords[1]))
            direction = position.direction(dx, dy, distance)
            if distance > text_max_distance:
                self._info_coords = self._info_coords[0] + direction[0] * text_speed, self._info_coords[1] + direction[1] * text_speed
        except AttributeError as e:
            self._info_coords = Grid.get_position_near( text.get_rect(), (self.x, self.y))
        except Exception as e:
            logging.exception(f'error rendering info for snake {self}')
            

        
        if self._info_coords:
            text_x = self._info_coords[0]
            text_y = self._info_coords[1]
        else:
            logging.warning(f'commands coords: {self._info_coords}')

        # text.get_rect().move_ip(text_x, text_y)# does not seem to work
        pygame.draw.line(GameConfig.WINDOW, self.color.correct_gamma(0.3), (text.get_rect().center[0]+text_x, text.get_rect().center[1]+text_y), self.head.get_rect().center, 3)
        GameConfig.WINDOW.blit(text, ( text_x, text_y ))        

    def set_direction(self, direction):
        self.direction = direction
        
    def rotate_left(self):
        if self.direction == None: self.direction = DIRECTION_LEFT
    
        if self.direction == DIRECTION_UP:
            self.direction = DIRECTION_LEFT
        else:
            self.direction = self.direction -1
        
    def rotate_right(self):
        if self.direction == None: self.direction = DIRECTION_RIGHT
        if self.direction == DIRECTION_LEFT:
            self.direction = DIRECTION_UP
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

    @property
    def size(self):
        return Grid.BLOCK_SIZE

    @property
    def step(self):
        return Grid.BLOCK_SIZE

    def die(self):
        self.status = STATUS_DEAD

    def is_alive(self):
        if self.status != STATUS_DEAD: 
            return True 
        else: 
            return False

    def collide_vs_snake(self, target):
        # TODO alternative check with collidepoint(), colliderect(), collidelist(), collideobjects()
        if isinstance(target, Snake):
            for segment in target.body:
                if self == target and segment.is_head(): continue # head to head self collision is not possible
                if self.head.position == segment.position: # return True only if head collides with a segment
                    return True
        return False

    def move(self):
        self.update()

    def update(self):
        self._update_body_by_insert()
        self._update_head()

    def _update_body_by_insert(self):
        '''
        insert an element at current head position to the beginning of the body
        head will be moved afterwards
        extra tailing body segments will be cut at lenght
        '''
        new_segment = Segment( self.position, color=self.color)
        self.body.insert(1, new_segment )
        #logging.debug(f'{self}')
        if len(self.body) > self.lenght:
            #self.body.pop( len(self.body)-1 )
            #self.body.pop(-1)
            del self.body[-1]        
    
    def _update_head(self):
        if self.direction == DIRECTION_LEFT:
            self.head.x += -self.step
        elif self.direction == DIRECTION_RIGHT:
            self.head.x += self.step
        elif self.direction == DIRECTION_UP:
            self.head.y += -self.step      
        elif self.direction == DIRECTION_DOWN:
            self.head.y += self.step

        #check border collisions and wraparound
        if self.head.x >= pygame.display.get_surface().get_size()[0]: self.head.x = 0
        if self.head.x < 0: self.head.x = pygame.display.get_surface().get_size()[0] - self.step
        if self.head.y >= pygame.display.get_surface().get_size()[1]: self.head.y = 0
        if self.head.y < 0: self.head.y = pygame.display.get_surface().get_size()[1] - self.step

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
