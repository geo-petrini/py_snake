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