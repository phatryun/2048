#!/usr/bin/python3.4
# -*-coding:Utf-8 -*


import time
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Flatten
from keras.layers.convolutional import Conv2D
#from tensorflow.keras.layers import Conv2D, Flatten

from keras.optimizers import sgd, Adam
import os
import random
from collections import deque, Counter
from tqdm import tqdm
import pandas as pd

from Jeu2048 import *

import matplotlib.pyplot as plt

class Trainer :
	def __init__(self, name=None, learning_rate=0.01, memory_size=3000, batch_size=30, mode=None, layers_size=[64,32]) :
		self.board_size = 16
		self.action_size = 4
		self.gamma = 0.01
		self.epsilon = 1.0
		self.learning_rate = learning_rate
		self.name = name
		self.memory = deque(maxlen=memory_size)
		self.batch_size = batch_size
		self.mode = mode

		#get previous model if exist
		if name is not None and os.path.isfile("model-"+name) :
			model = load_model("model-"+name)
		else :
			if mode == "CNN" :
				INPUT_SHAPE_CNN = self.board_size#(4+4*4)*self.board_size
				model = Sequential()
				model.add(Conv2D(32, kernel_size=3, activation='relu', input_shape=(INPUT_SHAPE_CNN,4,4)))
				model.add(Conv2D(64, kernel_size=1, activation='relu'))
				model.add(Flatten())
				model.add(Dense(self.action_size, activation='linear'))
				model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
				self.name = "16_C2D-32-3[relu]_C2D-64-1[relu]_flatten_4[linear]_Adam[mse]" 
			else :
				# create it if doesn't exist yet
				model = Sequential()
				model.add(Dense(layers_size[0], input_shape=(self.board_size,), activation="relu"))
				
				for i_layer in range(1,len(layers_size)) :
					model.add(Dense(layers_size[i_layer], activation="relu"))

				model.add(Dense(self.action_size, activation="linear"))
				model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
				self.name = "16_64[relu]_32[relu]_32[relu]_4[linear]_Adam[mse]" 
		self.model = model
	
	def GetOneHotMatriceFromBoard(self, board) :

		table = {2**i:i for i in range(1,self.board_size)} # dictionary storing powers of 2: {2: 1, 4: 2, 8: 3, ..., 16384: 14, 32768: 15, 65536: 16}
		table[0] = 0

		grid_onehot = np.zeros(shape=(self.board_size, 4, 4))
		for i in range(4):
			for j in range(4):
				grid_element = board[i][j]
				grid_onehot[table[grid_element],i, j] = 1

		#print(grid_onehot.shape)
		return np.array([grid_onehot])

	def getNorm2logFromBoard(self, board) :
		board_norm = np.concatenate((board), axis=None)
		board_norm = np.where(board_norm <= 0, 1, board_norm)
		board_norm = np.log2(board_norm)/np.log2(16384)

		list_board = np.array([board_norm])
		return list_board

	def train(self, game, remember=False):

		#normalise board
		if self.mode == "CNN" :
			list_board = self.GetOneHotMatriceFromBoard(game.board)
		else:
			list_board = self.getNorm2logFromBoard(game.board)

		# train on all action
		target = self.model.predict(list_board)[0]

		# get reward of action
		for a in game.ACTION_NAMES :
			index_action = game.ACTION_NAMES.index(a)
			game_temp = game.copy()
			_, reward, is_game_over, _ = game_temp.playAction(a, check_end=False)

			target[index_action] = reward
			if not is_game_over :
				reward_max = -99
				for a_next in game.ACTION_NAMES :
					index_action_next =  game.ACTION_NAMES.index(a_next)
					game_temp_next = game_temp.copy()
					_, reward_next, is_game_over_next, _ = game_temp_next.playAction(a_next, check_end=False)
					reward_max = max(reward_max, reward_next)

				target[index_action] += self.gamma * reward_max


		#print(target)
		if remember :
			self.memory.append([list_board, target])
			return True
		else :
			inputs = list_board
			outputs = np.array([target])
			return self.model.fit(inputs, outputs, epochs=1, verbose=0, batch_size=1)


	def remember(self, game):

		# get all action reward
		dict_train_game = dict()
		for a in game.ACTION_NAMES :
			index_action = game.ACTION_NAMES.index(a)
			game_temp = game.copy()

			next_board, reward, is_game_over, is_move_nOk = game_temp.playAction(a, check_end=False)

			dict_train_game[a] = (game.board, index_action, reward, next_board, is_game_over)

		
		#normalise board
		if self.mode == "CNN" :
			list_board = self.GetOneHotMatriceFromBoard(game.board)
		else:
			list_board = self.getNorm2logFromBoard(game.board)

		# train on all action
		target = self.model.predict(list_board)[0]

		for a in game.ACTION_NAMES :
			val_action = dict_train_game[a]
			if self.mode == "CNN" :
				list_next_board = self.GetOneHotMatriceFromBoard(val_action[3])
			else:
				list_next_board = self.getNorm2logFromBoard(val_action[3])

			if val_action[4] :
				target[val_action[1]] = val_action[2]
			else :
				target[val_action[1]] = val_action[2] + self.gamma * np.max(self.model.predict(list_next_board))
		
		self.memory.append([list_board, target])
	
	def replay(self, batch_size) :
		batch_size = min(batch_size, len(self.memory))

		minibatch = random.sample(self.memory, batch_size)

		inputs = np.zeros((batch_size, self.board_size, 4, 4))
		outputs = np.zeros((batch_size, self.action_size))
		
		for i, (board, target) in enumerate(minibatch):
			inputs[i] = board
			outputs[i] = target

		return self.model.fit(inputs, outputs, epochs=1, verbose=0, batch_size=batch_size)

	def getBestAction(self, board):

		if self.mode == "CNN" :
			list_board = self.GetOneHotMatriceFromBoard(board)
		else:
			list_board = self.getNorm2logFromBoard(board)

		#predict the next action
		act_values = self.model.predict(list_board)

		# Pick the action based on the predicted reward
		action =  np.argmax(act_values[0])

		return action, act_values

	def save(self, id=None, overwrite=False) :
		name = 'model'
		if self.name:
			name += '-' + self.name
		else:
			name += '-' + str(time.time())
		if id:
			name += '-' + id

		self.model.save(name, overwrite=overwrite)

