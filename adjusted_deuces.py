import deuces

class DistLookupTable(deuces.lookup.LookupTable):
    '''
        Deuces ranks each set of 5 cards, by making the most of the fact that there 
        are only 7462 distinct hands in the poker. There is a lot of degeneracy.

        However, to know how good your hand is, you need to not only know its rank but
        also the distribution of hands for a given rank. This is very straightforward.

        Using the well documented values from Deuces:

                         Distinct Hands   Degeneracy/Hand
        Straight Flush        10                4       [(4 choose 1)]
        Four of a Kind        156               4       [(4 choose 4) * (4 choose 1)]
        Full Houses           156               24      [(4 choose 3) * (4 choose 2)]
        Flush                 1277              4       [(4 choose 1)]
        Straight              10                1020    [(4^5) - 4 flushes]
        Three of a Kind       858               64      [(4 choose 3) * 4^2]
        Two Pair              858               144     [(4 choose 2) * (4 choose 1) * 4^1]
        One Pair              2860              384     [(4 choose 2) * 4^3]
        High Card             1277              1020    [(4^5) - 4 flushes]
        ----------------------------------------------
        
        TOTAL DISTINCT HANDS       7462
        TOTAL NUMBER OF HANDS      2598960

        Using this a both a normalised distribution function f(x) can be defined and 
        also a cumulative distribution function. 

        This function returns the normalised distribution function for a rank. 
        '''
    def __init__(self):
        super(DistLookupTable, self).__init__()
    
    MAX_STRAIGHT_FLUSH  = 10
    MAX_FOUR_OF_A_KIND  = 166
    MAX_FULL_HOUSE      = 322 
    MAX_FLUSH           = 1599
    MAX_STRAIGHT        = 1609
    MAX_THREE_OF_A_KIND = 2467
    MAX_TWO_PAIR        = 3325
    MAX_PAIR            = 6185
    MAX_HIGH_CARD       = 7462
    
    MAX_TO_PERCENTILE = {
            MAX_STRAIGHT_FLUSH: 0,
            MAX_FOUR_OF_A_KIND: 40,
            MAX_FULL_HOUSE: 664,
            MAX_FLUSH: 4408,
            MAX_STRAIGHT: 9516,
            MAX_THREE_OF_A_KIND: 19716,
            MAX_TWO_PAIR: 74628,
            MAX_PAIR: 198180,
            MAX_HIGH_CARD: 1296420
        }

    MAX_TO_DEGENERACY = {
            MAX_STRAIGHT_FLUSH: 4,
            MAX_FOUR_OF_A_KIND: 4,
            MAX_FULL_HOUSE: 24,
            MAX_FLUSH: 4,
            MAX_STRAIGHT: 1020,
            MAX_THREE_OF_A_KIND: 64,
            MAX_TWO_PAIR: 144,
            MAX_PAIR: 384,
            MAX_HIGH_CARD: 1020
        }

    RANK_CLASS_TO_DEGENERACY = {
            1: 4,
            2: 4,
            3: 24,
            4: 4,
            5: 1020,
            6: 64,
            7: 144,
            8: 384,
            9: 1020
        }

    MAX_ALL_HANDS = 2598960

class DistributionsEvaluator(deuces.evaluator.Evaluator):
    def __init__(self):
        super(DistributionsEvaluator, self).__init__()
        self.table = DistLookupTable()

    def get_five_card_rank_probability_distribution(self, hr):
        class_degeneracy = DistLookupTable.RANK_CLASS_TO_DEGENERACY[self.get_rank_class(hr)]
        return float(class_degeneracy)/float(DistLookupTable.MAX_HANDS)
        
    def get_five_card_rank_percentile(self, hr):
        """
        Returns the class of hand given the hand hand_rank
        returned from evaluate. 
        """
        if hr >= 0 and hr <= DistLookupTable.MAX_STRAIGHT_FLUSH:
            lower_hds_in_rc = (hr - 0) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_STRAIGHT_FLUSH]            
            lower_hds_not_in_rc = 0
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS) 
        
        elif hr <= DistLookupTable.MAX_FOUR_OF_A_KIND:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_STRAIGHT_FLUSH) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_FOUR_OF_A_KIND]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_FOUR_OF_A_KIND]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_FULL_HOUSE:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_FOUR_OF_A_KIND) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_FULL_HOUSE]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_FULL_HOUSE]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_FLUSH:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_FULL_HOUSE) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_FLUSH]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_FLUSH]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_STRAIGHT:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_FLUSH) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_STRAIGHT]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_STRAIGHT]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_THREE_OF_A_KIND:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_STRAIGHT) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_THREE_OF_A_KIND]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_THREE_OF_A_KIND]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_TWO_PAIR:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_THREE_OF_A_KIND) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_TWO_PAIR]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_TWO_PAIR]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_PAIR:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_TWO_PAIR) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_PAIR]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_PAIR]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        
        elif hr <= DistLookupTable.MAX_HIGH_CARD:
            lower_hds_in_rc = (hr - DistLookupTable.MAX_PAIR) * DistLookupTable.MAX_TO_DEGENERACY[DistLookupTable.MAX_HIGH_CARD]            
            lower_hds_not_in_rc = DistLookupTable.MAX_TO_PERCENTILE[DistLookupTable.MAX_HIGH_CARD]
            return float(lower_hds_in_rc + lower_hds_not_in_rc)/float(DistLookupTable.MAX_ALL_HANDS)  
        else:
            raise Exception("Invalid hand rank, cannot return rank class")

deuces.Evaluator = DistributionsEvaluator


