from smithers_framework import BotFramework
from adjusted_deuces import deuces as dc

import random
from collections import OrderedDict
from itertools import combinations

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
        self.evaluator = dc.Evaluator()
        
        self.cards = None
        self.board = []
        self.pot = None
        self.percentile = None
        self.win_odds = None
        self._deuces_rank = None

        self.not_broke_competitors = 0
        self.not_folded_competitors = 0


    def register(self):
        super(BadOddsBot, self).register()

    def play(self):
        super(BadOddsBot, self).play()

    def set_up_competitors(self, competitors):
        for i, c in enumerate(competitors):
            comp = self.CompetitorModel(name=c["name"], chips=c["chips"], seat=i)
            self.competitors[c["name"]] = comp

    def receive_tournament_start_message(self, players):
        self.not_broke_competitors = len(self.competitors)
        self.not_folded_competitors = len(self.competitors)
        print "tournament starting: %s players: %s" % (
                  len(players), ", ".join([p["name"] for p in players]))

    def receive_move_message(self, player_name, move, amount, chips_left, is_blind):
        # print "received a move from another " + \
        #       "player: %s, move: %s, amount: %s, chips_left: %s, is a blind? %s" % (
        #           player_name, move, amount, chips_left, is_blind)
        print "%s %s" %(player_name, move)
        if move=="FOLD":
            self.not_folded_competitors -= 1
        pass

    def receive_hands_message(self, card1, card2):
        self.cards = [dc.Card.new(card1), dc.Card.new(card2)]
        dc.Card.print_pretty_cards(self.cards)

    def receive_board_message(self, board, pot):
        self.board = [dc.Card.new(b) for b in board]
        if not self.cards:
            return 
        dc.Card.print_pretty_cards(self.board)

        if len(board) == 3:
            self.win_odds = self.monte_carlo_expected_winnings(self.cards, self.board, self.evaluator,  10) 
        elif len(board) == 4:
            self.win_odds = self.monte_carlo_expected_winnings(self.cards, self.board, self.evaluator, 990) 
        elif len(board) == 5:
            self.win_odds = self.monte_carlo_expected_winnings(self.cards, self.board, self.evaluator, 990) 

        print "\t1:2:1 %.2f" %self.win_odds
        pow(self.win_odds, self.not_folded_competitors)
        self.win_odds = pow(self.win_odds, self.not_folded_competitors)


    def receive_results_message(self, results_list):
        self.not_folded_competitors = self.not_broke_competitors
        self.win_odds = None
        self.percentile = None
        self.cards = None
        print "received the results of the hand:"
        for r in results_list:
            print "RESULTS: player: %s, winnings: %s, hand: %s" % (r[0], r[1], r[2])

    def receive_broke_message(self, names):
        self.not_broke_competitors -= 1
        print "player(s): %s went bust" % (", ".join(names))

    def receive_tournament_winner_message(self, name):
        print "player: %s won the tournament" % name

    def on_move_request(self, min_raise, call, pot, current_bet, chips):
        moves = [
            ("RAISE_TO", min_raise),
            ("CALL", call),
            ("FOLD", 0)
        ]

        if self.win_odds:
            print  "\tTO CALL:", call, " POT: ", pot, " CURRENT BET", current_bet
            
            pot_odds = float(call-current_bet)/float(call-current_bet + pot)
            raise_odds = float(min_raise-current_bet)/float(min_raise-current_bet + pot)
            
            print "\tWIN RATE: %.2f  POT ODDS: %.2f" %(self.win_odds*100,pot_odds *100)
            if self.win_odds >= pot_odds:
                if raise_odds < self.win_odds:
                    move = moves[0]
                else:
                    move = moves[1]
            else:
                move = moves[2]
        else:
            move = moves[1]
        
        print "\tmoved: %s, %s" % move
        return move

    # @staticmethod
    # def _calculate_exp_percentile(cards, board, evaluator):
    #     if not cards or not board:
    #         return -1
    #     full_deck = set(dc.Deck.GetFullDeck())
    #     active_deck = full_deck - set(cards+board)
    #     missing = 5 - len(board) 

    #     percentiles = []

    #     combos = combinations(active_deck, missing)
    #     for c in combos:
    #         new_board = board + list(c)
    #         rank = evaluator.evaluate(cards, new_board)
    #         percentile = evaluator.get_five_card_rank_percentile(rank)
    #         percentiles.append(percentile)

    #     if not c:
    #         rank = evaluator.evaluate(cards, board)
    #         percentile = evaluator.get_five_card_rank_percentile(rank)
    #         percentiles.append(percentile)
        
    #     mean = float(sum(percentiles))/float(len(percentiles))
    #     return (1 - mean) * 100


    def monte_carlo_expected_winnings(self, cards, board, evaluator, sample):
        if not cards or not board:
            return -1

        full_deck = set(dc.Deck.GetFullDeck())
        active_deck = full_deck - set(cards+board)
        missing = 5 - len(board)    

        winners = []
        for c in combinations(active_deck, missing):
            new_board = board + list(c)

            our_hand = evaluator.evaluate(cards, new_board)  
            result = self.monte_carlo_sample(our_hand, cards, new_board, evaluator, sample)
    
            winners.append(result)
            
        # print "PROBABILITY OF WINNING %.2f " % (float(sum(winners)*100)/float(len(winners)))
        return float(sum(winners))/float(len(winners))

    def monte_carlo_sample(self, our_score, our_cards, board, evaluator, sample_number):
        full_deck = set(dc.Deck.GetFullDeck())
        active_deck = full_deck - set(our_cards+board)
        missing = 2

        winners = 0

        combos = [c for c in combinations(active_deck, missing)]

        for their_cards in random.sample(combos, sample_number):
            their_score = evaluator.evaluate(list(their_cards), board)
            if our_score <= their_score:
                winners += 1

        return float(winners)/float(sample_number)







if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) >= 2 else ""
    # name = name if name else "randombot":
    # "raw_socket_listener -> tcp://127.0.0.1:9950"
    pb = BadOddsBot(name, "http://localhost:6767")
    # pb.is_test = True
    pb.register()
    pb.play()
