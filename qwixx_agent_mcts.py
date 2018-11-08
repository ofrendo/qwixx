from gym_qwixx.envs.qwixx_env import QwixxEnv
from qwixx_agent_random import QwixxAgentRandom
from qwixx_game_performer import QwixxGamePerformer

import random

# Monte carlo tree simulation
class QwixxAgentMCTS():


	def __init__(self, playerIndex):
		#print("Init Qwixx agent random, playerIndex=" + str(playerIndex))
		self.playerIndex = playerIndex

	
	def get_next_action(self, env, diceThrow, availableActionsParams):
	
		# For each action:
		# 	perform that action, then perform the rest of the game randomly
		actionValues = [-100] * (len(availableActionsParams)) # -100 because must be below -20
		
		for actionIndex in range(len(availableActionsParams)):
			# Clone env
			envClone = env.clone()
						
						
			availableActionsPerPlayer = []
			chosenActionPerPlayer = []
			
			# Assume other players collect actions this round randomly
			for playerIndex in range(envClone.numberPlayers):
				availableActions = envClone.get_available_actions(diceThrow, playerIndex)
				availableActionsPerPlayer.append(availableActions)
					
				if playerIndex != self.playerIndex:
					agent = QwixxAgentRandom(playerIndex)
					chosenAction = agent.get_next_action(envClone, diceThrow, availableActions)
					chosenActionPerPlayer.append(chosenAction)
				else:
					chosenActionPerPlayer.append(availableActionsParams[actionIndex])
			
			# Apply actions
			gamePerformer = QwixxGamePerformer(envClone.numberPlayers, envClone, [QwixxAgentRandom(playerIndex), QwixxAgentRandom(playerIndex)])
			gamePerformer.apply_action_tuple_per_player(diceThrow, chosenActionPerPlayer, availableActionsPerPlayer)
			
			if envClone.is_game_over() == False:
				envClone.next_round()
			
			# From then on perform rest of the game randomly
			result = gamePerformer.perform_complete_game()
			actionValues[actionIndex] = result[self.playerIndex]
			
		
		chosenActionIndex = self.argmax(actionValues)
		
		#print("actionValues:")
		#display(actionValues)
		#print("chosenActionIndex: " + str(chosenActionIndex))
		
		return availableActionsParams[chosenActionIndex]

	def argmax(self, actionValues):
		currentMax = -100
		currentIndex = -1
		for actionIndex in range(len(actionValues)):
			if actionValues[actionIndex] > currentMax:
				currentMax = actionValues[actionIndex]
				currentIndex = actionIndex
		
		return currentIndex


