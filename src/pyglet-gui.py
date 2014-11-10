#! /usr/bin/env python

import random
import events


img1= pyglet.image.load('logo.gif')
img2 = pyglet.image.load('logo1.gif')
img3 = pyglet.image.load('playgame.png')
img4 = pyglet.image.load('about.png')
img5 = pyglet.image.load('exit.png')
img6 = pyglet.image.load('ship.jpg')




class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
  
        self.grid = []
  
        for y in range(0, height):
            for x in range(0, width):
                self.grid.append(Tile((x, y)))

    def __getitem__(self, key):
        return self.grid[key]
  
    def __setitem__(self, key, value):
        self.grid[key] = value

    def getPos(self, row, col):
        if -1 in [row, col]:
            return -1
  
        if row >= self.width or col >= self.width:
            return -1
  
        if row * self.width + col > self.width * self.height - 1:
            return -1
  
        return row * self.width + col
  
    def up(self, pos):
        return max(-1, pos - self.width)
  
    def down(self, pos):
        if pos + self.width >= self.width * self.height:
            return -1
        else:
            return pos + self.width
  
    def left(self, pos):
        if not pos % self.width:
            return -1
        else:
            return pos - 1
  
    def right(self, pos):
        if not (pos + 1) % self.width:
            return -1
        else:
            return pos + 1
  
    def upleft(self, pos):
        if self.up(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos - self.width - 1
  
    def upright(self, pos):
        if self.up(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos - self.width + 1
  
    def downleft(self, pos):
        if self.down(pos) == -1 or \
           self.left(pos) == -1:
            return -1
        else:
            return pos + self.width - 1
  
    def downright(self, pos):
        if self.down(pos) == -1 or \
           self.right(pos) == -1:
            return -1
        else:
            return pos + self.width + 1

class Battleship_Grid(Grid):
    def __init__(self, width = 9, height = 10, totalShips = 4, local = False):
        self.active = False

        self.width = width
        self.height = height
        self.totalShips = totalShips

        self.reset()

        self.x = 0
        self.y = 0
        self.offset_x = 120
        self.offset_y = 120

    def reset(self):
        Grid.__init__(self, width = self.width, height = self.height)
        self.createBattleship_Grid()

        self.gameOver = False

    def draw(self, offset_x, offset_y):
        for tile in self.grid:
            tile.draw(offset_x, offset_y)

    def createBattleship_Grid(self):
        # place the ships randomly
        # Help Coding Ships
        pass

    def revealPos(self, pos):
        if pos == -1 or self.grid[pos].revealed:
            return

        self.grid[pos].revealed = True

        self.revealPos(self.up(pos))
        self.revealPos(self.left(pos))
        self.revealPos(self.right(pos))
        self.revealPos(self.down(pos))
  
        self.revealPos(self.upleft(pos))
        self.revealPos(self.upright(pos))
        self.revealPos(self.downleft(pos))
        self.revealPos(self.downright(pos))

    def checkPos(self, pos):
        return pos > -1 and \
               not self.grid[pos].revealed


if __name__ == '__main__':
    import pyglet
    from pyglet import window
    from pyglet import clock
    from pyglet.gl import *
    from pyglet.window import mouse
        

window = pyglet.window.Window(800, 600, caption = "CSC446")


@window.event
def on_draw():
        window.clear()
        img1.blit(225,500)
        img2.blit(315,470)
        img3.blit(350,350)
        img4.blit(370,250)
        img5.blit(380,150)
        img6.blit(25,200)

def on_mouse_press(x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
                img1.x = x;
                img1.y = y;




pyglet.app.run()
