deck = []
for hex in range(0x0001F0A1,0x0001F0DF):
    if (hex % 16) not in [0, 12, 15]: # who TF put mahjong tiles between the playing cards?
        deck.append(chr(hex))
print(deck)
print(len(deck))