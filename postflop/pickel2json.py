import pickle
import json

probdict = pickle.load(open('postflop_odds.pkl','rb'))
json.dump(probdict, open("postflop_odds.json", "w"))

#print hand_list
#len(set([card1[1],card2[1]]))+1