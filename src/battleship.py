#!/usr/bin/env python3

import random # to generate a ID


class OutsideGridException(Exception):
    pass

class OutOfTurnException(Exception):
    pass

class ShipCollisionException(Exception):
    pass

class GameInitializedException(Exception):
    pass

class RepeatFireException(Exception):
    pass

class Ship:

    def __init__(self, id, coordinates = None):
        self.id = id
        if coordinates:
            self.coordinates = coordinates
        else:
            self.coordinates = []

    def is_sunk(self, coordinates):
        return all(c in coordinates for c in self.coordinates)


class Player:

    def __init__(self, name):
        self.name = name 
        self.ships = []
        self.firing_coordinates = [] # list of coordinates in tuple form
        self.ready = False # Player ready to transition to next state

    # Returns true if the ship collides with the player's ships
    def ship_collides(self, ship):
        for s in self.ships:
            for c in s.coordinates:
                if c in ship.coordinates:
                    return True
        return False

class Game:

    def __init__(self, grid):
        self.player1 = None
        self.player2 = None
        self.grid = grid
        # Grid in the form of a tuple
        # (w, h)
        # where w = width and h = height
        # so it's (c, r)
        # where c = columns, and r = rows
        self.state = -1 
        # State are the following
        # -1 = Setting up ships
        # 0 = Ready to fire
        # 1 = Ready for incoming
        # 2 = Ready for outgoing


    # TODO: raise an Error if ship is on top of another
    #       return the length of the ship
    def add_ship(self, player, ship):
        
        if any( not self.point_inside_grid(c) for c in ship.coordinates ):
            raise OutsideGridException("A point on the ship is outside the coordinate")

        if player.ship_collides(ship):
            raise ShipCollisionException("The ship collides with another ship on the grid")
        
        player.ships.append(ship)
    
    # Initialize the game 
    # Input :
    #           grid 
    #           player1
    #           player2
    # Output :  
    #           Nothing
    def init_game(self, player1, player2):
        #method for game class
        #initializes a game
        if self.player1 and self.player2: #to check if the game is already init
            raise GameInitializedException("Game Already initialized")
        else:
            self.player1 = player1
            self.player2 = player2
            self.state = 0

    # Checks to see if Game is ready by Tim Broadwell
    # The frontend queries this to see if the game is ready
    # Output : returns true if the following are instantiated
    #     grid
    #     player1
    #     player2
    #     gameid
    #          else return false
    def game_ready(self):
        if self.player1 and self.player2 and self.state == 0:
            return True
        return False

    # The function checks to see if the player is allowed to fire, adds the 
    # fire coordinates to the players fire_coordinates list
    # Input : 
    #        gameid
    #        player that is firing
    #        coordinates to fire to
    def fire(self, player, coordinates):

        if self.state != 0:
            raise OutOfTurnException("You can't fire yet")

        if self.state == 0 and player.ready:
            raise OutOfTurnException("You can't fire twice per round")

        if not self.point_inside_grid(coordinates):
            raise OutsideGridException("That firing coordinate is outside the grid")

        if coordinates in player.firing_coordinates:
           raise RepeatFireException("Player has already fired there") 

        player.firing_coordinates.append(coordinates)

        player.ready = True
        self.increment_state();

    # Returns true if the other player fired
    # Input: 
    #         gameid
    #         player
    # Output:
    #         true or false
    def incoming_ready(self, player):
        return self.state == 1

    # Relays information about the incoming fire
    # Input : 
    #          player expecting the incoming fire
    # Output : 
    #          Incoming hits coordinates
    #          if they were hits
    #          if they sunk the ship
    def incoming(self, player):

        if not self.incoming_ready(player):
            raise OutOfTurnException("Both players did not fire")

        other_player = self.other_player(player)
        ship_hit, ship_sunk = self.check_player_hit(other_player)
        firing_coordinates = other_player.firing_coordinates[-1]

        player.ready = True
        self.increment_state()
        return (firing_coordinates, ship_hit, ship_sunk)

    def outgoing_ready(self, player):
        return self.state == 2

    def outgoing(self, player):

        if not self.outgoing_ready(player):
            raise OutOfTurnException("Both players did not call incoming")
        
        ship_hit, ship_sunk = self.check_player_hit(player)
        firing_coordinates = player.firing_coordinates[-1]

        player.ready = True
        self.increment_state()
        return (firing_coordinates, ship_hit, ship_sunk)

    # Convenience method to return the other player
    def other_player(self, player):
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        else:
            return None

    # Convenience method to return the player object with a given name
    def get_player( self, player_string):
        if self.player1.name == player_string:
            return self.player1
        elif self.player2.name == player_string:
            return self.player2
        else:
            return None

    def check_player_hit(self, player_firing):

        firing_coordinates = player_firing.firing_coordinates[-1]

        ship_hit = None # The ship that was hit
        ship_sunk = False
        for s in self.other_player(player_firing).ships:
            if firing_coordinates in s.coordinates:
                ship_hit = s
                break
        
        if ship_hit:
            if ship_hit.is_sunk(player_firing.firing_coordinates):
                ship_sunk = True
                
        return (ship_hit, ship_sunk)
        
    def players_ready(self):
        return self.player1.ready and self.player2.ready

    def increment_state(self):
        if self.players_ready():
            self.state = (self.state + 1) % 3
            self.player1.ready = self.player2.ready = False

    def point_inside_grid(self, point):

        x_inside = point[0] >= 0 and point[0] < self.grid[0]
        y_inside = point[1] >= 0 and point[1] < self.grid[1]

        return x_inside and y_inside


