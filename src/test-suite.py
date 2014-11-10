#!/usr/bin/env python3

from battleship import *
from text_frontend import *
import unittest
from server import *

class BattleShipSimpleTestCase(unittest.TestCase):

    def setUp(self):
        self.game = Game( (5,5) )
        self.player1 = Player("J")
        self.player2 = Player("K")

        self.player1.ships = [ Ship("A", [(0,0), (0,1)]) ]
        self.player2.ships = [ Ship("Z", [(1,0), (1,1)]) ]


    def testInit(self):
        self.game.init_game(self.player1, self.player2)
        self.assertRaises(GameInitializedException, self.game.init_game, 
                          self.player1, self.player2)


    def testGameReady(self):
        self.assertEqual(self.game.game_ready(), False)
        self.game.init_game(self.player1, self.player2)
        self.assertEqual(self.game.game_ready(), True)

    def testFire(self):
        self.game.init_game(self.player1, self.player2)
        
        self.game.fire(self.player1, (0,0))
        self.assertRaises(OutOfTurnException, self.game.fire, self.player1, (0,1))

    def testIncomingReady(self):
        self.game.init_game(self.player1, self.player2)

        self.assertEqual(self.game.incoming_ready(self.player1), False)
        self.assertEqual(self.game.incoming_ready(self.player2), False)

        self.game.fire(self.player1, (0,0))

        self.assertEqual(self.game.incoming_ready(self.player1), False)
        self.assertEqual(self.game.incoming_ready(self.player2), False)

        self.game.fire(self.player2, (1,0))

        self.assertEqual(self.game.incoming_ready(self.player1), True)
        self.assertEqual(self.game.incoming_ready(self.player2), True)

    def testIncoming(self):
        self.game.init_game(self.player1, self.player2)

        self.assertRaises(OutOfTurnException, self.game.incoming, self.player1)
        self.assertRaises(OutOfTurnException, self.game.incoming, self.player2)
        
        self.game.fire(self.player1, (0,0))

        self.assertRaises(OutOfTurnException, self.game.incoming, self.player1)
        self.assertRaises(OutOfTurnException, self.game.incoming, self.player2)

        self.game.fire(self.player2, (1,0))

    def testShipMiss(self):
        self.game.init_game(self.player1, self.player2)

        self.game.fire(self.player1, (0,0))
        self.game.fire(self.player2, (1,0))

        coord, ship, sunk = self.game.incoming(self.player1)

        self.assertEqual(coord, (1,0))
        self.assertEqual(ship, None)
        self.assertEqual(sunk, False)

        coord, ship, sunk = self.game.incoming(self.player2)

        self.assertEqual(coord, (0,0))
        self.assertEqual(ship, None)
        self.assertEqual(sunk, False)
        
    def testShipHit(self):
        self.game.init_game(self.player1, self.player2)

        self.game.fire(self.player1, (1,0))
        self.game.fire(self.player2, (0,0))

        coord, ship, sunk = self.game.incoming(self.player1)

        self.assertEqual(coord, (0,0))
        self.assertEqual(ship.id, "A")
        self.assertEqual(sunk, False)

        coord, ship, sunk = self.game.incoming(self.player2)

        self.assertEqual(coord, (1,0))
        self.assertEqual(ship.id, "Z")
        self.assertEqual(sunk, False)

        self.game.outgoing(self.player1)
        self.game.outgoing(self.player2)

        self.game.fire(self.player1, (1,1))
        self.game.fire(self.player2, (0,2))
    
        coord, ship, sunk = self.game.incoming(self.player1)

        self.assertEqual(coord, (0,2))
        self.assertEqual(ship, None)
        self.assertEqual(sunk, False)

        coord, ship, sunk = self.game.incoming(self.player2)

        self.assertEqual(coord, (1,1))
        self.assertEqual(ship.id, "Z")
        self.assertEqual(sunk, True)

    # Test written by Matt to test if the bug he was experiencing was
    # with the backend or the frontend
    def testShipSunk(self):
        p1 = Player("J")
        p2 = Player("K")

        self.game.init_game(p1, p2)
        p1.ships.append( Ship("a", [(0,0), (0,1)]) )
        p1.ships.append( Ship("b", [(2,0), (2,1)]) )
        
        p2.ships.append( Ship("c", [(1,0), (1,1)]) )

        self.game.fire(p1, (4,4))
        self.game.fire(p2, (0,0))

        self.game.incoming(p1)
        self.game.incoming(p2)

        self.game.outgoing(p1)
        self.game.outgoing(p2)

        self.game.fire(p1, (2,2))
        self.game.fire(p2, (0,1))

        coord,ship,sunk = self.game.incoming(p1)
        self.assertEqual(ship.id, "a")
        self.assertEqual(sunk, True)
        

    def testFireOutsideGrid(self):
        self.game.init_game(self.player1, self.player2)
        
        self.assertRaises(OutsideGridException, self.game.fire, self.player1, (5,4))
        self.assertRaises(OutsideGridException, self.game.fire, self.player1, (4,5))
        self.assertRaises(OutsideGridException, self.game.fire, self.player1, (-1,0))
        self.assertRaises(OutsideGridException, self.game.fire, self.player1, (0,-1))
        
        # This should not raise an exception
        self.game.fire(self.player1, (4,4))

    def testFireOnSameCoordinate(self):
        self.game.init_game(self.player1, self.player2)
        
        self.game.fire(self.player1, (0,0))
        self.game.fire(self.player2, (1,0))
        
        self.game.incoming(self.player1)
        self.game.incoming(self.player2)

        self.game.outgoing(self.player1)
        self.game.outgoing(self.player2)

        self.assertRaises(RepeatFireException, self.game.fire, self.player1, (0,0) )
        self.game.fire(self.player1, (0,1))
        
        self.assertRaises(RepeatFireException, self.game.fire, self.player2, (1,0) )
        self.game.fire(self.player2, (1,1))

        self.game.incoming(self.player1)
        self.game.incoming(self.player2)

        self.game.outgoing(self.player1)
        self.game.outgoing(self.player2)
        
        self.assertRaises(RepeatFireException, self.game.fire, self.player1, (0,0) )
        self.game.fire(self.player1, (0,2))
        
        self.assertRaises(RepeatFireException, self.game.fire, self.player2, (1,0) )
        self.game.fire(self.player2, (1,2))

    def testAddShip(self):
        player1 = Player("J")
        ship1 = Ship("A", [(0,0), (0,1)])

        self.game.add_ship( player1, ship1 )
        self.assertTrue( ship1 in player1.ships )

    def testAddShipCollision(self):
        player1 = Player("J")
        ship1 = Ship("A", [(0,0), (0,1)])
        ship2 = Ship("B", [(0,1), (0,2)])

        self.game.add_ship( player1, ship1 )
        self.assertRaises(ShipCollisionException, self.game.add_ship, player1, ship2)

    def testAddShipOutsideGrid(self):
        player1 = Player("J")
        ship1 = Ship("A", [ (4,4), (4,5) ])
        ship2 = Ship("B", [ (4,4), (5,4) ])
        ship3 = Ship("C", [ (0,0), (0,-1) ])
        ship4 = Ship("D", [ (0,0), (-1,0) ])

        self.assertRaises(OutsideGridException, self.game.add_ship, player1, ship1)
        self.assertRaises(OutsideGridException, self.game.add_ship, player1, ship2)
        self.assertRaises(OutsideGridException, self.game.add_ship, player1, ship3)
        self.assertRaises(OutsideGridException, self.game.add_ship, player1, ship4)

    def testPlayersShareShipList(self):
        # Look at issue #2 in bitbucket
        g = Game( (5,5) )
        p1 = Player("B")
        p2 = Player("A")
        s1 = Ship("S1", [ (0,0), (0,1) ] )
        g.add_ship(p1, s1)
        self.assertTrue( len(p1.ships) != len(p2.ships) )

