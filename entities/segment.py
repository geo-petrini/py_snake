import pygame
from entities.globals import *
from entities.position import *

class Segment():
    _position = None
    def __init__(self, position, index = None, color=pygame.Color("darkgray")):
        self.color = color
        self.index = index
        self.position = position    #uses @position.setter which does a deep copy
        #logging.debug(f'{self}')
    @property
    def size(self):
        return Grid.BLOCK_SIZE
    @property
    def width(self):
        return Grid.BLOCK_SIZE
    @property
    def height(self):
        return Grid.BLOCK_SIZE

    def draw(self, direction=None):
        pygame.draw.rect(GameConfig.WINDOW, self.color, [self.x, self.y, self.size, self.size])
        if self.index != None and 'head' in self.index:
            self.__render_head(direction)

    def __render_head(self, direction):
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
            if direction == DIRECTION_UP:
                pass
            if direction == DIRECTION_RIGHT:
                #rotate 90deg 
                new = pygame.transform.rotate(head_surface, -90)
            if direction == DIRECTION_DOWN:
                #rotate 180deg
                new = pygame.transform.rotate(head_surface, 90*2)
            if direction == DIRECTION_LEFT:
                #rotate 270deg
                new = pygame.transform.rotate(head_surface, -90*3)
            #pygame.transform.rotate(head_surface, angle)
            draw_area = head_surface.get_rect().move(self.x, self.y)        
            GameConfig.WINDOW.blit(new, draw_area)

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