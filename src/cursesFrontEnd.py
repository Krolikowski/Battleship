#! /usr/bin/env python3
import battleship, os, traceback, curses, time, sys

shipInfo = [ ("Patrol Boat", 2) ]

uppercase_chars =  map(chr, range(ord('A'), ord('A') + 26))
lowercase_chars =  map(chr, range(ord('a'), ord('a') + 26))
number_chars =  map(chr, range(ord('0'), ord('0') + 10))
misc_chars =  [",", " ", chr(263) ]

valid_input_chars = []
valid_input_chars.extend(uppercase_chars)
valid_input_chars.extend(lowercase_chars)
valid_input_chars.extend(number_chars)
valid_input_chars.extend(misc_chars)

class FrontEndPlayer( battleship.Player ):
    
    def __init__(self, name, grid):
        battleship.Player.__init__(self, name)
        self.grid = grid
        self.board = []
        self.opponentsBoard = []
        self.initBoards()
        self.shipSunkCount = 0
        self.stdscr = curses.initscr()

    def initBoards(self):
        cols = range( self.grid[0] )
        rows = range( self.grid[1] )
        
        self.board = [["~" for c in cols] for r in rows]
        self.opponentsBoard = [["~" for c in cols] for r in rows]

#------------------------Curses Functions------------------------------------------
def printGenericWindow(stdscr, playerName):
    '''Print all the information that will always need to be on the
    screen'''
    stdscr.border()
    y, x = stdscr.getmaxyx()
    stdscr.addstr( 2, int( ( x / 2)  - (len(playerName)/2)), playerName)
    stdscr.addstr( 3, int((x)/4) - 6, "HitMiss Board")
    stdscr.addstr( 3, int(( (3*x) / 4 ) - 7), "YourGamePieces")
    stdscr.refresh()

def printHorizontalLine(stdscr, y, x, string):
    stdscr.addstr(y, x, string)

def printVerticalLine(stdscr, y, x, string):

    for newY in range(y, len(string) + y):
        stdscr.addch(newY, x, string[newY - y])

def setColorPairs():
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)


def labelConstruct(maxLabel, space):
    chars = map(str, range(1, maxLabel + 1))
    return makeStringFromListOfChar(chars, space)

# GONZALO: I don't think this even needs to be a function. It's easily replaced
# with one line of code ( i.e.   "(' ' * space).join(chars)" ). You only use
# use these two functions in the printBoard function so they can be easily
# replaced with that one line and a comment explaining what's happening
def makeStringFromListOfChar(aList, spaceing):
    '''Long function name, amazing results'''
    separator = ' ' * spaceing
    return separator.join(aList)

# GONZALO: This function could use simpler variable names. Right now they are
# really long!
def printBoard(stdscr, boardObj, leftCorner):
    '''Note: leftCornerCoord => (y, x)'''
    xSpace = 3
    ySpace = 1
    gridLen = len(boardObj[0])
    printHorizontalLine(stdscr, leftCorner[0], leftCorner[1] + 1,\
                        labelConstruct(gridLen, xSpace))

    printVerticalLine(stdscr, leftCorner[0] + 1, leftCorner[1]-1,\
                        labelConstruct(gridLen, ySpace))
    yLine = leftCorner[0] - 1
    for line in range(len(boardObj)):
        printHorizontalLine(stdscr, (2 * (yLine +  line)) - 1, \
                            leftCorner[1] + 1, \
                            makeStringFromListOfChar(boardObj[line], xSpace))


def printPrompt(stdscr, prompt, y = 0):
    maxY, maxX = stdscr.getmaxyx()
    if y == 0:
        y = int((9 * maxY) / 10) #This calcs. the a line line 9/10ths from the bottom.
    printHorizontalLine(stdscr, y , 5 ,\
                        "  " * (maxX - (len(prompt) + 5))) #to clear everything
    printHorizontalLine(stdscr, y , 5, prompt)

def printErrorPrompt(stdscr, prompt):
    maxY, maxX = stdscr.getmaxyx()
    y = int((9 * maxY) / 10) + 1 #To print a line one below the reg prompt
    printPrompt(stdscr, prompt, y)

# GONZALO: These parameter names are long and they're not exactly descriptive
def printWindow(stdscr, boardObj, gamePieceBoardObj, \
                boardLeftCornerCoord, gamePieceLeftCornerCoord, playerName):
    '''boardObj should be a multi-dimensional array
       leftCornerCoord should be a tuple that contains the leftCorner
       where the board object should be printed'''
    curses.doupdate()
    curses.echo()
    printGenericWindow(stdscr, playerName)
    printBoard(stdscr, boardObj, boardLeftCornerCoord)
    printBoard(stdscr, gamePieceBoardObj, gamePieceLeftCornerCoord)
    curses.noecho()

def getBoardClickedCoord(stdscr, boardLeftCorner, boardObj):
    """Note: mouseClick will be a tuple containing (id, xCoord, yCoord, z,
    state) state will only matter with clicks
    This function returns (y, x)""" 
    i = stdscr.getch()

    if i == curses.KEY_MOUSE:
        mouseClick = curses.getmouse()
        return mouseClick[2], mouseClick[1]
    else:
        return None, None

