from entities.globals import *
from entities.segment import Segment

import logging

class Snake():

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
        if self.direction == DIRECTION_LEFT:
            self.head.x += -self.step
            #self.head.y += 0
        elif self.direction == DIRECTION_RIGHT:
            self.head.x += self.step
            #self.head.y += 0
        elif self.direction == DIRECTION_UP:
            #self.head.x += 0
            self.head.y += -self.step      
        elif self.direction == DIRECTION_DOWN:
            #self.head.x += 0
            self.head.y += self.step

        #check border collisions and wraparound
        if self.head.x >= WINDOW.get_size()[0]: self.head.x = 0
        if self.head.x < 0: self.head.x = WINDOW.get_size()[0] - self.step
        if self.head.y >= WINDOW.get_size()[1]: self.head.y = 0
        if self.head.y < 0: self.head.y = WINDOW.get_size()[1] - self.step

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