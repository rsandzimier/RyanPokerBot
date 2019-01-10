from pokerbots import Bot, parse_args, run_bot
from pokerbots.actions import FoldAction, CallAction, CheckAction, BetAction, RaiseAction, ExchangeAction

import random
"""
Simple example pokerbot, written in python.
"""


def full_deck():
    return ['As','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks',
    'Ad','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd',
    'Ac','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc',
    'Ah','2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh']

    


def simulate(cards, board_cards, dead_cards, n):
    rem_deck = [c for c in full_deck() if c not in cards and c not in board_cards and c not in dead_cards]
    for i in xrange(n):
        deck = rem_deck[:]
        board_cards_sim = board_cards[:]
        while len(board_cards_sim) < 5:
            j = random.randint(0,len(deck)-1)
            board_cards_sim.append(deck[j])
            deck.pop(j)
        opp_cards = []
        while len(opp_cards) < 2:
            j = random.randint(0,len(deck)-1)
            opp_cards.append(deck[j])
            deck.pop(j)
        #check_winner(cards, opp_cards, board_cards_sim)
    

class Player(Bot):
    def handle_new_game(self, new_game):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        new_game: the pokerbots.Game object.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game, new_round):
        '''
        Called when a new round starts. Called Game.num_rounds times.

        Arguments:
        game: the pokerbots.Game object for the new round.
        new_round: the new pokerbots.Round object.

        Returns:
        Nothing.
        '''
        pass

    def handle_round_over(self, game, round, pot, cards, opponent_cards, board_cards, result, new_bankroll, new_opponent_bankroll, move_history):
        '''
        Called when a round ends. Called Game.num_rounds times.

        Arguments:
        game: the pokerbots.Game object.
        round: the pokerbots.Round object.
        pot: the pokerbots.Pot object.
        cards: the cards you held when the round ended.
        opponent_cards: the cards your opponent held when the round ended, or None if they never showed.
        board_cards: the cards on the board when the round ended.
        result: 'win', 'loss' or 'tie'
        new_bankroll: your total bankroll at the end of this round.
        new_opponent_bankroll: your opponent's total bankroll at the end of this round.
        move_history: a list of moves that occurred during this round, earliest moves first.

        Returns:
        Nothing.
        '''
        pass

    def get_action(self, game, round, pot, cards, board_cards, legal_moves, cost_func, move_history, time_left, min_amount=None, max_amount=None):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the server needs an action from your bot.

        Arguments:
        game: the pokerbots.Game object.
        round: the pokerbots.Round object.
        pot: the pokerbots.Pot object.
        cards: an array of your cards, in common format.
        board_cards: an array of cards on the board. This list has len 0, 3, 4, or 5.
        legal_moves: a set of the move classes that are legal to make.
        cost_func: a function that takes a move, and returns additional cost of that move. Your returned move will raise your pot.contribution by this amount.
        move_history: a list of moves that have occurred during this round so far, earliest moves first.
        time_left: a float of the number of seconds your bot has remaining in this match (not round).
        min_amount: if BetAction or RaiseAction is valid, the smallest amount you can bet or raise to (i.e. the smallest you can increase your pip).
        max_amount: if BetAction or RaiseAction is valid, the largest amount you can bet or raise to (i.e. the largest you can increase your pip).
        '''
        simulate(cards,board_cards,[], 1)
        # Default to checkcall
        if CallAction in legal_moves:
            return CallAction()
        else:
            return CheckAction()


if __name__ == '__main__':
    args = parse_args()
    run_bot(Player(), args)