def main_RandomPlay(nb_try):
	trainer = Trainer(learning_rate=0.01)
	res = []

	for i in tqdm(range(nb_try)):	
		#lets play one party
		g = Game2048()
		is_game_over = False

		cpt = 1
		while not is_game_over : #and cpt < 10:

			a = random.choice(g.ACTION_NAMES)
			i_a = g.ACTION_NAMES.index(a)
			temp_g = g.copy()
			next_board, reward, is_game_over, is_move_nOk = g.playAction(a)
			
			trainer.remember(temp_g)
				
			if not is_move_nOk :
				g.AddRandomTile(1)

			cpt += 1

		#print("\n",np.max(g.board))
		res.append([cpt, np.max(g.board), g.score])

	df_res = pd.DataFrame(res, columns=["nb_moves", "highest_tile", "score"])
	#print(df_res)
	df_res.to_csv("./result_naif_IA.csv",index=False)
	return trainer

def main_RL(trainer, nb_test=100, max_play=1000, print_game=False, replay_len=1000):

	res = []
	cpt_total = 1
	plt.ion()

	game_saves = dict()

	df_res = pd.DataFrame(columns=["nb_moves", "highest_tile", "score"])
	for i in tqdm(range(nb_test)):	

		list_histo_game = list()
		#lets play one party
		#g = Game2048()
		g = Game2048(alea=False)
		g.board[0][0] = 2
		g.board[1][0] = 2
		is_game_over = False
		cpt = 1
		cpt_same_action = 0
		last_action = [0,0,0,0]
		while not is_game_over and cpt < max_play :

			#if cpt_total % 100 == 0 :
			#	trainer.replay(replay_len)

			i_a, actions_possible = trainer.getBestAction(g.board)
			a = g.ACTION_NAMES[i_a]
			
			g_temp = g.copy()

			next_board, reward, is_game_over, is_move_nOk = g.playAction(a)
			
			if print_game:
				print(g_temp.plotBoard())
				print("actions_possible : ", actions_possible)#, " --> ", a)
				print("action ", i_a, " : ", a, " -> ", reward)
				
			
			trainer.train(g_temp, remember=True)
			trainer.replay(replay_len)

			move_histo = dict()
			move_histo["board"] = g_temp.copy()
			move_histo["actions_possible"] = actions_possible[0]
			move_histo["action_choose"] = a
			move_histo["i_action_choose"] = i_a
			move_histo["reward"] = reward
			list_histo_game.append(move_histo)


			if not is_move_nOk :
				g.AddRandomTile(1)
				#g.board[3][3] = 2
			cpt += 1
			cpt_total += 1

		#print("\n",np.max(g.board))
		df_res.loc[len(df_res)] = [cpt, np.max(g.board), g.score]
		plt.plot(df_res.index, df_res["score"], color="b")
		plt.plot(df_res.index, df_res["highest_tile"], color="r")
		plt.plot(df_res.index, df_res["nb_moves"], color="g")

		plt.title(str(i))
		plt.legend(("score","highest_tile", "nb_moves"), loc=2)
		plt.draw()
		plt.pause(0.1)

		game_saves[i] = list_histo_game
	#df_res = pd.DataFrame(res, columns=["nb_moves", "highest_tile", "score"])
	#print(df_res)
	df_res.to_csv("./result_RL_IA_" + trainer.name + "_norm.csv",index=False)
	plt.savefig("./result_RL_IA_" + trainer.name + "_norm.png")
	#plt.show(block=True)

	return game_saves



