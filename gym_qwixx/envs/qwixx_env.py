

import numpy as np
from random import randint

import gym
from gym import spaces

import copy


class QwixxEnv(gym.Env):

	def _get_dice_throw(self):
		return randint(1,6)

	def get_throw_all_dice(self): 
		result = {
			"white1": self._get_dice_throw(),
			"white2": self._get_dice_throw(),
			"red": self._get_dice_throw(),
			"yellow": self._get_dice_throw(),
			"green": self._get_dice_throw(),
			"blue": self._get_dice_throw()
		}
		return result

	def get_color_dice(self, dice, rowIndex):
		if rowIndex == 0: 
			return dice["red"]
		if rowIndex == 1:
			return dice["yellow"]
		if rowIndex == 2:
			return dice["green"]
		if rowIndex == 3:
			return dice["blue"]
	
	
	def is_valid_action(self, playerIndex, action): 
		"""
		Check whether this is a valid action
		action[0]: rowIndex (color)
		action[1]: columnIndex (field of row)
		"""
		rowIndex = action[0]
		
		# Check whether any players have closed this row on a DIFFERENT turn
		if self._is_row_closed(rowIndex, self.turnNumber) == True:
			return False
		
		# Currently marked fields in a row
		markedFields = np.where(self.currentState[playerIndex][rowIndex] == 1)[0]
		highestCurrentColumnIndex = -1 # By default none are marked
		
		
		if markedFields.size > 0:
			highestCurrentColumnIndex = markedFields.max()
		
		
		if action[1] > highestCurrentColumnIndex:
			return True
		else:
			return False
		
	
	def get_available_actions_own_turn(self, dice, playerIndex):
		
		result = []
		
		# First possibility (white+white), which row should it be used for?
		for rowIndexI in range(5):
			
			firstAction = []
			
			if rowIndexI < 4:
				# Generate (white1+white2, X) actions
				firstAction = (rowIndexI, dice["white1"]+dice["white2"]-2)
				
				# Check whether this is a valid action
				if self.is_valid_action(playerIndex, firstAction) == False:
					continue
				
			else:
				# Generate (None, X) actions, don't use white+white
				firstAction = None
			
						
			
			# Second possibility (white+color), which row should it be used for?
			for rowIndexJ in range(5): 
			
				if rowIndexJ < 4:
					colorDice = self.get_color_dice(dice, rowIndexJ)
					
					# Generate (X, white1+color) actions
					secondAction_W1C = (rowIndexJ, dice["white1"]+colorDice-2)
					
					# Generate (X, white2+color) actions
					secondAction_W2C = (rowIndexJ, dice["white2"]+colorDice-2)

					# Check if each action is valid
					# Check that secondAction is larger than firstAction if in same row
					# (don't create actionTuple with two same actions or one where using color dice is smaller than white, since w1+w2 needs to be used first
					if (
						self.is_valid_action(playerIndex, secondAction_W1C) and  # Is white1+color even valid?
							(
								firstAction == None or 																# Either no first action
								firstAction[0] != secondAction_W1C[0] or											# First action is on a different row
								(firstAction[0]==secondAction_W1C[0] and firstAction[1] < secondAction_W1C[1])		# If they are on the same row, second action must be after firstAction
							)
						):
						
						result.append((firstAction, secondAction_W1C))
						
					if (
						self.is_valid_action(playerIndex, secondAction_W2C) and
							(
								firstAction == None or 
								firstAction[0] != secondAction_W2C[0] or
								(firstAction[0]==secondAction_W2C[0] and firstAction[1] < secondAction_W2C[1])
							) and
						dice["white1"] != dice["white2"]
						):
						# If white1==white2 then this results in 2x same actions since w1c already fills this
						result.append((firstAction, secondAction_W2C))
					
					
				elif firstAction is not None:
					# Generate (X, None) actions (don't use second possibility, white+color, only use white+white)
					secondAction = None
					
					result.append( (firstAction, secondAction) )
					
		
		# Generate (Fehlwurf, None) action
		# Get leftest possible Fehlwurf
		indexFehlwurf = int(sum(self.currentState[playerIndex][4]))
		actionFehlwurf = ((4, indexFehlwurf), None)
		result.append( actionFehlwurf )
		
		return result
		
		
		
	def get_available_actions_opponent_turn(self, dice, playerIndex): 
	
		result = []
	
		# Only possibility (white+white), which row should it be used for?
		for rowIndex in range(5): 
			
			if rowIndex < 4:
				colorDice = self.get_color_dice(dice, rowIndex)
					
				# Generate (white1+white2) action
				action_W1W2 = (rowIndex, dice["white1"]+dice["white2"]-2)
				
				if self.is_valid_action(playerIndex, action_W1W2):
					result.append((action_W1W2, None))
				
			else:
				# Take no action
				action = None
				
				result.append((action, None))
			
		return result
		
		
		
	def get_available_actions(self, dice, playerIndex): 
		"""
		list(5) of arrays of 2- tuples of actions available for a given diceThrow for a given player
		"""
		
		if playerIndex == self.playerTurn:
			return self.get_available_actions_own_turn(dice, playerIndex)
		else:
			return self.get_available_actions_opponent_turn(dice, playerIndex)
		
		
		
		
	def __init__(self, randomPlayerStart=False):

		self.__version__ = "0.1.0"
		#print("init: QwixxEnv - Version {}".format(self.__version__))
		
		self.numberPlayers = 2
		#self.playerTurn = 0  # Hardcoded player 1 starts for debugging
		
		self.randomPlayerStart = randomPlayerStart
		if randomPlayerStart==True:
			self.playerTurn = randint(0, self.numberPlayers-1)  
		else:
			self.playerTurn = 0
		
		
		#print("Starting with player=" + str(self.playerTurn))
		
		self.turnNumber = 0
		self.rowsClosed = [-1] * 4
		
		
	def set_state(self, state):
		self.currentState = state
		
	def get_state(self):
		return self.currentState
	
	def set_player_turn(self, playerTurn):
		self.playerTurn = playerTurn
		
	def set_number_players(self, numberPlayers):
		self.numberPlayers = numberPlayers
	
	def set_turn_number(self, turnNumber):
		self.turnNumber = turnNumber
		
	def set_rows_closed(self, rowsClosed):
		self.rowsClosed = rowsClosed
	
	def clone(self):
		clone = QwixxEnv(self.randomPlayerStart)
		clone.set_number_players(self.numberPlayers)
		clone.set_player_turn(self.playerTurn)
		clone.set_state(copy.deepcopy(self.get_state()))
		clone.set_turn_number(self.turnNumber)
		clone.set_rows_closed(copy.deepcopy(self.rowsClosed))
		return clone
	
	def _get_initial_state(self): 
		""" 
		Get the initial observation 
		Initial state is 11 boxes * 4 colors + 4 fehlwürfe = 48 booleans (are they marked?)
		"""
		#print("Generating state for " + str(self.numberPlayers) + " players.")
		#initialState = np.zeros(self.numberPlayers * (11*4+4))
		
		# 4 rows, 1 for each color
		initialState = [ [np.zeros(11) for i in range(4)] for playerIndex in range(self.numberPlayers) ]
		# append fehlwürfe
		for playerIndex in range(self.numberPlayers):
			initialState[playerIndex].append(np.zeros(4))
		
		return initialState
		
	
	def _can_close_row(self, playerIndex, rowIndex):
		"""
		rowIndex=0: red
		rowIndex=1: yellow
		rowIndex=2: green
		rowIndex=3: blue
		rowIndex=4: fehlwurf
		
		Row can be closed if the player marked the last spot in a line and has at least 5 fields marked
		"""
		
		if rowIndex == 4:
			return False
		
		if sum(self.currentState[playerIndex][rowIndex]) >= 5 and self.currentState[playerIndex][rowIndex][10] == 1:
			return True
				
		return False
		
	def _is_row_closed(self, rowIndex, turnNumber=None):
		"""
		Is a given row closed?
		If a turnNumber is given: if the row was closed during the current turn, the other person can still use that row
		"""
		if rowIndex == 4:
			return False
		
		if turnNumber == None:
			return self.rowsClosed[rowIndex] >= 0
		else: 
			return self.rowsClosed[rowIndex] >= 0 and self.rowsClosed[rowIndex] < turnNumber
		
		
	def is_game_over(self):
		""" 
		Check whether 2 rows are closed or 4 fehlwürfe are done for any player
		"""
		numRowsClosed = 0
		for rowIndex in range(4):
			if self._is_row_closed(rowIndex) == True:
				numRowsClosed += 1
		#print(numRowsClosed)
		
		if numRowsClosed >= 2:
			return True
			
		for playerIndex in range(self.numberPlayers):
			if sum(self.currentState[playerIndex][4]) == 4:
				return True
			
		return False	
	
	def apply_action_tuple(self, playerIndex, actionTuple):
	
		if actionTuple == None:
			raise Exception("Player" + str(playerIndex) + " cannot execute a None tuple!")
	
		if actionTuple[0] == None and actionTuple[1] == None and self.playerTurn == playerIndex:
			raise Exception("Player" + str(playerIndex) + " may not perform 2 None actions while it is his turn!")
	
		if actionTuple[0] != None and actionTuple[1] != None and self.playerTurn != playerIndex:
			raise Exception("Player" + str(playerIndex) + " may not perform 2 actions while it is not his turn!")
	
		if actionTuple[0] == actionTuple[1] and actionTuple[0] != None:
			raise Exception("Player" + str(playerIndex) + " attempting to perform same action twice: " + str(actionTuple))
	
		self._apply_action(playerIndex, actionTuple[0])
		self._apply_action(playerIndex, actionTuple[1])
		
		
	def _apply_action(self, playerIndex, action):
		
		if action == None:
			return
		
		if self.is_valid_action(playerIndex, action) == False:
			display(self.currentState)
			raise Exception("player" + str(playerIndex) + " cannot perform chosen action: " + str(action))
		
		rowIndex = action[0]
		columnIndex = action[1]
		
		self.currentState[playerIndex][rowIndex][columnIndex] = 1
		
		if columnIndex == 10:
			self.rowsClosed[rowIndex] = self.turnNumber
		
		
	def next_round(self):
	
		if self.is_game_over():
			raise Exception("Game is already over, cannot apply next round!")
	
		self.playerTurn += 1
		if self.playerTurn == self.numberPlayers:
			self.playerTurn = 0
	
		self.turnNumber += 1
	
	
	
	
	#def step(self, action):
		"""
        The agent takes a step in the environment.
        Parameters
        ----------
        action : int
        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """
	
		# Apply action to state
		# Action is a 2-tuple:
		# Each element is a 2-tuple:
		# ((rowIndex, columnIndex), (rowIndex, columnIndex))
		
		
		
	
		# Check whether game is over
		#episode_over = False
		#for playerIndex in range(self.numberPlayers): 
			#print("asd")
			
		
		# Player turn
		
		
		#return (self.currentState, reward, episode_over, {})
		
	def reset(self):
		"""
		Reset the state of the environment and returns an initial observation.
		Returns
		-------
		observation (object): the initial observation of the space.
		"""
		self.currentState = self._get_initial_state()
		return self.currentState
		
		
	def _get_points_color_row(self, currentIndex, totalIndex, currentTotal):
		if totalIndex == 0:
			return 0
	
		if currentIndex == totalIndex:
			return currentTotal
		
		currentIndex += 1
		currentTotal += currentIndex
		
		return self._get_points_color_row(currentIndex, totalIndex, currentTotal)
		
		
	def _get_points_row(self, playerIndex, rowIndex):
		"""
		Color rows are 1, 3, 6, 10, 15, 21, 28 etc
		Fehlwürfe are -5 points for each marked field
		"""
		if rowIndex < 4:
			numFieldsMarked = sum(self.currentState[playerIndex][rowIndex])
			
			# Check row closed mark bonus
			if numFieldsMarked >= 5 and self.currentState[playerIndex][rowIndex][10] == 1:
				numFieldsMarked += 1
			
			return self._get_points_color_row(1, numFieldsMarked, 1)
		else:
			# Fehlwürfe
			return -5 * sum(self.currentState[playerIndex][4])
			
		
		
	def get_points(self, playerIndex):
		result = 0
		
		for rowIndex in range(5):
			result += self._get_points_row(playerIndex, rowIndex)
		
		return result
		
		
		
		
		
		
		
		
		
		
	
		