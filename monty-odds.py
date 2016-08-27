from smithers_framework import BotFramework
from adjusted_deuces import deuces as dc

import random
from collections import OrderedDict

class BadOddsBot(BotFramework):
    '''BadOddsBot is a poker bot that doesnt know how to play the odds in poker.
    It evaluates the hand that it could possibly have, and considers these odds 
    in the global possibility of hands. In other words, after the flop is dealt,
    it works out all scores of the hands it could have and their distribution. 
    It works out an expected value and plays these odds. 

    It does not consider what the opposition has or even distinguish between the 
    cards in its hand (that no other bot can have) and table cards. This means that
    if 3 of a kind are on the table it will bet aggressively, even if this means 
    opposition could be looking full house or even 4 of a kind.

    The aim is this should run in about half a second or less.  
    '''

    def __init__(self, name, server_url, listening_socket=None):
        super(BadOddsBot, self).__init__(name, server_url, listening_socket)
        self.competitors = OrderedDict()
        self.CompetitorModel = dict  # insert your own class here
        print dir(dc)
        self.evaluator = dc.Evaluator()
        
        self.cards = None
        self.board = []
        self.pot = 0
        self._current_odds = -1
        self._deuces_rank = -1


    def register(self):
        super(BadOddsBot, self).register()

    def play(self):
        super(BadOddsBot, self).play()

    def set_up_competitors(self, competitors):
        for i, c in enumerate(competitors):
            comp = self.CompetitorModel(name=c["name"], chips=c["chips"], seat=i)
            self.competitors[c["name"]] = comp

    def receive_tournament_start_message(self, players):
        print "tournament starting: %s players: %s" % (
                  len(players), ", ".join([p["name"] for p in players]))

    def receive_move_message(self, player_name, move, amount, chips_left, is_blind):
        print "received a move from another " + \
              "player: %s, move: %s, amount: %s, chips_left: %s, is a blind? %s" % (
                  player_name, move, amount, chips_left, is_blind)

    def receive_hands_message(self, card1, card2):
        self.cards = [dc.Card.new(card1), dc.Card.new(card2)]
        dc.Card.print_pretty_cards(self.cards)

    def receive_board_message(self, board, pot):
        self.board = [dc.Card.new(b) for b in board]
        if self.cards:
            self._deuces_rank = self.evaluator.evaluate(self.cards, self.board)
            print (1 - self.evaluator.get_five_card_rank_percentile(self._deuces_rank) )*100
        self.pot = pot
        dc.Card.print_pretty_cards(self.board)


    def receive_results_message(self, results_list):
        print "received the results of the hand:"
        for r in results_list:
            print "RESULTS: player: %s, winnings: %s, hand: %s" % (r[0], r[1], r[2])

    def receive_broke_message(self, names):
        print "player(s): %s went bust" % (", ".join(names))

    def receive_tournament_winner_message(self, name):
        print "player: %s won the tournament" % name

    def on_move_request(self, min_raise, call, pot, current_bet, chips):
        print  self._deuces_rank  

        moves = [
            ("RAISE_TO", min_raise),
            ("CALL", call),
            ("FOLD", 0)
        ]


        move = random.choice(moves)
        print "moved: %s, %s" % move
        return move



if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) >= 2 else ""
    # name = name if name else "randombot":
    # "raw_socket_listener -> tcp://127.0.0.1:9950"
    pb = BadOddsBot(name, "http://localhost:6767")
    # pb.is_test = True
    pb.register()
    pb.play()
