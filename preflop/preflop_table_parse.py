VALS = set(['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'])
SUITS = set(['s', 'd', 'c', 'h'])
CARDS = set([a+b for a in VALS for b in SUITS])
def isomorphic(hand):
	j = list(hand)
	isoset = set()
	if j[0][1]==j[1][1]:
		# same suit
		for a in SUITS:
			isoset.add(frozenset([j[0][0]+a,j[1][0]+a]))
	else:
		for a in SUITS:
			for b in SUITS:
				if a!=b:
					isoset.add(frozenset([j[0][0]+a,j[1][0]+b]))
	
	return isoset
import pickle
# NITER = 10000
probdict = {}
# # hand = frozenset(['As','Ad'])
# # ii = isomorphic(hand)
# # print(ii)

inputFileText = open("preflop_table_raw", "r").read().split('\n')
for row in inputFileText:
	pack = row.split()
	if pack[0][:5] not in ['Cards','http:']:
		upc = pack[0]
		odds = float(pack[1][:-1])/100.
		print(upc,odds)
		if upc[-1]=='s':
			hand = frozenset([upc[0]+'s',upc[1]+'s'])
		else:
			hand = frozenset([upc[0]+'s',upc[1]+'h'])
		hands = isomorphic(hand)
		for h in hands:
			probdict[h]=odds
pickle.dump(probdict, open( "preflop_odds.pkl", "wb" ) )
		# print(row)


# probdict[frozenset hand]=probdict


# for card in CARDS:
# 	deck2 = CARDS.copy()
# 	deck2.remove(card)
# 	for card2 in deck2:
# 		hand = frozenset([card])
# 	# print(card in deck2)
# 	# print(len(deck2))
# 	break