def clearScreen(stdscr):
    stdscr.clear()

def getText(stdscr, prompt):

    printPrompt(stdscr, prompt)
    
    string = ''
    charInput =  stdscr.getch() 
    while( charInput != 10 ): #10 is the enter key

        if( not chr(charInput) in valid_input_chars ):
            charInput = stdscr.getch() 
            continue

        if( charInput == 263 ): #backspace chard
            string = string[:-1]
        else:
            string += chr( charInput )
        printPrompt(stdscr, prompt + " " + string)
        charInput = stdscr.getch() 

    return string

#------------------------Game Functions-----------------------------------------

def introMessage():
    '''Prints the intro message for the game.'''
    pass#todo make a intro message

def addShipToBoard(ship, board):
    '''Function to ste the board with the ship's coordinates
    Input: A list of ship objects and the board object.
    Output: None'''

    # GONZALO: OH just thought of doing this!
    for x,y in ship.coordinates:
        board[x][y] = ship.id

def coordConstructor(startCord, endCord):
    '''Fills in the missing coordinates between startCord and endCord
       Input: 
         startCord - the first coordinate of the ship
         endCord - the last coordinate of the ship
       Output: 
         A list containing all coordinates of that ship'''

    if startCord > endCord:
        # if the coordList's first entry is greater then the second
        startCord,endCord = endCord, startCord

    hOrientation = startCord[0] == endCord[0]
    vOrientation = startCord[1] == endCord[1]
    
    if not hOrientation and not vOrientation:
        raise ValueError("Ships coordinates were not orientated correctly")

    length = 0
    if hOrientation:
        length = (endCord[1] - startCord[1]) + 1
    else:
        length = (endCord[0] - startCord[0]) + 1

    # The coordinate list to return
    shipCoords = []
    for i in range(length):
        if hOrientation:
            coord = (startCord[0], startCord[1] + i)
        elif vOrientation: 
            coord = (startCord[0] + i, startCord[1])
        shipCoords.append( coord )
        
    return shipCoords


def getShipEnds(stdscr, prompt, oppBoard, board, playerName):
    prompt += " In 'row,column row,column' form: "
    while True:
        try:
            printPrompt(stdscr, prompt)
            stringCoord = getText(stdscr, prompt)
            start, end = [eval(t) for t in stringCoord.split()]
            if len(start) == 2 and len(end) == 2:
                break #To avoid incorrect input of 'x,y u' getting out of loop
            else: raise Exception
        except Exception:
            printErrorPrompt(stdscr, "Incorrect formatting. Try again. (press Enter)")
            stdscr.getch()
            clearScreen(stdscr)
            printWindow(stdscr, oppBoard, board, (4,2), \
                        (4, int( ( stdscr.getmaxyx()[1]) / 2)), playerName)

    start = (start[0] - 1, start[1] - 1)
    end = (end[0] - 1, end[1] - 1)
    return start, end

def setUpPlayerShips(game, player):
    '''To set up ships for the player specified
    Input: Game object
    Output: Lists of ship objects'''

    shipIDs = map(chr, range(ord('A'), ord('A') + len(shipInfo)))
    
    for name, length in shipInfo:

        errorMesg = None
        shipId = next(shipIDs)

        while True:
            clearScreen(player.stdscr)
            printWindow(player.stdscr, player.opponentsBoard, player.board, (4,2), \
                        (4, int( ( player.stdscr.getmaxyx()[1]) / 2)), player.name)

            if errorMesg:
                printErrorPrompt(player.stdscr,  errorMesg )
                errorMesg = None

            shipPrompt = "Where do you want your {0}, which should be {1} long?"
            printPrompt(player.stdscr, shipPrompt.format(name, length))
            startPos, endPos = getShipEnds(player.stdscr, shipPrompt.format(name, length), \
                                           player.opponentsBoard, player.board, player.name)

            if any( not game.point_inside_grid(p) for p in [startPos, endPos] ):
                errorMesg = "A point was not inside the grid!"
                continue
            
            try:
                shipCoordinates = coordConstructor(startPos, endPos)
            except ValueError:
                errorMesg = "Ship can only be oriented horizontally or vertically"
                continue

            if len(shipCoordinates) != length:
                errorMesg = "That is an incorrect length!"
                continue

            ship = battleship.Ship(shipId, shipCoordinates)

            try:
                game.add_ship(player, ship)
                addShipToBoard(ship, player.board)
            except battleship.ShipCollisionException:
                errorMesg = "Your ships would have collided"
                continue

            break # Success! 

#----------------------Main-----------------------------------------------------

import logging
logging.basicConfig(filename='curses.log', level=logging.DEBUG)

