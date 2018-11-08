import traceback
from gym_qwixx.envs.qwixx_env import QwixxEnv
from qwixx_agent_random import QwixxAgentRandom
from qwixx_agent_mcts import QwixxAgentMCTS


class QwixxGamePerformer():
	
	def apply_action_tuple_per_player(self, diceThrow, chosenActionPerPlayer, availableActionsPerPlayer):
		for playerIndex in range(self.env.numberPlayers):
			availableActions = availableActionsPerPlayer[playerIndex]
			chosenAction = chosenActionPerPlayer[playerIndex]
			if (self.apply_action_tuple(playerIndex, diceThrow, chosenAction, availableActions)) == False:
				raise Exception("Error occured")
			
	
	
	def apply_action_tuple(self, playerIndex, diceThrow, chosenAction, availableActions):
		try:
			self.env.apply_action_tuple(playerIndex, chosenAction)
			return True
		except Exception as error: 
			print("Error applying player " + str(playerIndex) + " action! Current playerTurn: " + str(self.env.playerTurn) + ", current turnNumber=" + str(self.env.turnNumber))
			display(diceThrow)
			display(self.env.get_state())
			display(availableActions)
			display(chosenAction)
			display(error)
			traceback.print_tb(error.__traceback__)
			return False
		

	def __init__(self, numberPlayers, env=None, agents=None):

		if agents != None:
			self.agents = agents
		else: 
			self.agents = [QwixxAgentRandom(playerIndex) for playerIndex in range(numberPlayers)]
		
		if env != None:
			self.env = env
		else: 
			self.env = QwixxEnv()
			self.env.set_number_players(len(self.agents))
			self.env.reset()
		
		
	def perform_complete_game(self):
		gameOver = self.env.is_game_over()
		
		#print("Current gameOver=" + str(gameOver))
		#if gameOver == True:
		#		display(self.env.get_state())
			
		while gameOver == False:
			
			diceThrow = self.env.get_throw_all_dice()
			# n random agents
			chosenActionPerPlayer = []
			availableActionsPerPlayer = []
			
			# First collect action choosing
			for playerIndex in range(self.env.numberPlayers):
				availableActions = self.env.get_available_actions(diceThrow, playerIndex)
				availableActionsPerPlayer.append(availableActions)
				chosenAction = self.agents[playerIndex].get_next_action(self.env, diceThrow, availableActions)
				chosenActionPerPlayer.append(chosenAction)
				
			# Then perform actions
			self.apply_action_tuple_per_player(diceThrow, chosenActionPerPlayer, availableActionsPerPlayer)
			
			if self.env.is_game_over():
				gameOver = True
			else: 
				self.env.next_round()
		
		pointsResult = [self.env.get_points(playerIndex) for playerIndex in range(self.env.numberPlayers)]
		return pointsResult

