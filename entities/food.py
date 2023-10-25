import pygame
from pygame import Surface, transform
import logging
import random
from entities.globals import *

STATUS_AVAILABLE = 0
STATUS_EATEN = 1

class Food():

    def __init__(self, position, color=GameColor.FOOD_COLOR):
        self.color = color
        self.position = position
      
        #self.surface = Surface((self.width+self.width//3, self.height+self.height//3))
        #self.surface.set_colorkey((0, 0, 0))
        #self.surface.fill(color)
        #self.rect = self.surface.get_rect() 
        self.rotation = 0
        #logging.debug(f'{self}')
        self.status = STATUS_AVAILABLE
   
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

    @property
    def size(self):
        return Grid.BLOCK_SIZE
    @property
    def width(self):
        return Grid.BLOCK_SIZE
    @property
    def height(self):
        return Grid.BLOCK_SIZE

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
        
        pygame.draw.rect(GameConfig.WINDOW, self.color,[self.x, self.y, self.size, self.size])

    def OLD__draw_rotating_surface(self):
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x + self.size//2, self.y + self.size//2)    
    
        self.rotation = self.rotation + 2
        old_center = self.rect.center
        new = transform.rotate(self.surface, self.rotation)
        self.rect = new.get_rect()
        self.rect.center = old_center
        GameConfig.WINDOW.blit(new, self.rect)   

    def __draw_rotating_surface(self):
        image = pygame.Surface((self.width+self.width//3, self.height+self.height//3), pygame.SRCALPHA)
        #image = pygame.Surface( (self.size, self.size), pygame.SRCALPHA)
        image.fill( self.color.correct_gamma(0.1) )  # refill the surface color if you change it somewhere in the program
        x = 0
        y = 0
        self.rotation = self.rotation + 2

        rotated_image = pygame.transform.rotate(image, self.rotation)
        new_rect = rotated_image.get_rect(center = image.get_rect().center)
        new_rect.center = ( self.x+self.width//2, self.y+self.height//2 )
        new_rect.center = self.center
        GameConfig.WINDOW.blit(rotated_image, new_rect.topleft)          

    def reset(self):
        (w, h) = GameConfig.WINDOW.get_size()

        self.position.x = round(random.randrange(0, w - self.size) / self.size) * self.size
        self.position.y = round(random.randrange(0, h - self.size) / self.size) * self.size
        logging.info(f'position reset {self}')

    def _info_str(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.position})'