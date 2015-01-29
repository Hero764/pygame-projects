import pygame, sys, random
from pygame.locals import *

CELLSZ = 10 # Size of cell in pixels squared
WALLSZ = 2 
START = 0   # ID of the start cell

colors = {'black'  : (0, 0, 0),
          'white'  : (255, 255, 255),
          'red'    : (255, 0, 0),
          'green'  : (0, 255, 0),
          'blue'   : (0, 0, 255),
          'yellow' : (255, 255, 0),
          'cyan'   : (0, 255, 255),
          'magenta': (255, 0, 255)}

def weightedChoice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    for c, w in choices:
        r -= w
        if r < 0:
            return c

def getNeighbor(cellId, direction):
    if direction == 'left':
        return cellId - 1
    if direction == 'right':
        return cellId + 1
    if direction == 'up':
        return cellId - mazeSize
    if direction =='down':
        return cellId + mazeSize

class Cell:
    def __init__(self, idNum, rect):
        self.idNum = idNum
        
        self.leftBorder   = True
        self.rightBorder  = True
        self.topBorder    = True
        self.bottomBorder = True

        self.topLeft     = (rect[0], rect[1])
        self.topRight    = (rect[0] + rect[2], rect[1])
        self.bottomLeft  = (rect[0], rect[1] + rect[3])
        self.bottomRight = (rect[0] + rect[2], rect[1] + rect[3])

        self.color = None

