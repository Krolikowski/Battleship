#! /usr/bin/env python3
import battleship, os, server, time, random

shipInfo = [ ("Patrol Boat", 2), ("Destroyer", 3) ]

class FrontEndPlayer( battleship.Player ):
    
    def __init__(self, name, grid):
        super(FrontEndPlayer, self).__init__(name)
        self.grid = grid
        self.board = []
        self.opponentsBoard = []
        self.initBoards()
        self.shipSunkCount = 0

    def initBoards(self):
        cols = range( self.grid[0] )
        rows = range( self.grid[1] )
        
        self.board = [["~" for c in cols] for r in rows]
        self.opponentsBoard = [["~" for c in cols] for r in rows]

class TextGame:
    
    def clearScreen(self):
        os.system('cls' if os.name=='nt' else 'clear')

    def addShipToBoard(self, ship, board):
        '''Function to ste the board with the ship's coordinates
        Input: A list of ship objects and the board object.
        Output: None'''

        for coordinate in ship.coordinates:
            board[coordinate[0]][coordinate[1]] = ship.id

    def printBoard(self, boardObj):
        '''Function to print the board object to the terminal
        Input: boardObj
        Output: Printing the board to the terminal'''
        print("  ", end="")
        for i in range(len(boardObj)):
            print(str(i+1).zfill(2), end=" ")
        print()
        for i in range(len(boardObj)):
            print(str(i+1).zfill(2), end=" ")
            row = boardObj[i]
            for elem in row:
                print(elem, end="  ")
            print()
        print()

    def coordConstructor(self, startCord, endCord):
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


    def getShipEnds(self):

        while True:
            try:
                prompt = "In 'row,column row,column' form: "
                userInput = input( prompt )
                start, end = [eval(t) for t in userInput.split()]
                break
            except Exception:
                print("The input was incorrect, try again..")

        start = (start[0] - 1, start[1] - 1)
        end = (end[0] - 1, end[1] - 1)
        return start, end

    def setUpPlayerShips(self, game, player):
        '''To set up ships for the player specified
        Input: Game object
        Output: Lists of ship objects'''

        shipIDs = map(chr, range(ord('A'), ord('A') + len(shipInfo)))

        for name, length in shipInfo:

            errorMesg = None
            shipId = next(shipIDs)

            while True:
                self.clearScreen()
                self.printBoard(player.board)

                if errorMesg:
                    print("\n" + errorMesg + "\n")
                    errorMesg = None

                shipPrompt = "Where do you want your {0}, which should be {1} long?"
                print( shipPrompt.format(name, length) )
                startPos, endPos = self.getShipEnds()

                if any( not game.point_inside_grid(p) for p in [startPos, endPos] ):
                    errorMesg = "A point was not inside the grid!"
                    continue

                try:
                    shipCoordinates = self.coordConstructor(startPos, endPos)
                except ValueError:
                    errorMesg = "Ship can only be oriented horizontally or vertically"
                    continue

                if len(shipCoordinates) != length:
                    errorMesg = "That is an incorrect length!"
                    continue

                ship = battleship.Ship(shipId, shipCoordinates)

                try:
                    game.add_ship(player, ship)
                    self.addShipToBoard(ship, player.board)
                except battleship.ShipCollisionException:
                    errorMesg = "Your ships would have collided"
                    continue

                break # Success! 


