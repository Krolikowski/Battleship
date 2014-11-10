#!/usr/bin/env python3

from battleship import *
from xmlrpc.server import *
from xmlrpc.client import *
import re
from random import randrange

def except_func(number):
    if number == 1:
        raise OutsideGridException("Server Exception")
    else:
        raise ValueError("Another Server Exception")

class ProposedGame:

    def __init__(self, p1, p2):
        self.players = [p1, p2]

    def accept(self, player):
        if player in self.players:
            player.accepted_game = True
            player.voted = True
        
    def reject(self, player):
        if player in self.players:
            player.accepted_game = False
            player.voted = True

    def ready(self):
        return all(p.voted for p in self.players)

    def accepted(self):
        return all(p.accepted_game for p in self.players)

    def rejected(self):
        return any(not p.accepted_game for p in self.players)

class GameManager(Game):
    
    def __init__(self):
        # Player ID -> Player object
        self.online_players = dict()

        # Players looking for a game
        # Player ID -> Player object
        self.free_players = dict()

        # Games that both players have yet to accept/reject
        # Player ID -> Proposed game
        self.proposed_games = dict()

        # Games that one or more players rejected
        # Player ID -> Proposed game
        self.rejected_games = dict()

        # Player ID -> Game object
        self.online_games = dict()

    # All method calls to this object are routed through here.
    # Converts dict objects into battleship objects
    def _dispatch(self, method, params):
        print("dispatch!", method)
        param_list = list(params)

        for i in range(len(param_list)):

            if type(params[i]) is not dict:
                continue

            # Hack way to determine if parameter is a Player
            if 'online_id' in params[i]:

                player_id = params[i]['online_id']
                player = self.online_players.get(player_id)
                
                if not player:
                    player = OnlinePlayer(params[i]['name'])
                    player.online_id = player_id
                    self.online_players[player_id] = player 

                param_list[i] = player

            # Hack way to determine if parameter is a Ship
            if 'coordinates' in params[i]:
                
                ship = Ship(params[i]['id'])
                ship.coordinates = params[i]['coordinates']

                param_list[i] = ship

        params = tuple(param_list)
        f = getattr(self, method)
        return f(*params)

    def register_player(self, player):
        self.free_players[player.online_id] = player

        if len(self.free_players) <= 1:
            return # No opponents available

        # Remove player
        del self.free_players[player.online_id]
        opponent_id, opponent = self.free_players.popitem()

        proposed_game = ProposedGame(player, opponent)
        
        self.proposed_games[player.online_id] = proposed_game
        self.proposed_games[opponent_id] = proposed_game

        return None

    def opponent_found(self, player):
        return player.online_id in self.proposed_games

    def accept_opponent(self, player):
        proposed_game = self.proposed_games[player.online_id]
        proposed_game.accept(player)
        
        if not proposed_game.ready():
            return

        if proposed_game.accepted():
            game = Game( (10,10) )
            game.init_game(*proposed_game.players)

        for p in proposed_game.players:
            del self.proposed_games[p.online_id]
            if proposed_game.accepted():
                self.online_games[p.online_id] = game
            else:
                self.rejected_games[p.online_id] = proposed_game
            
    def reject_opponent(self, player):
        proposed_game = self.proposed_games[player.online_id]
        proposed_game.reject(player)

        if not proposed_game.ready():
            return

        for p in proposed_game.players:
            del self.proposed_games[p.online_id]
            self.rejected_games[p.online_id] = proposed_game

    def deregister_player(self, player):
        pass

    # Returns a tuple (ready, accepted) where
    # ready is True if both players voted
    # accepted is True if both players accepted the game or 
    #          None if both players have not voted
    def opponent_responded(self, player):
        if player.online_id in self.online_games:
            return True, True
        elif player.online_id in self.rejected_games:
            return True, False
        else:
            return False, None

    def add_ship(self, player, ship):
        game = self.online_games[player.online_id]
        return game.add_ship(player,ship)

    def game_ready(self, player):
        game = self.online_games[player.online_id]
        if len(game.player1.ships) == 2 and len(game.player2.ships):
            return True
        else:
            return False

    def fire(self, player, coordinates):
        game = self.online_games[player.online_id]
        return game.fire(player, coordinates)

    def incoming_ready(self, player):
        game = self.online_games[player.online_id]
        return game.incoming_ready(player)

    def incoming(self, player):
        game = self.online_games[player.online_id]
        return game.incoming(player)

    def outgoing_ready(self, player):
        game = self.online_games[player.online_id]
        return game.outgoing_ready(player)

    def outgoing(self, player):
        game = self.online_games[player.online_id]
        return game.outgoing(player)

class OnlinePlayer(Player):
    
    def __init__(self, name):
        super(OnlinePlayer, self).__init__(name)
        self.online_id = randrange(999999)
        # Whether the player accepted the proposed game
        self.accepted_game = False
        # Whether the player accepted or rejected the proposed game
        self.voted = False


# RPC Client boilerplate moved to the server...
allowed_errors = [OutsideGridException, OutOfTurnException,
                  ShipCollisionException,GameInitializedException,
                  RepeatFireException ]

class ExceptionUnmarshaller (Unmarshaller):
    '''The default Unmarshaller of xmlrpc.client does not allow exceptions from
    the server to be raised in the client. Instead they are "wrapped" in a Fault
    error. 

    This Unmarshaller will take a list of exceptions. The unmarshaller will "unwrap" all
    the exceptions in the list before they are raised

    For example, take the list of exceptions
    >>> allowed_exceptions = [ValueError, Exception]
    
    Then, instead of getting this exception
    >>> <Fault 1: "<class 'ValueError'>:Server Exception">
    
    You get this exception
    >>> Value Error: Server Exception
    '''

    def __init__(self, allowed_exceptions, use_datetime=False):
        # Every fault contains a faultString. The faultString contains the exception
        # to be wrapped in the following format:
        #   "<class '$module.$exception'>:$message"
        # The $module is optional
        p = '<class \'((?P<module>.*)\.)?(?P<exception>.*)\'>:(?P<message>.*$)'
        # This is a regex pattern. It will match the exception, it's message and 
        # the module of the exception if there is one
        super(ExceptionUnmarshaller, self).__init__(self, use_datetime)
        self.error_pat = re.compile(p)
        self.allowed_exceptions = dict()
        for e in allowed_exceptions:
            self.allowed_exceptions[e.__name__] = e

    def close(self):
        if self._type == "fault":
            d = self._stack[0]
            match = self.error_pat.match(d['faultString'])
            if match:
                exc_name = match.group('exception')
                message = match.group('message')
                
                if exc_name in self.allowed_exceptions:
                    raise self.allowed_exceptions[exc_name](message)

            # Fall through and just raise the fault
            raise Fault(**d)
        else:
            return super(ExceptionUnmarshaller, self).close()


class ExceptionTransport (Transport):
    # This will force the client ServerProxy to use the new Unmarshaller
    
    def getparser (self):
        # We want to use our own custom unmarshaller
        unmarshaller = ExceptionUnmarshaller(allowed_errors)
        parser = ExpatParser(unmarshaller)
        return parser, unmarshaller


def getProxy():
    return ServerProxy('http://137.142.101.27:8000', allow_none=True, 
                transport=ExceptionTransport())


if __name__ == '__main__':
    # IDEA: Have every function the client calls to have a client id. Create a
    # decorator client side, so that the UI never has to deal with it
    server = SimpleXMLRPCServer(("137.142.101.27", 8000), allow_none=True)
    server.register_function(except_func)
    server.register_instance(GameManager())
    # Run the server's main loop
    server.serve_forever()



        
