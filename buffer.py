import sys, time
from numpy import interp


class Progress:
    def __init__(self, value, end, title='Downloading',buffer=50):
        self.title = title
        self.end = end
        self.buffer = buffer
        self.value = value
        self.progress()

    def progress(self):
        maped = int(interp(self.value, [1, self.end], [0, self.buffer]))
        print(f'{self.title}: [{"#"*maped}{"-"*(self.buffer - maped)}]', end='\r')