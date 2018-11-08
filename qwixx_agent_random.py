

import random


class QwixxAgentRandom():


	def __init__(self, playerIndex):
		#print("Init Qwixx agent random, playerIndex=" + str(playerIndex))
		self.playerIndex = playerIndex

	
	def get_next_action(self, env, diceThrow, availableActions):
		chosenAction = random.choice(availableActions)
		return chosenAction


