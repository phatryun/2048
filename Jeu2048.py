#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
import numpy as np
import random

class Game2048:
	ACTION_Noth = 0
	ACTION_Right = 1
	ACTION_South = 2
	ACTION_West = 3

	ACTIONS = [ACTION_Noth, ACTION_Right, ACTION_South, ACTION_West]

	ACTION_NAMES = ["N", "E", "S", "W"]

	num_actions = len(ACTIONS)
	def __init__(self, alea=True):
		"""initalisation of the board """
		self.board = np.zeros((4, 4)).astype(int)
		self.score = 0
	
		if alea :
			self.initGame()

	def initGame(self):
		"""Random add of new tile"""
		self.AddRandomTile(0)
		self.AddRandomTile(0)
		

	def plotTile(self, nb):
		"""Transform value of a tile to optimise printing """
		res = " "
		size = len(str(nb))
		if size == 1:
			res += "   "+str(nb)+" "
		elif size == 2:
			res += "  "+str(nb)+" "
		elif size == 3:
			res += " "+str(nb)+" "
		elif size == 4:
			res += str(nb)+" "

		return res

	def plotBoard(self):
		"""Return a string with printed board"""
		res = "\n*******************\n"
		res += "score : " + str(self.score) + " \n"
		
		res += " |\n".join([" | ".join([self.plotTile(e) for e in line]) for line in self.board])
		res += " |\n"

		res += "\n*******************\n"
		return res

	def getPositionTileAvaible(self):
		"""give a list of empty tile"""
		list_res = []
		for i in range(0,4):
			for j in range(0,4):
				if self.board[i][j] == 0:
					list_res.append([i,j])

		return list_res
	
	def AddRandomTile(self, mode):
		"""add a tile in a random position"""
		if mode == 0 :
			val = 2
		else :
			val = random.choice([2,2,2,2,2,2,2,2,2,4])
		
		position = random.choice(self.getPositionTileAvaible())

		self.board[position[0]][position[1]] = val

	def compressList(self, list_values):
		"""Fonction that compress a list_values at left """
		bool_not_compress = [True, True, True, True]
		i = 1
		while i < 4:
			if i != 0 and list_values[i] != 0:
				if list_values[i-1] == 0:
					list_values[i-1] = list_values[i]
					list_values[i] = 0
					i = i - 1 
				elif list_values[i-1] == list_values[i] and bool_not_compress[i-1]:
					res = list_values[i] + list_values[i-1]
					self.score += res
					list_values[i-1] = res
					list_values[i] = 0
					bool_not_compress[i-1] = False
					i += 1
				else:
					i += 1
			else:
				i += 1
		
		return list_values
	
	def invertListValues(self, list_values):
		"""Fonction qui inverse l'ordre des valeurs d'une liste donnée en paramètre"""
		return list_values[::-1]

	def preCompression(self, list_values, bool_reverse):
		"""define the order of compression """
		is_list_change = True
		list_values_temp = list_values.copy()

		if bool_reverse :
			self.invertListValues(self.compressList(self.invertListValues(list_values)))
		else :
			self.compressList(list_values)

		#look if list_values change ==> No change equal not possible to play this move
		for elt in (list_values_temp==list_values) :
			is_list_change *= elt
			
		return is_list_change, list_values

	def getActionPossible(self, action):
		""" find action possible with actual board"""

		game_temp = Game2048()
		liste_action = ["N","S","E","W"]
		action_possible = []

		for a in liste_action:
			game_temp.board = np.copy(self.board)
			_, _, _, is_move_nOk = game_temp.playAction(a, check_end=False)
			if not is_move_nOk :
				action_possible.append(a)

		return action_possible

	def playAction(self, action, check_end=True):
		"""play a mouvment pass in parameters"""
		is_move_nOk = True
		old_score = self.score
		old_board = np.copy(self.board)
		
		if action == "W" :
			for i in range(0,4):
				is_list_change, self.board[i] = self.preCompression(self.board[i], False)
				is_move_nOk *= is_list_change
		elif action == "E":
			for i in range(0,4):
				is_list_change, self.board[i] = self.preCompression(self.board[i], True)
				is_move_nOk *= is_list_change
		elif action == "N":
			for i in range(0,4):
				is_list_change, self.board[:,i] = self.preCompression(self.board[:,i], False) 
				is_move_nOk *= is_list_change
		elif action == "S":
			for i in range(0,4):
				is_list_change, self.board[:,i] = self.preCompression(self.board[:,i], True)
				is_move_nOk *= is_list_change
		else:
			print("Coup inconu")

		is_game_over = False
		if check_end :
			# the game is over if none action are possible
			is_game_over = len(self.getActionPossible(action)) == 0
	
		if is_move_nOk :
			reward = -2
		else :
			reward = self.score - old_score
			#reward = np.sum(self.board == 0) - np.sum(old_board == 0)
			#reward = self.score
		
		return self.board, reward, is_game_over, is_move_nOk



	def play(self):
		"""Main de notre jeu"""
		print("\n\Welcome in this wonderfull 2048 game ! ")
		
		is_game_over = False

		print(self.plotBoard())
		input_key = input("play a move : N/S/E/W (q for exit the game): ")
		
		while input_key.lower() != 'q' and not is_game_over :
			board, reward, is_game_over, is_move_nOk = self.playAction(input_key.upper())
			if is_move_nOk :
				print("impossible to do this mouvement")
			else:
				self.AddRandomTile(1)

			print(self.plotBoard())
			print("is_game_over : ", is_game_over)
			print("reward : ", reward)
			if not is_game_over :
				input_key = input("play a move : N/S/E/W (q for exit the game): ")
		
		print("See you soon !")


	def val(self,x,y):
		return self.tab[x][y]

	def copy(self):
		new_game = Game2048()
		new_game.board = np.copy(self.board)
		new_game.score = self.score

		return new_game

#g = Game2048()
#g.play()