class TextFrontEndTestCase(unittest.TestCase):

    def setUp(self):
        self.frontend = TextGame()

    def testCoordConstructor(self):
        
        # Lists of list that contain
        #     starting position
        #     ending position
        #     expected output
        testData = [ [(1,1), (1,2), [(1,1), (1,2)]],
                     [(1,2), (1,1), [(1,1), (1,2)]],
                     [(2,1), (2,3), [(2,1), (2,2), (2,3)]],
                     [(2,3), (2,1), [(2,1), (2,2), (2,3)]],
                     [(3,5), (3,9), [(3,5), (3,6), (3,7), (3,8), (3,9)]],
                     [(3,9), (3,5), [(3,5), (3,6), (3,7), (3,8), (3,9)]],
                     # Vertical Orientation
                     [(1,1), (2,1), [(1,1), (2,1)]],
                     [(2,1), (1,1), [(1,1), (2,1)]],
                     [(1,2), (3,2), [(1,2), (2,2), (3,2)]],
                     [(3,2), (1,2), [(1,2), (2,2), (3,2)]],
                     [(3,5), (7,5), [(3,5), (4,5), (5,5), (6,5), (7,5)]],
                     [(7,5), (3,5), [(3,5), (4,5), (5,5), (6,5), (7,5)]] ]

        for start,end,result in testData:
            self.assertEqual(self.frontend.coordConstructor(start,end), result)

    def testAddShipToBoard(self):
        board = [ ['~','~','~'], ['~','~','~'], ['~','~','~'] ]
        ship1 = Ship("A")
        ship1.coordinates = [(0,0), (0,1)]
        board_result_1 = [ ['A','A','~'], ['~','~','~'], ['~','~','~'] ]

        self.frontend.addShipToBoard(ship1, board)
        self.assertEqual(board, board_result_1)

        board = [ ['~','~','~'], ['~','~','~'], ['~','~','~'] ]
        ship2 = Ship("B")
        ship2.coordinates = [(0,0), (1,0)]
        board_result_2 = [ ['B','~','~'], ['B','~','~'], ['~','~','~'] ]

        self.frontend.addShipToBoard(ship2, board)
        self.assertEqual(board, board_result_2)