class App:
    def __init__(self, mazeSize, delay):
        pygame.init()
        self.cells = [Cell(i, (CELLSZ * (i%mazeSize), CELLSZ * (i/mazeSize), CELLSZ, CELLSZ)) for i in range(mazeSize*mazeSize)]
        self.screen = pygame.display.set_mode((CELLSZ*mazeSize, CELLSZ*mazeSize))

        self.delay = delay
        self.currentCell = None
        self.running = True 

        self.generating = True
        self.depthSearching = False
        self.breadthSearching = False

        self.visited = set()
        self.stack = []

        self.updateCells = []
        
        self.screen.fill(colors['white'])
        pygame.display.update()

        self.clearMaze()

    def clearMaze(self):
        for cell in self.cells:
            cell.leftBorder   = True
            cell.rightBorder  = True
            cell.topBorder    = True
            cell.bottomBorder = True
            cell.color = None
            
        self.currentCell = random.choice(self.cells)
        self.visited = set()
        self.stack = []
        self.mazeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  
        self.borders = [('left', random.random()), ('right', random.random()), ('up', random.random()), ('down', random.random())]
        
        self.depthSearching   = False
        self.breadthSearching = False

        self.screen.fill(colors['white'])
        pygame.display.update()

    def newSearch(self):
        self.pathColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
        self.currentCell = self.cells[0]
        self.visited = set()
        self.visitQueue = []

        for cell in self.cells:
            cell.color = self.mazeColor
            self.updateCells.append(cell)

        self.draw()
 
    def generateMaze(self): # Performs one step of depth-search maze generation algorithm
        if len(self.visited) == len(self.cells):
            self.generating = False
            return
       
        chosen = set()

        while True:
            border = weightedChoice(self.borders)
            chosen.add(border)
            neighbor = getNeighbor(self.currentCell.idNum, border)
            if border == 'left':
                if ((self.currentCell.idNum % mazeSize) != 0) and (self.cells[neighbor] not in self.visited):
                    self.currentCell.leftBorder = False
                    self.cells[neighbor].rightBorder = False
                    break
            elif border == 'up': 
                if ((self.currentCell.idNum / mazeSize) != 0) and (self.cells[self.currentCell.idNum - mazeSize] not in self.visited):
                    self.currentCell.topBorder = False
                    self.cells[neighbor].bottomBorder = False
                    break
            elif border == 'right':
                if ((self.currentCell.idNum % mazeSize) != (mazeSize-1)) and (self.cells[self.currentCell.idNum + 1] not in self.visited):
                    self.currentCell.rightBorder = False
                    self.cells[neighbor].leftBorder = False
                    break 
            elif border == 'down': 
                if ((self.currentCell.idNum / mazeSize) != (mazeSize-1)) and (self.cells[neighbor] not in self.visited):
                    self.currentCell.bottomBorder = False
                    self.cells[neighbor].topBorder = False
                    break
           
            neighbor = None
            if len(chosen) == 4:
                break
    
        if neighbor == None:
            if not self.stack: # Never happens?
                if self.currentCell.color is None:
                    self.currentCell.color = self.mazeColor
                    self.updateCells.append(self.currentCell)

                self.currentCell = random.choice(self.cells)
                while self.currentCell in self.visited:
                    self.currentCell = random.choice(self.cells)
               
                self.visited.add(self.currentCell)
                self.updateCells.append(self.currentCell)

            else:
                if self.currentCell.color is None: 
                    self.currentCell.color = self.mazeColor
                self.updateCells.append(self.currentCell)

                #self.mazeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                self.currentCell = self.stack.pop()
                self.updateCells.append(self.currentCell)

        else:
            self.stack.append(self.currentCell)
            self.currentCell.color = self.mazeColor 
            self.updateCells.append(self.currentCell) 

            self.currentCell = self.cells[neighbor]
            self.visited.add(self.currentCell)
            self.updateCells.append(self.currentCell)

    def depthSearch(self):
        if self.currentCell == self.cells[-1]: # We found it!
            self.depthSearching = False
            return
        
        if not self.currentCell.leftBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'left')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.rightBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'right')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.topBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'up')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.bottomBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'down')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])

        self.updateCells.append(self.currentCell)
        self.currentCell.color = self.pathColor
        
        self.currentCell = self.visitQueue.pop() 
        self.visited.add(self.currentCell)
        self.updateCells.append(self.currentCell) 
    
    def breadthSearch(self):
        if self.currentCell == self.cells[-1]:
            self.breadthSearching = False
        
        if not self.currentCell.leftBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'left')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.rightBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'right')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.topBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'up')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        if not self.currentCell.bottomBorder:
            neighbor = getNeighbor(self.currentCell.idNum, 'down')
            if self.cells[neighbor] not in self.visited:
                self.visitQueue.append(self.cells[neighbor])
        
        self.updateCells.append(self.currentCell)
        self.currentCell.color = self.pathColor

        self.currentCell = self.visitQueue.pop(0)
        self.visited.add(self.currentCell)
        self.updateCells.append(self.currentCell)

    def draw(self):
        updateRects = []

        for cell in self.updateCells:
            if cell == self.currentCell:
                self.screen.fill(colors['blue'], (cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ))
            elif cell.color == None:
                continue # Don't draw anything
            else:
                self.screen.fill(cell.color, (cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ)) 
            
            if cell.leftBorder and ((cell.idNum != START)): 
                pygame.draw.line(self.screen, colors['black'], cell.topLeft, cell.bottomLeft, WALLSZ)
            if cell.rightBorder and ((cell.idNum != len(self.cells) - 1)):
                pygame.draw.line(self.screen, colors['black'], cell.topRight, cell.bottomRight, WALLSZ)
            if cell.topBorder:
                pygame.draw.line(self.screen, colors['black'], cell.topLeft, cell.topRight, WALLSZ)
            if cell.bottomBorder:
                pygame.draw.line(self.screen, colors['black'], cell.bottomLeft, cell.bottomRight, WALLSZ)
            
            updateRects.append((cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ))
        
        pygame.display.update(updateRects)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if event.key == pygame.K_g:
                    self.clearMaze()
                    self.generating = True
                elif event.key == pygame.K_d and not (self.generating or self.breadthSearching):
                    self.newSearch()
                    self.depthSearching = True
                elif event.key == pygame.K_b and not (self.generating or self.depthSearching):
                    self.newSearch()
                    self.breadthSearching = True

                # Control fps 
                elif event.key == pygame.K_z: #
                    self.delay += 1
                elif event.key == pygame.K_x:
                    self.delay -= 1

    def update(self):
        self.updateCells = []

        if self.generating:
            self.generateMaze()
        elif self.depthSearching:
            self.depthSearch()
        elif self.breadthSearching:
            self.breadthSearch()

    def mainLoop(self):
        while self.running:
            self.draw()
            self.handleEvents()
            self.update() 

            pygame.time.delay(self.delay)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        mazeSize = int(sys.argv[1])
    else:
        mazeSize = 10
    
    if len(sys.argv) >= 3:
        delay = int(sys.argv[2])
    else:
        delay = 10

    app = App(mazeSize, delay)
    app.mainLoop()