class PVPTextGame(TextGame):

    def main(self):
        """Text-based UI for two players at the same console."""
        #--------------Game Setup-------------------------------------

        player1Name = input("What is player 1's name? ")
        player2Name = input("What is player 2's name? ")

        gridSize = eval(input("What did you want the square grid size to be?(IE 10x10=>10) "))
        grid = (gridSize, gridSize)

        player1 = FrontEndPlayer(player1Name, grid)
        player2 = FrontEndPlayer(player2Name, grid)

        game = battleship.Game( grid )
        game.init_game( player1, player2 )

        self.setUpPlayerShips(game, player1)
        self.setUpPlayerShips(game, player2)

        self.clearScreen()
        #--------------Game Logic----------------------------------------
        if not game.game_ready():
            raise Exception("The game is unexpectedly not ready")

        winner = None
        while not winner:

            for p in [player1, player2]:
                errorMesg = ""
                while True:
                                    
                    self.clearScreen()
                    print(p.name, "'s boards\n")
                    print("Miss/Hit Board")
                    self.printBoard(p.opponentsBoard)
                    print("Your board")
                    self.printBoard(p.board)

                    if errorMesg:
                        print(errorMesg + "\n")

                    try:
                        fireCoordinate = eval(input("Where do you want to fire? (x,y) format: "))
                        fireCoordinate = (fireCoordinate[0] - 1, fireCoordinate[1] - 1)
                        game.fire(p, fireCoordinate)
                    except battleship.RepeatFireException:
                        errorMesg = "You already fired in that spot!"
                        continue
                    except battleship.OutsideGridException:
                        errorMesg = "Those coordinates are outside of the grid!"
                        continue
                    except Exception:
                        errorMesg = "The input was incorrect, try again..."
                        continue

                    break

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
                    other_p.shipSunkCount += 1

                if other_p.shipSunkCount == len(shipInfo):
                    winner = p

            self.clearScreen()

        print("Congratulations " + winner.name + ". You won!")


class OnlineFrontEndPlayer( FrontEndPlayer ):

    def __init__(self, name, gridSize):
        super(OnlineFrontEndPlayer, self).__init__(name, gridSize)
        self.online_id = random.randrange(999999)
        # Whether the player accepted the proposed game
        self.accepted_game = False
        # Whether the player accepted or rejected the proposed game
        self.voted = False

class OnlineTextGame(TextGame):
    
    class DummyGame:

        def __init__(self, serverProxy, gridSize):
            self.proxy = serverProxy
            self.game = battleship.Game(gridSize)
        
        def point_inside_grid(self, point):
            return self.game.point_inside_grid(point)

        def add_ship(self, player, ship):
            return self.proxy.add_ship(player, ship)

    def main(self):
        s = server.getProxy()
        p = OnlineFrontEndPlayer(input("What is your name? "), (10,10))

        s.register_player(p)

        print("Waiting for opponent!...")
        while not s.opponent_found(p):
            time.sleep(.5)
        
        s.accept_opponent(p);

        print("Waiting for opponent to accept!");
        while not s.opponent_responded(p):
            time.sleep(.5)

        dummy_game = self.DummyGame(s, (10,10))
        self.setUpPlayerShips(dummy_game, p)

        while not s.game_ready(p):
            time.sleep(.5)
            
        print("Game Ready!")
        
        mySunkShips = 0
        othersSunkShips = 0

        winner = False
        while True:

            errorMesg = None
            while True:
                try:

                    print("Miss/Hit Board")
                    self.printBoard(p.opponentsBoard)
                    print("Your board")
                    self.printBoard(p.board)

                    if errorMesg:
                        print(errorMesg + "\n")

                    fireCoordinate = eval(input("Where do you want to fire? (x,y) format: "))
                    fireCoordinate = (fireCoordinate[0] - 1, fireCoordinate[1] - 1)
                    s.fire(p, fireCoordinate)
                except battleship.RepeatFireException:
                    errorMesg = "You already fired in that spot!"
                    continue
                except battleship.OutsideGridException:
                    errorMesg = "Those coordinates are outside of the grid!"
                    continue
                except Exception:
                    errorMesg = "The input was incorrect, try again..."
                    continue

                break
            

            print("Waiting for opponent to fire...")
            while not s.incoming_ready(p):
                time.sleep(.5)

            incomingHit, ship, shipSunk = s.incoming(p)

            if ship:
                p.board[ incomingHit[0] ][ incomingHit[1] ] = "H"
                
            if shipSunk:
                mySunkShips += 1
                
            if mySunkShips == len(shipInfo):
                winner = False
                break

            while not s.outgoing_ready(p):
                time.sleep(.5)

            outgoingHit, ship, shipSunk = s.outgoing(p)

            if ship:
                p.opponentsBoard[ outgoingHit[0] ][ outgoingHit[1] ] = "X"
            else:
                p.opponentsBoard[ outgoingHit[0] ][ outgoingHit[1] ] = "M"

            if shipSunk:
                othersSunkShips += 1

            if othersSunkShips == len(shipInfo):
                winner = True
                break

        if winner:
            print("Congratulations you won!")
        else:
            print("Regretably you lost")

if __name__ == "__main__":

    game = OnlineTextGame();
    game.main();

