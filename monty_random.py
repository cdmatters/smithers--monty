from smithers_framework import BotFramework

import random
from collections import OrderedDict

class RandomBot(BotFramework):

    def __init__(self, name, server_url, listening_socket=None):
        super(RandomBot, self).__init__(name, server_url, listening_socket)
        self.competitors = OrderedDict()
        self.CompetitorModel = dict  # insert your own class here
        self.fold_pr = -1

    def register(self):
        super(RandomBot, self).register()

    def play(self):
        super(RandomBot, self).play()

    def set_up_competitors(self, competitors):
        print "set up folding probability"
        self.fold_pr = float(1)/float((len(self.competitors)+1)*2)

    def receive_tournament_start_message(self, players):
        pass

    def receive_move_message(self, player_name, move, amount, chips_left, is_blind):
        pass

    def receive_hands_message(self, card1, card2):
        pass

    def receive_board_message(self, board, pot):
        pass

    def receive_results_message(self, results_list):
        self.fold_pr = float(1)/float((len(self.competitors)+1)*2)
        print "reset folding probability"

    def receive_broke_message(self, names):
        pass

    def receive_tournament_winner_message(self, name):
        pass

    def on_move_request(self, min_raise, call, pot, current_bet, chips):
        
        moves = [
            ("RAISE_TO", min_raise),
            ("CALL", call),
            ("FOLD", 0)
        ]
        fold_now = random.random()

        if (self.fold_pr >= fold_now):
            move =  moves[2]
            print "moved: %s, %s" % move
            return move
        
        else:
            self.fold_pr = float(self.fold_pr)/float(2) # pr's converge
            moves.pop()
            
            raise_now = random.random()
            if raise_now < 0.25:
                move = moves[0]
            else:
                move = moves[1]
            print "moved: %s, %s" % move
            return move


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) >= 2 else ""
    pb = RandomBot(name, "http://localhost:6767")
    pb.register()
    pb.play()