class GameManagerTestCase(unittest.TestCase):

    # Emulates the server calling the _dispatch method
    def setUp(self):
        self.manager = GameManager()
        self.p1 = OnlinePlayer("Player 1")
        self.p2 = OnlinePlayer("Player 2")
        self.p3 = OnlinePlayer("Player 3")

        for p in [self.p1, self.p2, self.p3]:
            self.manager.online_players[p.online_id] = p

    def testRegisterPlayer(self):
        self.manager.register_player(self.p1)
        self.assertTrue( self.p1.online_id in self.manager.free_players )
        
        # P1 should have been paired with P2
        self.manager.register_player(self.p2)
        self.assertTrue( self.p1.online_id not in self.manager.free_players )
        self.assertTrue( self.p2.online_id not in self.manager.free_players )
        self.assertTrue( self.p1.online_id in self.manager.proposed_games )
        self.assertTrue( self.p2.online_id in self.manager.proposed_games )

        # P3 should have no opponents
        self.manager.register_player(self.p1)
        self.assertTrue( self.p1.online_id in self.manager.free_players )

    def testOpponentFound(self):
        self.manager.register_player(self.p1)
        self.assertTrue(not self.manager.opponent_found(self.p1))

        self.manager.register_player(self.p2)
        self.assertTrue(self.manager.opponent_found(self.p1))
        self.assertTrue(self.manager.opponent_found(self.p2))

        self.manager.register_player(self.p3)
        self.assertTrue(not self.manager.opponent_found(self.p3))

    def testAcceptOpponent(self):
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.accept_opponent(self.p1)
        self.assertTrue(self.p1.voted)
        self.assertTrue(self.p1.accepted_game)

        self.manager.accept_opponent(self.p2)
        self.assertTrue(self.p2.voted)
        self.assertTrue(self.p2.accepted_game)

    def testRejectOpponent(self):
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.reject_opponent(self.p1)
        self.assertTrue(self.p1.voted)
        self.assertTrue(not self.p1.accepted_game)

        self.manager.reject_opponent(self.p2)
        self.assertTrue(self.p2.voted)
        self.assertTrue(not self.p2.accepted_game)

    def testOpponentResponded(self):
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.accept_opponent(self.p1)
        self.assertEqual(self.manager.opponent_responded(self.p1), (False, None))
        self.assertEqual(self.manager.opponent_responded(self.p2), (False, None))

        self.manager.accept_opponent(self.p2)
        self.assertEqual(self.manager.opponent_responded(self.p1), (True, True))
        self.assertEqual(self.manager.opponent_responded(self.p2), (True, True))

        self.assertTrue(self.p1.online_id in self.manager.online_games)
        self.assertTrue(self.p2.online_id in self.manager.online_games)
        
        # Reset the game manager
        self.setUp()

        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.accept_opponent(self.p1)
        self.assertEqual(self.manager.opponent_responded(self.p1), (False, None))
        self.assertEqual(self.manager.opponent_responded(self.p2), (False, None))

        self.manager.reject_opponent(self.p2)
        self.assertEqual(self.manager.opponent_responded(self.p1), (True, False))
        self.assertEqual(self.manager.opponent_responded(self.p2), (True, False))

        self.setUp()

        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.reject_opponent(self.p1)
        self.assertEqual(self.manager.opponent_responded(self.p1), (False, None))
        self.assertEqual(self.manager.opponent_responded(self.p2), (False, None))

        self.manager.accept_opponent(self.p2)
        self.assertEqual(self.manager.opponent_responded(self.p1), (True, False))
        self.assertEqual(self.manager.opponent_responded(self.p2), (True, False))
        

    def testAddShip(self):
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.accept_opponent(self.p1)
        self.manager.accept_opponent(self.p2)

        good_ship = Ship("A");
        good_ship.coordinates = [(0,0), (0,1) ]

        self.manager.add_ship(self.p1, good_ship)
        self.manager.add_ship(self.p2, good_ship)

        self.assertTrue(good_ship in self.p1.ships)
        self.assertTrue(good_ship in self.p2.ships)

        collision_ship = Ship("C")
        collision_ship.coordinates = [(0,1), (0,2)]

        self.assertRaises(ShipCollisionException, self.manager.add_ship, 
                          self.p1, collision_ship)
        
        self.assertRaises(ShipCollisionException, self.manager.add_ship, 
                          self.p2, collision_ship)

        outside_ship = Ship("O")
        outside_ship.coordinates = [(9,9), (9,10)]

        self.assertRaises(OutsideGridException, self.manager.add_ship, 
                          self.p1, outside_ship)
        
        self.assertRaises(OutsideGridException, self.manager.add_ship, 
                          self.p2, outside_ship)

        good_ship2 = Ship("B")
        good_ship2.coordinates = [(1,0), (1,1)]

        self.manager.add_ship(self.p1, good_ship2)
        self.manager.add_ship(self.p2, good_ship2)

        self.assertTrue(good_ship2 in self.p1.ships)
        self.assertTrue(good_ship2 in self.p2.ships)

    def testFire(self):
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)
        
        self.manager.accept_opponent(self.p1)
        self.manager.accept_opponent(self.p2)

        shipA = Ship("A", [(0,0), (0,1)])
        shipB = Ship("B", [(1,0), (1,1), (1,2)])

        self.manager.add_ship(self.p1, shipA)
        self.manager.add_ship(self.p1, shipB)
        
        self.manager.add_ship(self.p2, shipA)
        self.manager.add_ship(self.p2, shipB)

        self.assertRaises(OutsideGridException, self.manager.fire, 
                          self.p1, (9,10))
        self.assertRaises(OutsideGridException, self.manager.fire, 
                          self.p2, (9,10))

        self.manager.fire(self.p1, (0,0))
        self.manager.fire(self.p2, (0,0))
        
        self.assertTrue((0,0) in self.p1.firing_coordinates)
        self.assertTrue((0,0) in self.p2.firing_coordinates)

        self.manager.incoming(self.p1)
        self.manager.incoming(self.p2)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        self.manager.fire(self.p1, (1,0))
        self.manager.fire(self.p2, (1,0))

        self.assertTrue((1,0) in self.p1.firing_coordinates)
        self.assertTrue((1,0) in self.p2.firing_coordinates)

        # Incoming so we don't get an OutOfTurnException
        self.manager.incoming(self.p1)
        self.manager.incoming(self.p2)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        self.assertRaises(RepeatFireException, self.manager.fire, 
                          self.p1, (0,0))
        self.assertRaises(RepeatFireException, self.manager.fire, 
                          self.p2, (0,0))
        
    def testIncomingReady(self):
         
        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)

        self.manager.accept_opponent(self.p1)
        self.manager.accept_opponent(self.p2)

        good_ship = Ship("A");
        good_ship.coordinates = [(0,0), (0,1) ]

        self.manager.add_ship(self.p1, good_ship)
        self.manager.add_ship(self.p2, good_ship)

        self.assertEqual(self.manager.incoming_ready(self.p1), False)
        self.assertEqual(self.manager.incoming_ready(self.p2), False)

        self.manager.fire(self.p1, (5,5))

        self.assertEqual(self.manager.incoming_ready(self.p1), False)
        self.assertEqual(self.manager.incoming_ready(self.p2), False)

        self.manager.fire(self.p2, (5,4))

        self.assertEqual(self.manager.incoming_ready(self.p1), True)
        self.assertEqual(self.manager.incoming_ready(self.p2), True)

        self.manager.incoming(self.p1)
        self.manager.incoming(self.p2)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        # Test the opposite firing order

        self.assertEqual(self.manager.incoming_ready(self.p1), False)
        self.assertEqual(self.manager.incoming_ready(self.p2), False)

        self.manager.fire(self.p2, (5,5))

        self.assertEqual(self.manager.incoming_ready(self.p1), False)
        self.assertEqual(self.manager.incoming_ready(self.p2), False)

        self.manager.fire(self.p1, (5,4))

        self.assertEqual(self.manager.incoming_ready(self.p1), True)
        self.assertEqual(self.manager.incoming_ready(self.p2), True)

        
    def testIncoming(self):

        self.manager.register_player(self.p1)
        self.manager.register_player(self.p2)

        self.manager.accept_opponent(self.p1)
        self.manager.accept_opponent(self.p2)

        p1_ship1 = Ship("A");
        p1_ship1.coordinates = [(0,0), (0,1)]

        p1_ship2 = Ship("B");
        p1_ship2.coordinates = [(1,0), (1,1)]
        
        self.manager.add_ship(self.p1, p1_ship1)
        self.manager.add_ship(self.p1, p1_ship2)

        p2_ship1 = Ship("A");
        p2_ship1.coordinates = [(0,0), (0,1)]

        p2_ship2 = Ship("B");
        p2_ship2.coordinates = [(1,0), (1,1)]

        self.manager.add_ship(self.p2, p2_ship1)
        self.manager.add_ship(self.p2, p2_ship2)

        # Test correct coordinates
        p1_fire_coord = (5,5)
        p2_fire_coord = (6,6)

        self.manager.fire(self.p1, p1_fire_coord)
        self.manager.fire(self.p2, p2_fire_coord)

        p1_recv_coord, p1_ship, p1_sunk = self.manager.incoming(self.p1)
        p2_recv_coord, p2_ship, p2_sunk = self.manager.incoming(self.p2)

        self.assertEqual(p1_recv_coord, p2_fire_coord)
        self.assertEqual(p2_recv_coord, p1_fire_coord)

        # Test ship miss
        self.assertEqual(p1_ship, None)
        self.assertEqual(p2_ship, None)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        # Test the ship hit
        self.manager.fire(self.p1, p1_ship2.coordinates[0])
        self.manager.fire(self.p2, p1_ship2.coordinates[0])

        p1_recv_coord, p1_ship, p1_sunk = self.manager.incoming(self.p1)
        p2_recv_coord, p2_ship, p2_sunk = self.manager.incoming(self.p2)
        
        self.assertEqual(p1_ship, p1_ship2)
        self.assertEqual(p2_ship, p2_ship2)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)
        
        # Test ship sunk
        self.manager.fire(self.p1, p1_ship2.coordinates[1])
        self.manager.fire(self.p2, p1_ship2.coordinates[1])

        p1_recv_coord, p1_ship, p1_sunk = self.manager.incoming(self.p1)
        p2_recv_coord, p2_ship, p2_sunk = self.manager.incoming(self.p2)
        
        self.assertEqual(p1_ship, p1_ship2)
        self.assertEqual(p2_ship, p2_ship2)
        
        self.assertTrue(p1_sunk)
        self.assertTrue(p2_sunk)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        # Test ship not sunk
        self.manager.fire(self.p1, p1_ship1.coordinates[0])
        self.manager.fire(self.p2, p1_ship1.coordinates[0])

        p1_recv_coord, p1_ship, p1_sunk = self.manager.incoming(self.p1)
        p2_recv_coord, p2_ship, p2_sunk = self.manager.incoming(self.p2)

        self.assertTrue(not p1_sunk)
        self.assertTrue(not p2_sunk)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)

        # Test OutofTurnException
        self.manager.fire(self.p1, (7,7))

        self.assertRaises(OutOfTurnException, self.manager.incoming, self.p1)

        self.manager.fire(self.p2, (7,7))
        self.manager.incoming(self.p1)
        self.manager.incoming(self.p2)

        self.manager.outgoing(self.p1)
        self.manager.outgoing(self.p2)        

        self.manager.fire(self.p2, (3,3))

        self.assertRaises(OutOfTurnException, self.manager.incoming, self.p2)


if __name__ == "__main__":
    unittest.main()
