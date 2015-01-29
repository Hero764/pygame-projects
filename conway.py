import pygame, sys, random
from pygame.locals import *

CELLSZ = 20

class Cell:
    def __init__(self, idNum, rect):
        self.idNum = idNum
        
        self.topLeft     = (rect[0], rect[1])
        self.topRight    = (rect[0] + rect[2], rect[1])
        self.bottomLeft  = (rect[0], rect[1] + rect[3])
        self.bottomRight = (rect[0] + rect[2], rect[1] + rect[3])

        self.alive = False

class GameOfLife:
    def __init__(self, size):
        pygame.init() 
      
        self.screen = pygame.display.set_mode((CELLSZ * size, CELLSZ * size))
        self.screen.fill((255,255,255))
        pygame.display.flip()

        self.size = size
        self.delay = 100

        self.running = False
        self.playing = False
        self.setting = True

        self.cells = [Cell(i, (CELLSZ * (i%size), CELLSZ * (i/size), CELLSZ, CELLSZ)) for i in range(size*size)]
        self.updateCells = []

    def getNeighbors(self, cellId):
        neighbors = []
        if self.validNeighbor(cellId, 'left'):
            neighbors.append(self.cells[cellId-1]) # Left
            if self.validNeighbor(cellId, 'up'):
                neighbors.append(self.cells[cellId - (self.size+1)]) # Upper left
            if self.validNeighbor(cellId, 'down'):
                neighbors.append(self.cells[cellId + (self.size-1)]) # Lower left

        if self.validNeighbor(cellId, 'right'):
            neighbors.append(self.cells[cellId+1]) # Right
            if self.validNeighbor(cellId, 'up'):
                neighbors.append(self.cells[cellId - (self.size-1)]) # Upper right
            if self.validNeighbor(cellId, 'down'):
                neighbors.append(self.cells[cellId + (self.size+1)]) # Lower right

        if self.validNeighbor(cellId, 'up'):
                neighbors.append(self.cells[cellId-self.size]) # Up
        if self.validNeighbor(cellId, 'down'):
                neighbors.append(self.cells[cellId+self.size]) # Down
        return neighbors

    def validNeighbor(self, cellId, direction):
        if direction == 'left':
            return (cellId % self.size) != 0
        if direction == 'right':
            return (cellId % self.size) != (self.size-1)
        if direction == 'up':
            return (cellId / self.size) != 0 
        if direction == 'down':
            return (cellId / self.size) != (self.size-1)

    def getCell(self, pos):
        for cell in self.cells:
            if Rect(cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ).collidepoint(pos):
                return cell
    
    def clearScreen(self):
        for cell in self.cells:
            cell.alive = False
            self.updateCells.append(cell)
        self.draw()
    
    def randomScreen(self):
        for cell in self.cells:
            r = random.random()
            if r < 0.25:
                cell.alive = True
            else:
                cell.alive = False
            self.updateCells.append(cell)
        self.draw()

    def handleEvents(self):
        for event in pygame.event.get():
            if self.setting:
                if event.type == MOUSEBUTTONDOWN:
                    cell = self.getCell(event.pos)
                    cell.alive = not cell.alive
                    self.updateCells.append(cell)

                if event.type == KEYDOWN:
                    if event.key == pygame.K_p:
                        self.setting = False
                        self.playing = True
                    elif event.key == pygame.K_c:
                        self.clearScreen()
                    elif event.key == pygame.K_r:
                        self.randomScreen()

            elif self.playing:
                if event.type == KEYDOWN:
                    if event.key == pygame.K_s:
                        self.playing = False
                        self.setting = True
                    elif event.key == pygame.K_x:
                        self.delay -= 5
                    elif event.key == pygame.K_z:
                        self.delay += 5
            
            if event.type == QUIT:
                self.running = False

    def draw(self):
        updateRects = []

        for cell in self.updateCells:
            updateRects.append((cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ))
            if cell.alive:
                self.screen.fill((0,0,0), (cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ))
            else:
                self.screen.fill((255,255,255), (cell.topLeft[0], cell.topLeft[1], CELLSZ, CELLSZ))
                
        pygame.display.update(updateRects)

    def update(self):
        born = []
        kill = []

        for cell in self.cells:
            alive = 0
            for neighbor in self.getNeighbors(cell.idNum):
                if neighbor.alive:
                    alive += 1
            
            if cell.alive:
                if alive < 2 or alive > 3:
                    self.updateCells.append(cell)
                    kill.append(cell)
            else:
                if alive == 3:
                    self.updateCells.append(cell)
                    born.append(cell)
        for cell in born:
            cell.alive = True
        for cell in kill:
            cell.alive = False
    def run(self):
        self.running = True

        while self.running:
            self.handleEvents()
            self.draw()
            self.updateCells = []
            if self.playing:
                self.update()            
                pygame.time.delay(self.delay)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        gridSize = 20
    else:
        gridSize = int(sys.argv[1]) 

    gol = GameOfLife(gridSize)
    gol.run()
