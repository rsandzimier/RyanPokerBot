import pickle
from pbots_calc import calc
import time
import math

vals_dict = {'A':14,'K':13,'Q':12,'J':11,'T':10,'9':9,'8':8,'7':7,'6':6,'5':5,'4':4,'3':3,'2':2}
VALS = ['A','K','Q','J','T','9','8','7','6','5','4','3','2']
SUITS = ['a','b','c','d']
CARDS = [a+b for a in VALS for b in SUITS]

card_keys5 = []

for card1 in [c for c in CARDS if c[1] in SUITS[:1]]:
	for card2 in [c for c in CARDS if c[1] in SUITS[:2] and vals_dict[card1[0]]>=vals_dict[c[0]] and not c in [card1]]:
		for card3 in [c for c in CARDS if c[1] in SUITS[:len(set([card1[1],card2[1]]))+1] and not c in [card1,card2]]:
			for card4 in [c for c in CARDS if c[1] in SUITS[:len(set([card1[1],card2[1],card3[1]]))+1] and vals_dict[card3[0]]>=vals_dict[c[0]] and not c in [card1,card2,card3]]:
				for card5 in [c for c in CARDS if c[1] in SUITS[:min(len(set([card1[1],card2[1],card3[1],card4[1]]))+1,4)] and vals_dict[card4[0]]>=vals_dict[c[0]] and not c in [card1,card2,card3,card4]]:
						card_keys5.append(card1+card2+card3+card4+card5)

print len(card_keys5)



probdict = {}

start_time = time.time()

i = 0

for key in card_keys5:
	cards = key[0:4].replace('a','s').replace('b','h') # c maps to c, d maps to d
	board_cards = key[4:10].replace('a','s').replace('b','h') # c maps to c, d maps to d
	probdict[key] = calc(cards + ':xx', board_cards, '', 1000).ev[0]
	i += 1
	if i%int(len(card_keys5)*0.005)==0:
		print str(i*100.0/len(card_keys5)) + '% complete. Estimated time remaining: ' + str((len(card_keys5)-i)*((time.time()-start_time)/i)*(1/60.0)) + ' minutes'

pickle.dump(probdict, open( "postflop_odds.pkl", "wb" ) )

#print hand_list
#len(set([card1[1],card2[1]]))+1