#t = main_RandomPlay(100)
#t.replay(1000)

#
#g = Game2048()
#print(t.GetOneHotMatriceFromBoard(g.board).shape)
#[173.6525   37.80621 175.47876  56.88058]

#### Regarder si le DNN arrive bien a trainer le meme board

t = Trainer(learning_rate=0.01, memory_size=3000, mode="CNN")
gsaves = main_RL(t, nb_test=5000, max_play=3000, print_game=False, replay_len=1000)

print("memory_size : ", len(t.memory))

print("score Alea")
df_alea = pd.read_csv("./result_naif_IA.csv")
df_alea_tile = df_alea.groupby(["highest_tile"], as_index=False).agg({"score":"count", "nb_moves":("sum", "mean")})
print(df_alea_tile)

print("score RL")
df_RL = pd.read_csv("./result_RL_IA_" + t.name + "_norm.csv")
df_RL_tile = df_RL.groupby(["highest_tile"], as_index=False).agg({"score":"count", "nb_moves":("sum", "mean")})
print(df_RL_tile)


# testing iter by iter
"""a = np.zeros((4,4)).astype(int)

print(np.sum(a == 0))

a[1][0] = 2
print(a)
print(np.sum(a == 0))"""

# regarder l'évolution du predict quand c'est sur 1e action vs les 4
# Au train, apprendre sur les 4 outputs

"""
g = Game2048(alea=False)
g.board[0][0] = 2
g.board[1][0] = 2

print(g.plotBoard())

t = Trainer(learning_rate=0.01)

dict_train = dict()
for a in g.ACTION_NAMES :
	print(a)
	index_action = g.ACTION_NAMES.index(a)
	g_temp = g.copy()

	next_board, reward, is_game_over, is_move_nOk = g_temp.playAction(a)

	print("a : ",a, " --> ", reward)
	dict_train[a] = (g.board, index_action, reward, next_board, is_game_over)

print("learning")
print(g.plotBoard())

list_board = t.getNorm2logFromBoard(g.board)

target = t.model.predict(list_board)[0]
target_tmp = np.copy(target)
print("target                : ", ["%.04f" % e for e in target], " --> ", np.argmax(target))
for a in g.ACTION_NAMES :
	val_action = dict_train[a]
	list_next_board = t.getNorm2logFromBoard(val_action[3])
	target[val_action[1]] = val_action[2] + t.gamma * np.max(t.model.predict(list_next_board))


print("target corrigee       : ", ["%.04f" % e for e in target], " --> ", np.argmax(target))

inputs = list_board
outputs = np.array([target])

t.model.fit(inputs, outputs, epochs=1, verbose=0, batch_size=1)
target = t.model.predict(list_board)[0]
print("target_after          : ", ["%.04f" % e for e in target], " --> ", np.argmax(target))
print("target_after - target : ", ["%.04f" % e for e in  target-target_tmp])

for i in range(0,4) :
	print(i, " : ", "%0.4f" % target[i], " - ", "%0.4f" % target_tmp[i], " = ", "%0.4f" %  (target[i]-target_tmp[i]))

print(np.sum(np.abs(target_tmp - target)))
"""

"""

#t.train(board_tmp, i_a, reward, next_board, is_game_over)"""

#target - target_after :  [-1.3199449e-04  5.1538646e-04  1.1593314e+00  3.8544089e-04]

"""
0  :  -0.1450  -  -0.1466  =  0.0016
1  :  0.0812  -  0.0827  =  -0.0015
2  :  -0.0421  -  -0.0500  =  0.0079
3  :  0.1550  -  0.1658  =  -0.0108
"""