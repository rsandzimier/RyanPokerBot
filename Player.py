from pokerbots import Bot, parse_args, run_bot
from pokerbots.actions import FoldAction, CallAction, CheckAction, BetAction, RaiseAction, ExchangeAction
import time
import pickle
import json
import sys

try:
    from pbots_calc import calc
except ImportError:
    calc = None
    print "Warning: could not import calc"
#from equity_calc import calc

import random
import numpy as np
import math
"""
Simple example pokerbot, written in python.
"""
vals_dict = {'A':14,'K':13,'Q':12,'J':11,'T':10,'9':9,'8':8,'7':7,'6':6,'5':5,'4':4,'3':3,'2':2}

def full_deck():
    return ['As','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks',
    'Ad','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd',
    'Ac','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc',
    'Ah','2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh']
    
def full_range():
    deck = full_deck();
    hand_range = [];
    for i in range(0,len(deck)):
        for j in range(i+1, len(deck)):
            hand_range.append(''.join([deck[i], deck[j]]))
    return hand_range

class Player(Bot):
    def handle_new_game(self, new_game):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        new_game: the pokerbots.Game object.

        Returns:
        Nothing.
        '''
        self.check_fold = False
        with open('preflop/preflop_odds.pkl','rb') as fp:
            self.preflop_odds = pickle.load(fp)
        with open('postflop/postflop_odds.json','r') as fp:
            self.postflop_odds = json.load(fp)
            pass
        print len(self.postflop_odds)
        #self.postflop_odds = pickle.load(open('postflop/postflop_odds.pkl','rb'))

        self.moves = 0
        self.phase = 0 # 0:blinds, 1:pre-flop bet, 2:pre-flop exchange, 3:flop bet, 4:flop exchange, 5: turn bet, 6:turn exchange, 7:river bet
        self.firstToAct = True
        self.actedThisPhase = False
        self.actedThisPhase_opp = False

        self.opp_range_all = [];
        self.opp_range = [];

        self.bet = 1
        self.bet_opp = 1
        self.exchanges = 0
        self.exchanges_opp = 0
        self.stack = new_game.round_stack
        self.stack_opp = new_game.round_stack

        self.norm_ratio = 999

        self.betting_history = []

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
        print "ROUND #" + str(new_round.hand_num)

        self.opp_range_all = full_range()
        self.opp_range = self.opp_range_all[:]

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
        #if len(board_cards) > 3: print "TURN OR RIVER"
        while (self.moves < len(move_history)):
            self.handleMove(move_history[self.moves],game,board_cards)
            self.moves += 1
        
        self.moves = 0
        self.phase = 0
        self.firstToAct = True
        self.actedThisPhase = False
        self.actedThisPhase_opp = False
        self.bet = 1
        self.bet_opp = 1
        self.exchanges = 0
        self.exchanges_opp = 0
        self.stack = game.round_stack
        self.stack_opp = game.round_stack
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
        print time_left
        if len(self.opp_range_all) == 1326:
            self.removeSeenFromOppRange(cards)
        while (self.moves < len(move_history)):
            self.handleMove(move_history[self.moves],game,board_cards)
            self.moves += 1

        if calc is not None:
            result = calc(''.join(cards) + ':' + ','.join(self.opp_range), ''.join(board_cards), ''.join(self.discarded_cards), 1000)
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
            if len(board_cards) == 0: return CheckAction() # Never exchange pre-flop

            strength_exchange = calc('xx:' + ','.join(self.opp_range), ''.join(board_cards), ''.join(self.discarded_cards)+''.join(cards), 1000).ev[0]
            exchange_cost = cost_func(ExchangeAction())
            exchange_ev = strength_exchange * (pot.grand_total + exchange_cost) - exchange_cost
            check_ev = strength * pot.grand_total
            if exchange_ev > check_ev:  # exchanging is worth it
                self.discarded_cards |= set(cards)  # keep track of the cards we discarded
                return ExchangeAction()
            return CheckAction()
        else:  # decision to commit resources to the pot
            margin = game.big_blind/2.0 + 1.0
            if round.bankroll > 0: margin *= 1
            elif round.bankroll < 0: margin *= -1
            else: margin *= 0;
            bb_per_hand_ahead = (round.bankroll-margin)/(game.num_hands - round.hand_num + 1.0)

            if bb_per_hand_ahead > 1.5:
                if not self.check_fold: print 'WIN SECURE. START CHECK FOLDING. ROUND #' + str(round.hand_num)
                self.check_fold = True
                if CheckAction in legal_moves: return CheckAction()
                else: return FoldAction()

            #if len(board_cards) == 0 and pot.opponent_bets <= 2 and strength > 0.3:
            #    min_bet = math.ceil(max(4.0 - 4.0*bb_per_hand_ahead,0))
            #    if BetAction in legal_moves and min_bet > min_amount:
            #        return BetAction(min_bet)
            #    elif RaiseAction in legal_moves and min_bet > min_amount:
            #        return RaiseAction(min_bet)

            aggression_factor = min(max((1.5-bb_per_hand_ahead)/3.0 +np.random.normal(0.0,0.05),0.0),1.0)  # 0 no aggression, 1 full aggression

            continue_cost = cost_func(CallAction()) if CallAction in legal_moves else cost_func(CheckAction())
            # figure out how to raise the stakes
            if aggression_factor < 0.25:
                commit_amount = int(pot.pip + continue_cost+4*math.sqrt(max(strength-0.6,0.0))*aggression_factor*(pot.grand_total + continue_cost))
            elif aggression_factor > 0.6:
                commit_amount = int(pot.pip + continue_cost+2*math.sqrt(strength)*aggression_factor*(pot.grand_total + continue_cost))
            else:
                commit_amount = int(pot.pip + continue_cost+2*math.sqrt(max(strength-0.3,0.0))*aggression_factor*(pot.grand_total + continue_cost))

            if min_amount is not None:
                commit_amount = max(commit_amount, min_amount)
            if max_amount is not None:
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
                    strength -= 0.5*min(1.0-aggression_factor,0.5) #(max(min(0.75,continue_cost/(pot.grand_total-continue_cost)),0.25)-0.25)*(1.0-aggression_factor)  # intimidation factor

                # calculate pot odds: is it worth it to stay in the game?
                pot_odds = float(continue_cost) / (pot.grand_total + continue_cost)
                if strength >= pot_odds:  # staying in the game has positive EV
                    #if len(board_cards) == 0 and continue_cost == 1 and strength < 0.8*min(1.0-aggression_factor,0.5):
                    #    return FoldAction()
                    #if strength > 1.15-aggression_factor and 2*random.random()*(1.0-aggression_factor) < strength:  # commit more sometimes
                    #    return commit_action
                    if strength > 0.5 and random.random() < strength:  # commit more sometimes
                        return commit_action
                    return CallAction()
                else:  # staying in the game has negative EV
                    return FoldAction()

            elif continue_cost == 0:
                #if len(board_cards) == 0:
                #    if 2*0.63*np.random.normal(1.0,0.1)*(1.0-aggression_factor) < strength:  # balance bluffs with value bets
                #        return commit_action
                #else:
                if random.random() < strength: #np.random.normal(1.0,0.2)*(1.0-aggression_factor) < strength:  # balance bluffs with value bets
                    return commit_action
                return CheckAction()

        # Default to checkcall
        if CallAction in legal_moves:
            return CallAction()
        else:
            return CheckAction()

    def options_betting(self):
        options = [[],[]]
        if self.bet_opp > self.bet:
            return [[],[]]
        if self.bet_opp == 0 and self.bet == 0:
            options[0].append("CHECK")
            if self.stack > 0 and self.stack_opp > 0:
                maxbet = min([self.stack, self.stack_opp])
                minbet = min([2, maxbet])
                options[0].append("BET")
                options[1].append(minbet)
                options[1].append(maxbet)
        elif self.bet_opp == self.bet:
            options[0].append("CHECK")
            if self.stack-self.bet > 0 and self.stack_opp - self.bet_opp > 0:
                maxraise = min([self.stack, self.stack_opp])
                minraise = min([2+self.bet, maxraise])
                options[0].append("RAISE")
                options[1].append(minraise)
                options[1].append(maxraise)
        elif self.bet_opp < self.bet:
            options[0].append("CALL")
            options[0].append("FOLD")
            if self.stack-self.bet > 0 and self.stack_opp - self.bet > 0:
                maxraise = min([self.stack, self.stack_opp])
                minraise = min([max([2+self.bet, self.bet-self.bet_opp+self.bet]), maxraise])
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

    def options_exchanging(self):
        options = []
        options.append('CHECK')

        if self.stack_opp > 2**(self.exchanges_opp + 1):
            options.append('EXCHANGE')

        if "CHECK" in options:
            self.hold_option_count += 1
            self.hold_count_weighted += 1.0/len(options)                        
        if "EXCHANGE" in options:
            self.exchange_option_count += 1
            self.exchange_count_weighted += 1.0/len(options)
        return options

    def round_over_return(self, game, round):
        call_ratio = 0 if self.call_count == 0 else self.call_count_weighted/self.call_count
        check_ratio = 0 if self.check_count == 0 else self.check_count_weighted/self.check_count
        bet_ratio = 0 if self.bet_count == 0 else self.bet_count_weighted/self.bet_count
        raise_ratio = 0 if self.raise_count == 0 else self.raise_count_weighted/self.raise_count
        fold_ratio = 0 if self.fold_count == 0 else self.fold_count_weighted/self.fold_count
        hold_ratio = 0 if self.hold_count == 0 else self.hold_count_weighted/self.hold_count
        exchange_ratio = 0 if self.exchange_count == 0 else self.exchange_count_weighted/self.exchange_count
        self.norm_ratio = np.sqrt((call_ratio-1.0)**2+(check_ratio-1.0)**2+(bet_ratio-1.0)**2+(raise_ratio-1.0)**2+(fold_ratio-1.0)**2+(hold_ratio-1.0)**2+(exchange_ratio-1.0)**2)
        
        if game.num_hands == round.hand_num:
            if self.call_option_count != 0: print 'CALL PERCENTAGE: ' + str(self.call_count*100.0/self.call_option_count) + ' ' + str(self.call_count) + ' ' + str(self.call_option_count)
            if self.check_option_count != 0: print 'CHECK PERCENTAGE: ' + str(self.check_count*100.0/self.check_option_count) + ' ' + str(self.check_count) + ' ' + str(self.check_option_count)
            if self.bet_option_count != 0: print 'BET PERCENTAGE: ' + str(self.bet_count*100.0/self.bet_option_count) + ' ' + str(self.bet_count) + ' ' + str(self.bet_option_count) 
            if self.raise_option_count != 0: print 'RAISE PERCENTAGE: ' + str(self.raise_count*100.0/self.raise_option_count) + ' ' + str(self.raise_count) + ' ' + str(self.raise_option_count)
            if self.fold_option_count != 0: print 'FOLD PERCENTAGE: ' + str(self.fold_count*100.0/self.fold_option_count) + ' ' + str(self.fold_count) + ' ' + str(self.fold_option_count)
            if self.hold_option_count != 0: print 'HOLD PERCENTAGE: ' + str(self.hold_count*100.0/self.hold_option_count) + ' ' + str(self.hold_count) + ' ' + str(self.hold_option_count)
            if self.exchange_option_count != 0: print 'EXCHANGE PERCENTAGE: ' + str(self.exchange_count*100.0/self.exchange_option_count) + ' ' + str(self.exchange_count) + ' ' + str(self.exchange_option_count)
            print ''

            print 'CALL WEIGHTED RATIO: ' + str(call_ratio) + ' ' + str(self.call_count_weighted) + ' ' + str(self.call_count)
            print 'CHECK WEIGHTED RATIO: ' + str(check_ratio) + ' ' + str(self.check_count_weighted) + ' ' + str(self.check_count)
            print 'BET WEIGHTED RATIO: ' + str(bet_ratio) + ' ' + str(self.bet_count_weighted) + ' ' + str(self.bet_count) 
            print 'RAISE WEIGHTED RATIO: ' + str(raise_ratio) + ' ' + str(self.raise_count_weighted) + ' ' + str(self.raise_count)
            print 'FOLD WEIGHTED RATIO: ' + str(fold_ratio) + ' ' + str(self.fold_count_weighted) + ' ' + str(self.fold_count)
            print 'HOLD WEIGHTED RATIO: ' + str(hold_ratio) + ' ' + str(self.hold_count_weighted) + ' ' + str(self.hold_count)
            print 'EXCHANGE WEIGHTED RATIO: ' + str(exchange_ratio) + ' ' + str(self.exchange_count_weighted) + ' ' + str(self.exchange_count)
            print 'NORM WEIGHTED RATIO: ' + str(self.norm_ratio)
        sys.stdout.flush()
        return False

    def betFromMove(self, move, isB):
        i = 0
        if isB: i = 1

        bet_act = self.bet_opp if isB else self.bet
        bet_opp = self.bet if isB else self.bet_opp

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

        if isB and (move[:2] == 'BE' or move[:2] == 'RA'):
            maxraise = min([self.stack, self.stack_opp])
            minraise = min([max([2+self.bet, self.bet-self.bet_opp+self.bet]), maxraise])
            pot = 800 - self.stack - self.stack_opp + 2*max([self.bet,self.bet_opp])
            self.betting_history.append([bet_act,minraise,maxraise,pot,self.bet,self.bet_opp,self.stack,self.stack_opp])
            #print str(bet_act)+','+str(minraise)+','+str(maxraise)+',' + str(pot) + ',' + str(betA)+','+str(betB) + ',' + str(stackA)+','+str(stackB)
        if isB:
            self.bet_opp = bet_act
        else:
            self.bet = bet_act

    def exchangeFromMove(self, move, isB):
        if move[:2] == 'EX':
            if isB:
                self.exchange_count += 1
                self.opp_range = self.opp_range_all[:]
                print "B EXCHANGED"
            else: 
                self.removeSeenFromOppRange([move[15:17], move[18:20]])
            return True
        if isB:
            self.hold_count += 1
        return False

    def removeSeenFromOppRange(self, cards):
        for card in cards:
            self.opp_range_all = [x for x in self.opp_range_all if card not in x]
            self.opp_range = [x for x in self.opp_range if card not in x]

    def keyFromCards(self,cards,board_cards):
        #print [cards+board_cards]
        if vals_dict[cards[2]]>vals_dict[cards[0]]: cards = cards[2:4]+cards[0:2]
        if vals_dict[board_cards[2]]>vals_dict[board_cards[0]]: board_cards = board_cards[2:4]+board_cards[0:2]+board_cards[4:6]
        if vals_dict[board_cards[4]]>vals_dict[board_cards[2]]: board_cards = board_cards[0:2]+board_cards[4:6]+board_cards[2:4]
        if vals_dict[board_cards[2]]>vals_dict[board_cards[0]]: board_cards = board_cards[2:4]+board_cards[0:2]+board_cards[4:6]

        suits_key = ['a','b','e','f']
        suit_dict = {}
        key = cards+board_cards
        for i in range(0,5):
            if key[2*i+1] not in suit_dict:
                suit_dict[key[2*i+1]] = suits_key[len(suit_dict)]

        for suit in suit_dict:
            key = key.replace(suit,suit_dict[suit])
        key = key.replace('e','c')
        key = key.replace('f','d')
        #print key
        return key

    def reduceRangeBasedOnEV(self, pot, cost, board_cards, EV_thresh):
        if len(board_cards)==0:
            temp_range = []
            for cards in self.opp_range:
                if self.preflop_odds[frozenset([cards[0:2],cards[2:4]])]*(pot + 2*self.bet_opp) - cost >= EV_thresh:
                    temp_range.append(cards)
                else:
                    #print "Eliminating " + cards + " from opponent range"
                    pass
            self.opp_range = temp_range[:]
        if len(board_cards)==3:
            temp_range = []
            for cards in self.opp_range:
                if self.postflop_odds[self.keyFromCards(cards,''.join(board_cards))]*(pot + 2*self.bet_opp) - cost >= EV_thresh:
                    temp_range.append(cards)
                else:
                    #print "Eliminating " + cards + " from opponent range"
                    pass
                pass
            self.opp_range = temp_range[:]            


    def handleMove(self, move, game, board_cards):
        if (move[0:4] == "SHOW" and move[-1] != game.name):
            if not move[5:7]+move[8:10] in self.opp_range and not move[8:10]+move[5:7] in self.opp_range:
                print "OPPONENT SHOWED CARDS " + move[5:7]+move[8:10] + " WHICH WE PREVIOUSLY ELIMINATED"
            else:
                print "SHOWN CARDS WERE IN RANGE"
        if (self.phase >= 8): return

        myMove = (game.name == move[-1])
        
        if move[0:4] == "DEAL":
            self.removeSeenFromOppRange(board_cards)
            self.phase += 1
            return
        if move[0:4] == "FOLD":
            if not myMove:
                self.options_betting()
                self.betFromMove(move,True)
            self.phase = 8
            return
        # BLINDS
        if self.phase == 0:   
            if move[-1] == game.name:
                self.firstToAct = False
                self.bet_opp += 1
            else: 
                self.firstToAct = True
                self.bet += 1
            self.phase = 1
            return
        if move[0:4]=="POST": return
        # BET
        if self.phase%2==1:
            if myMove:
                self.betFromMove(move,False)
                self.actedThisPhase = True
            else:
                bet_opp_prev = self.bet_opp
                self.options_betting()
                self.betFromMove(move,True)
                self.actedThisPhase_opp = True
                self.reduceRangeBasedOnEV(2*game.round_stack-self.stack-self.stack_opp, self.bet_opp - bet_opp_prev, board_cards, 0)
            if self.actedThisPhase and self.actedThisPhase_opp and self.bet == self.bet_opp:
                self.stack -= self.bet
                self.stack_opp -= self.bet_opp
                self.bet = 0
                self.bet_opp = 0
                self.actedThisPhase = False
                self.actedThisPhase_opp = False
                self.phase += 1
            return
        # EXCHANGE
        if self.phase%2 == 0:
            if myMove:
                if (self.exchangeFromMove(move,False)):
                    self.exchanges += 1
                    self.stack = self.stack - 2**self.exchanges
            else:
                self.options_exchanging()
                if (self.exchangeFromMove(move,True)):
                    self.exchanges_opp = self.exchanges_opp + 1
                    self.stack_opp = self.stack_opp - 2**self.exchanges_opp
            return

if __name__ == '__main__':
    args = parse_args()
    run_bot(Player(), args)
