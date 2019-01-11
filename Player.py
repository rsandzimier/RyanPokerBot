from pokerbots import Bot, parse_args, run_bot
from pokerbots.actions import FoldAction, CallAction, CheckAction, BetAction, RaiseAction, ExchangeAction

try:
    from pbots_calc import calc
except ImportError:
    calc = None
    print "Warning: could not import calc"

import random
import numpy as np
"""
Simple example pokerbot, written in python.
"""


def full_deck():
    return ['As','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks',
    'Ad','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd',
    'Ac','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc',
    'Ah','2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh']
    


class Player(Bot):
    def handle_new_game(self, new_game):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        new_game: the pokerbots.Game object.

        Returns:
        Nothing.
        '''
        self.call_count = 0
        self.check_count = 0
        self.bet_count = 0
        self.raise_count = 0
        self.fold_count = 0
        self.hold_count = 0
        self.exchange_count = 0

        self.call_count_weighted = 0
        self.check_count_weighted = 0
        self.bet_count_weighted = 0
        self.raise_count_weighted = 0
        self.fold_count_weighted = 0
        self.hold_count_weighted = 0
        self.exchange_count_weighted = 0


        self.call_option_count = 0
        self.check_option_count = 0
        self.bet_option_count = 0
        self.raise_option_count = 0
        self.fold_option_count = 0
        self.hold_option_count = 0
        self.exchange_option_count = 0

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
        self.discarded_cards = set()

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
        #print 'ROUND ' + str(round.hand_num) +' OVER'


        #print move_history

        stackA = game.round_stack
        stackB = game.round_stack
        betA = 0
        betB = 0
        exchangeA = 0;
        exchangeB = 0;
        # BLINDS
        if move_history[0][-1] == 'A':
            firstToActIsA = False
            betA = betA + 1
            betB = betB + 2
        else:
            firstToActIsA = True
            betA = betA + 2
            betB = betB + 1
        move_history.pop(0)
        move_history.pop(0)
        # PRE-FLOP BET
        if not firstToActIsA:
            betA = self.betFromMove(move_history.pop(0),betA,betB,False)
        self.options_betting(stackA, stackB, betA, betB)
        if betA < 0: return self.round_over_return(game, round)
        betB = self.betFromMove(move_history.pop(0),betB,betA,True)
        if betB < 0: return self.round_over_return(game, round)
        if firstToActIsA or betB>betA:
            betA = self.betFromMove(move_history.pop(0),betA,betB,False)

        if betA < 0: return self.round_over_return(game, round)
        while(betA != betB):
            if betB < betA:
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
                if betB < 0: return self.round_over_return(game, round)
            else:
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
                if betA < 0: return self.round_over_return(game, round)

        stackA = stackA - betA
        stackB = stackB - betB

        betA = 0
        betB = 0

        # PRE-FLOP EXCHANGE
        while True:
            if firstToActIsA:
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
            else:
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
            if exchangeA_bool:
                exchangeA = exchangeA + 1
                stackA = stackA - 2**exchangeA
            if exchangeB_bool:
                exchangeB = exchangeB + 1
                stackB = stackB - 2**exchangeB
            if not exchangeA_bool and not exchangeB_bool:
                break
        move_history.pop(0)
        #(move_history.pop(0)[:2] != 'DE'
        # FLOP BET
        #print 'FLOP'
        while True and stackA!=0 and stackB != 0:
            if (betA == 0 and betB == 0 and firstToActIsA):
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if (betA == 0 and betB == 0 and not firstToActIsA):
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            if betB < betA or (betA == 0 and betB ==0 and firstToActIsA):
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            else:
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if betB < 0 or betA < 0:
                return self.round_over_return(game, round)
            if betA == betB:
                break
        stackA = stackA - betA
        stackB = stackB - betB

        betA = 0
        betB = 0

        # FLOP EXCHANGE
        while True:
            if firstToActIsA:
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
            else:
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
            if exchangeA_bool:
                exchangeA = exchangeA + 1
                stackA = stackA - 2**exchangeA
            if exchangeB_bool:
                exchangeB = exchangeB + 1
                stackB = stackB - 2**exchangeB
            if not exchangeA_bool and not exchangeB_bool:
                break
        move_history.pop(0)
        # TURN BET
        while True and stackA!=0 and stackB != 0:
            if (betA == 0 and betB == 0 and firstToActIsA):
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if (betA == 0 and betB == 0 and not firstToActIsA):
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            if betB < betA:
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            else:
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if betB < 0 or betA < 0:
                return self.round_over_return(game, round)
            if betA == betB:
                break
        stackA = stackA - betA
        stackB = stackB - betB

        betA = 0
        betB = 0

        # TURN EXCHANGE
        while True:
            if firstToActIsA:
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
            else:
                self.options_exchanging(stackB, exchangeB)
                exchangeB_bool = self.exchangeFromMove(move_history.pop(0),True)
                exchangeA_bool = self.exchangeFromMove(move_history.pop(0),False)
            if exchangeA_bool:
                exchangeA = exchangeA + 1
                stackA = stackA - 2**exchangeA
            if exchangeB_bool:
                exchangeB = exchangeB + 1
                stackB = stackB - 2**exchangeB
            if not exchangeA_bool and not exchangeB_bool:
                break
        move_history.pop(0)

        # RIVER BET

        while True and stackA!=0 and stackB != 0:
            if (betA == 0 and betB == 0 and firstToActIsA):
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if (betA == 0 and betB == 0 and not firstToActIsA):
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            if betB < betA:
                self.options_betting(stackA, stackB, betA, betB)
                betB = self.betFromMove(move_history.pop(0),betB,betA,True)
            else:
                betA = self.betFromMove(move_history.pop(0),betA,betB,False)
            if betB < 0 or betA < 0:
                return self.round_over_return(game, round)
            if betA == betB:
                break
        stackA = stackA - betA
        stackB = stackB - betB
        betA = 0
        betB = 0
        pass
        return self.round_over_return(game, round)


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



        if calc is not None:
            result = calc(''.join(cards) + ':xx', ''.join(board_cards), ''.join(self.discarded_cards), 1000)
            if result is not None:
                strength = result.ev[0]
            else:
                print "Warning: calc returned None"
                strength = random.random()
        else:
            strength = random.random()

        if ExchangeAction in legal_moves:  # decision to exchange
            # exchange logic
            # if we exchange, we should update self.discarded_cards
            exchange_cost = cost_func(ExchangeAction())
            exchange_ev = 0.5 * pot.opponent_total - 0.5 * (pot.total + exchange_cost)
            check_ev = strength * pot.opponent_total - (1. - strength) * pot.total
            if exchange_ev > check_ev:  # exchanging is worth it
                self.discarded_cards |= set(cards)  # keep track of the cards we discarded
                return ExchangeAction()
            return CheckAction()

        else:  # decision to commit resources to the pot
            continue_cost = cost_func(CallAction()) if CallAction in legal_moves else cost_func(CheckAction())
            # figure out how to raise the stakes
            commit_amount = int(pot.pip + continue_cost + 0.75 * (pot.grand_total + continue_cost))
            if min_amount is not None:
                commit_amount = max(commit_amount, min_amount)
                commit_amount = min(commit_amount, max_amount)

            if RaiseAction in legal_moves:
                commit_action = RaiseAction(commit_amount)
            elif BetAction in legal_moves:
                commit_action = BetAction(commit_amount)
            elif CallAction in legal_moves:  # we are contemplating an all-in call
                commit_action = CallAction()
            else:  # only legal action
                return CheckAction()

            if continue_cost > 0:  # our opponent has raised the stakes
                if continue_cost > 1 and strength < 1:  # tight-aggressive playstyle
                    strength -= 0.25  # intimidation factor
                # calculate pot odds: is it worth it to stay in the game?
                pot_odds = float(continue_cost) / (pot.grand_total + continue_cost)
                if strength >= pot_odds:  # staying in the game has positive EV
                    if strength > 0.5 and random.random() < strength:  # commit more sometimes
                        return commit_action
                    return CallAction()
                else:  # staying in the game has negative EV
                    return FoldAction()

            elif continue_cost == 0:
                if random.random() < strength:  # balance bluffs with value bets
                    return commit_action
                return CheckAction()


        # Default to checkcall
        if CallAction in legal_moves:
            return CallAction()
        else:
            return CheckAction()


    def options_betting(self, stackA, stackB, betA, betB):
        options = [[],[]]
        #print [stackA, stackB, betA, betB]
        if betB > betA:
            return [[],[]]
        if betB == 0 and betA == 0:
            options[0].append("CHECK")
            if stackA > 0 and stackB > 0:
                maxbet = min([stackA, stackB])
                minbet = min([2, maxbet])
                options[0].append("BET")
                options[1].append(minbet)
                options[1].append(maxbet)
        elif betB == betA:
            options[0].append("CHECK")

            if stackA-betA > 0 and stackB - betB > 0:
                maxraise = min([stackA, stackB])
                minraise = min([2+betA, maxraise])
                options[0].append("RAISE")
                options[1].append(minraise)
                options[1].append(maxraise)
        elif betB < betA:
            options[0].append("CALL")
            options[0].append("FOLD")

            if stackA-betA > 0 and stackB - betA > 0:
                maxraise = min([stackA, stackB])
                minraise = min([max([2+betA, betA-betB+betA]), maxraise])
                options[0].append("RAISE")
                options[1].append(minraise)
                options[1].append(maxraise)

        if "CALL" in options[0]:
            self.call_option_count += 1
            self.call_count_weighted += 1.0/len(options[0])
        if "CHECK" in options[0]:
            self.check_option_count += 1
            self.check_count_weighted += 1.0/len(options[0])
        if "BET" in options[0]:
            self.bet_option_count += 1
            self.bet_count_weighted += 1.0/len(options[0])
        if "RAISE" in options[0]:
            self.raise_option_count += 1
            self.raise_count_weighted += 1.0/len(options[0])                        
        if "FOLD" in options[0]:
            self.fold_option_count += 1
            self.fold_count_weighted += 1.0/len(options[0])
        return options

    def options_exchanging(self, stackB,exchangeB):
        options = []
        options.append('CHECK')

        if stackB > 2**(exchangeB + 1):
            options.append('EXCHANGE')

        if "CHECK" in options:
            self.hold_option_count += 1
            self.hold_count_weighted += 1.0/len(options)                        
        if "EXCHANGE" in options:
            self.exchange_option_count += 1
            self.exchange_count_weighted += 1.0/len(options)
        return options

    def round_over_return(self, game, round):
        if game.num_hands == round.hand_num:
            if self.call_option_count != 0: print 'CALL PERCENTAGE: ' + str(self.call_count*100.0/self.call_option_count) + ' ' + str(self.call_count) + ' ' + str(self.call_option_count)
            if self.check_option_count != 0: print 'CHECK PERCENTAGE: ' + str(self.check_count*100.0/self.check_option_count) + ' ' + str(self.check_count) + ' ' + str(self.check_option_count)
            if self.bet_option_count != 0: print 'BET PERCENTAGE: ' + str(self.bet_count*100.0/self.bet_option_count) + ' ' + str(self.bet_count) + ' ' + str(self.bet_option_count) 
            if self.raise_option_count != 0: print 'RAISE PERCENTAGE: ' + str(self.raise_count*100.0/self.raise_option_count) + ' ' + str(self.raise_count) + ' ' + str(self.raise_option_count)
            if self.fold_option_count != 0: print 'FOLD PERCENTAGE: ' + str(self.fold_count*100.0/self.fold_option_count) + ' ' + str(self.fold_count) + ' ' + str(self.fold_option_count)
            if self.hold_option_count != 0: print 'HOLD PERCENTAGE: ' + str(self.hold_count*100.0/self.hold_option_count) + ' ' + str(self.hold_count) + ' ' + str(self.hold_option_count)
            if self.exchange_option_count != 0: print 'EXCHANGE PERCENTAGE: ' + str(self.exchange_count*100.0/self.exchange_option_count) + ' ' + str(self.exchange_count) + ' ' + str(self.exchange_option_count)
            print ''

            call_ratio = 0 if self.call_count == 0 else self.call_count_weighted/self.call_count
            check_ratio = 0 if self.check_count == 0 else self.check_count_weighted/self.check_count
            bet_ratio = 0 if self.bet_count == 0 else self.bet_count_weighted/self.bet_count
            raise_ratio = 0 if self.raise_count == 0 else self.raise_count_weighted/self.raise_count
            fold_ratio = 0 if self.fold_count == 0 else self.fold_count_weighted/self.fold_count
            hold_ratio = 0 if self.hold_count == 0 else self.hold_count_weighted/self.hold_count
            exchange_ratio = 0 if self.exchange_count == 0 else self.exchange_count_weighted/self.exchange_count

            print 'CALL WEIGHTED RATIO: ' + str(call_ratio) + ' ' + str(self.call_count_weighted) + ' ' + str(self.call_count)
            print 'CHECK WEIGHTED RATIO: ' + str(check_ratio) + ' ' + str(self.check_count_weighted) + ' ' + str(self.check_count)
            print 'BET WEIGHTED RATIO: ' + str(bet_ratio) + ' ' + str(self.bet_count_weighted) + ' ' + str(self.bet_count) 
            print 'RAISE WEIGHTED RATIO: ' + str(raise_ratio) + ' ' + str(self.raise_count_weighted) + ' ' + str(self.raise_count)
            print 'FOLD WEIGHTED RATIO: ' + str(fold_ratio) + ' ' + str(self.fold_count_weighted) + ' ' + str(self.fold_count)
            print 'HOLD WEIGHTED RATIO: ' + str(hold_ratio) + ' ' + str(self.hold_count_weighted) + ' ' + str(self.hold_count)
            print 'EXCHANGE WEIGHTED RATIO: ' + str(exchange_ratio) + ' ' + str(self.exchange_count_weighted) + ' ' + str(self.exchange_count)
            print 'NORM WEIGHTED RATIO: ' + str(np.sqrt((call_ratio-1.0)**2+(check_ratio-1.0)**2+(bet_ratio-1.0)**2+(raise_ratio-1.0)**2+(fold_ratio-1.0)**2+(hold_ratio-1.0)**2+(exchange_ratio-1.0)**2))
            return True
        return False

    def betFromMove(self, move, bet_act, bet_opp, isB):
        i = 0
        if isB: i = 1
        if move[:2] == 'CA':
            bet_act = bet_opp
            self.call_count += i
        elif move[:2] == 'CH':
            bet_act = bet_act
            self.check_count += i
        elif move[:2] == 'FO':
            bet_act = -1
            self.fold_count += i
        elif move[:2] == 'RA':
            bet_act = int(move[6:move[6:].find(':')+6])
            self.raise_count += i
        elif move[:2] == 'BE':
            bet_act = int(move[4:move[4:].find(':')+4])
            self.bet_count += i
        return bet_act

    def exchangeFromMove(self, move, isB):
        i = 0
        if isB: i = 1
        if move[:2] == 'EX':
            self.exchange_count += i
            return True
        self.hold_count += i

        return False


if __name__ == '__main__':
    args = parse_args()
    run_bot(Player(), args)
