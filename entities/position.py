from entities.globals import *
from multipledispatch import dispatch

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
    
    @property
    def grid_col(self):
        #pixel position / Block size
        return self.x / GameConfig.BLOCK_SIZE

    @property
    def grid_row(self):
        #pixel position / Block size
        return self.y / GameConfig.BLOCK_SIZE        
    
@dispatch(Position, Position)
def distance(origin:Position, target:Position):
    dx = origin.x - target.x
    dy = origin.y - target.y
    return (dx ** 2 + dy ** 2) ** .5

@dispatch(tuple, tuple)
def distance(origin:tuple, target:tuple):
    dx = origin[0] - target[0]
    dy = origin[1] - target[1]
    return (dx ** 2 + dy ** 2) ** .5

@dispatch(list, list)
def distance(origin:list, target:list):
    dx = origin[0] - target[0]
    dy = origin[1] - target[1]
    return (dx ** 2 + dy ** 2) ** .5

@dispatch(int, int, int, int)
def distance(x1:int, y1:int, x2:int, y2:int):
    dx = x1 - x2
    dy = y1 - y2
    return (dx ** 2 + dy ** 2) ** .5

@dispatch(float, float, float, float)
def distance(x1:float, y1:float, x2:float, y2:float):
    dx = x1 - x2
    dy = y1 - y2
    return (dx ** 2 + dy ** 2) ** .5

def direction(dx, dy, distance):
    return dx / distance, dy / distance