def main(stdscr):
    """Text-based UI for two players at the same console."""
    #--------------Game Setup-------------------------------------

    introMessage()
    maxY, maxX = stdscr.getmaxyx()
    resize_message_printed = False
    while maxX < 120 and maxY < 30:
        if not resize_message_printed:
            printPrompt(stdscr, "You need to extend your terminal to 120 x 40")
            resize_message_printed = True
        stdscr.getch()
        maxY, maxX = stdscr.getmaxyx()
    clearScreen(stdscr)
    if( resize_message_printed ):
        time.sleep(2)
    printPrompt(stdscr, "Welcome to Battleship! press Enter to start playing a game.")
    stdscr.getch()
    player1Name = getText(stdscr,  "What is player 1's name?")
    player2Name = getText(stdscr,  "What is player 2's name?")

    gridSize = eval(getText(stdscr, "What did you want the square grid size to be?(IE 10x10=>10) "))
    grid = (gridSize, gridSize)

    player1 = FrontEndPlayer(player1Name, grid)
    player2 = FrontEndPlayer(player2Name, grid)
    
    game = battleship.Game( grid )
    game.init_game( player1, player2 )

    setUpPlayerShips(game, player1)
    setUpPlayerShips(game, player2)

    
    #--------------Game Logic----------------------------------------
    if not game.game_ready():
        raise Exception("The game is unexpectedly not ready")
    winner = None
    while not winner:
        for p in [player1, player2]:
            printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)
            while( True ):
                try: #get incorrect input working
                    fireCoordinateString = getText(p.stdscr, "Where do you want to fire? x,y form ")
                    logging.debug('fireCoordinateString: %s' % (fireCoordinateString, ))
                    fireCoordinate = eval(fireCoordinateString)
                    logging.debug('fireCoordinate: %s' % (fireCoordinate, ))
                    if( len(fireCoordinate) != 2 ):
                        logging.debug('throwing error...')
                        raise SyntaxError
                    logging.debug('beep')
                    fireCoordinate = (fireCoordinate[0] - 1, fireCoordinate[1] - 1)
                    game.fire(p, fireCoordinate)
                    break
        
                except battleship.OutOfTurnException:
                    printPrompt(p.stdscr, "It's not your turn to fire! Press Enter")
                    p.stdscr.getch()
                    clearScreen(p.stdscr)
                    printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)
                except battleship.OutsideGridException:
                    printPrompt(p.stdscr, "That firing coordinate is outside the grid! Press Enter")
                    p.stdscr.getch()
                    printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)
                except battleship.RepeatFireException:
                    printPrompt(p.stdscr, "You have already fired there! Press Enter")
                    p.stdscr.getch()
                    printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)
                except IndexError:
                    printPrompt(p.stdscr, "Incorrect input: x,y formatting expected! Press Enter")
                    p.stdscr.getch()
                    printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)
                except SyntaxError:
                    logging.debug('Caught SyntaxError')
                    printPrompt(p.stdscr, "Incorrect formatting! int, int formatting expected")
                    logging.debug('a')
                    p.stdscr.getch()
                    printWindow(p.stdscr, p.opponentsBoard, p.board, (4,2), \
                        (4, int( ( maxX) / 2)), p.name)

            clearScreen(p.stdscr)
            printPrompt(stdscr, "Please switch with your opponent! Enter to cont.")
            p.stdscr.getch()
            
        for p in [player1, player2]:
            incomingHit, ship, shipSunk = game.incoming(p)
            if ship:
                p.board[ incomingHit[0] ][ incomingHit[1] ] = "H"

        for p in [player1, player2]:
            outgoingHit, ship, shipSunk = game.outgoing(p)

            if ship:
                p.opponentsBoard[ outgoingHit[0] ][ outgoingHit[1] ] = "X"
            else:
                p.opponentsBoard[ outgoingHit[0] ][ outgoingHit[1] ] = "M"

            other_p = game.other_player(p)

            if shipSunk:
                printPrompt( p.stdscr, "{0}, you have sunk {1} (Press enter)".format(p.name, ship.id) )
                stdscr.getch()
                other_p.shipSunkCount += 1

            if other_p.shipSunkCount == len(shipInfo):
                winner = p
                
        clearScreen(p.stdscr)

    printPrompt(stdscr, "Congratulations " + winner.name + ". You won!")
    stdscr.refresh()
    stdscr.getch()
    

def resetTerm(stdscr):
    # Set everything back to normal
      stdscr.keypad(0)
      curses.echo()
      curses.nocbreak()
      curses.endwin()                 # Terminate curses
    
if __name__=='__main__':
  try:
      # Initialize curses
      stdscr=curses.initscr()
      curses.start_color()#Color display -Will not raise error if unavaiable
      curses.mousemask(-1)#to allow clicking input
      # Turn off echoing of keys, and enter cbreak mode,
      # where no buffering is performed on keyboard input
      curses.noecho()
      curses.cbreak()

      # In keypad mode, escape sequences for special keys
      # (like the cursor keys) will be interpreted and
      # a special value like curses.KEY_LEFT will be returned
      stdscr.keypad(1)
      main(stdscr)# Enter the main loop
  except:
      traceback.print_exc()           # Print the exception
  finally:
      resetTerm(stdscr)
