#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

from Jeu2048 import *
#from Arbre import *
import time

class Utile:
	"""
	Fonction utile pour notre IA
	"""

	def calculeScoreH(self, grilleTemp, heur):
		"""Fonction simplifaint le choix de l'heuristique"""
		score = -1
		if heur == 1:
			score = self.calculScoreNaif(grilleTemp)
		elif heur == 2:
			score = self.calculGradient(grilleTemp.tab)
		elif heur == 3:
			score = self.calculeScorePosition(grilleTemp.tab)
		elif heur == 4:
			score = self.calculScoreH2_1(grilleTemp)


		return score

	def calculScoreNaif(self, grilleTemp):
		"""Heuristique avec le score de la grille """
		return grilleTemp.score


	
	def calculeScorePosition(self, tab,r=0.25):
		"""heuristique position des valeurs des cases ==> Suite parfaite"""
		tabHeur = array([[13,12,5,4]
												,[14,11,6,3]
												,[15,10,7,2]
												,[16,9,8,1]])
		"""tabHeur = array([[16,14,6,4]
												,[17,13,7,3]
												,[18,12,8,2]
												,[19,11,9,1]])"""
		"""tabHeur = array([[31,27,11,7]
												,[23,25,13,5]
												,[25,23,15,3]
												,[37,21,17,1]])"""


		res = 0.0

		for i in range(0,4):
			for j in range(0,4):
				if tab[i][j] != "      ":
					res += int(tab[i][j])*r**int(tabHeur[i][j])

		return res

	
	def calculGradient(self,tab):
		"""Heuristique du Gradient"""
		tabHeur = list()
		tabHeur.append(array([[-3,-2,-1,0]
							,[-2,-1,0,1]
							,[-1,0,1,2]
							,[0,1,2,3]]))
		tabHeur.append(array([[0,-1,-2,-3]
							,[1,0,-1,-2]
							,[2,1,0,-1]
							,[3,2,1,0]]))
		tabHeur.append(array([[3,2,1,0]
							,[2,1,0,-1]
							,[1,0,-1,-2]
							,[0,-1,-2,-3]]))
		tabHeur.append(array([[0,1,2,3]
							,[-1,0,1,2]
							,[-2,-1,0,1]
							,[-3,-2,-1,0]]))
		Grad_max = 0
		for tab_grad in tabHeur:
			res = 0.0
			for i in range(0,4):
				for j in range(0,4):
					if tab[i][j] != "      ":
						res += int(tab[i][j])*int(tab_grad[i][j])

			Grad_max = max(Grad_max, res)

		return Grad_max

	

	
	def calculScoreH2_1(self, grilleTemp):
		"""Heuristique améliorer avec la maximisation des tuiles vide"""
		res = 0
		#First calcul the monotonity (H2)
		res += self.calculeScorePosition(grilleTemp.tab) #Position
		#res += self.calculGradient(grilleTemp.tab) #Gradient
		
		
		
		#finaly free title
		nbFreeTitle = len(grilleTemp.positionsAvaibleNewTitle())
		res += nbFreeTitle/16 #Position
		#res += -(16-nbFreeTitle)**2 #Gradient

		return res

	



class IA:
	"""
	IA de notre 2048

	"""

	def __init__(self):
		"""Initialisation de notre IA"""
		self.grille = Grille()
		self.utile = Utile()
		

	"""Algorithme NAIF """
	def nextMove(self,board,depth,heur):
		m,s = self.nextMoveRecur(board,depth,depth,heur)
		return m,s

	def nextMoveRecur(self,board,depth,depthMax,heur,base=0.9):
		bestScore = -1000000000
		bestCoup = ""
		coupPossible = ["W","N","S","E"]
		newBoard = Grille()

		for coup in coupPossible:
			newBoard.tab = board.tab.copy()
			CoupNOK = newBoard.jouerCoup(str(coup))
			if not(CoupNOK): #Si le coup est validé
				newBoard.ajoutAlea(1)
				score = self.utile.calculeScoreH(newBoard,heur)
				if depth != 0:
					my_m,my_s = self.nextMoveRecur(newBoard,depth-1,depthMax,heur)
					score += my_s*pow(base,depthMax-depth+1)

				if score > bestScore:
					bestCoup = str(coup)
					bestScore = score

		return bestCoup, bestScore


	"""Algorithme Expectimax """
	def player_max(self, grilleTemp, depth,heur):
		if depth == 0:
			return "A",self.utile.calculeScoreH(grilleTemp,heur)

		bestScore = -100000000
		bestCoup = "B"
		coupPossible = ["W","N","S","E"]
		newgrilleTemp = Grille()

		for coup in coupPossible:
			score = 0
			newgrilleTemp.tab = grilleTemp.tab.copy()
			CoupNOK = newgrilleTemp.jouerCoup(str(coup))
					
			if not(CoupNOK): #Si le coup est validé
				score += self.player_expect(newgrilleTemp,depth-1,heur)
				if score >= bestScore:
					bestCoup = str(coup)
					bestScore = score


		
		return bestCoup, bestScore


	def player_expect(self, grilleTemp, depth,heur):
		total_score = 0
		total_weight = 0
		probability = 0
		listPositionTitleAvaible = grilleTemp.positionsAvaibleNewTitle()
		newgrilleTemp = Grille()

		for position in listPositionTitleAvaible:
			#on ajoute un nouveau élément à la position
			newgrilleTemp.tab = grilleTemp.tab.copy()
			val = newgrilleTemp.ajoutNotAlea(position)
			coup,score = self.player_max(newgrilleTemp, depth-1,heur)
			if val == "    2 ":
				probability = 0.9
			else:
				probability = 0.1
			
			total_score += score*probability
			total_weight += probability

		return total_score/total_weight



	def coup_IA(self,depth=4,heur=4):
		"""Fonction permettant de calculer le meilleur coup de L'IA"""
		print self.grille.AfficherGrille()
		
		#meilleurCoup,score = self.nextMove(self.grille,depth,heur) #NAIF
		meilleurCoup,score = self.player_max(self.grille,depth,heur) #Expectimax

		print "Le meilleur coup calculer est : " + meilleurCoup + " avec un score de : "+ str(score)
		#raw_input() #permet de faire une pause
		self.grille.jouerCoup(meilleurCoup)
		
		

	def play_IA(self,essai):
		"""Permet de faire tourner le jeur"""
		
		
		i = 1
		t_debut = time.clock()
		while self.grille.asMove():
			print "$$$$$$$ essai :",essai+1," $$$$$$$$$$$$      coup ",i,"    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
			self.coup_IA()
			self.grille.ajoutAlea(1)
			print self.grille.AfficherGrille()
		
			i += 1

		t_fin = time.clock()
		print "Excutée en ", t_fin-t_debut, "secondes"
		tempParIter = ((t_fin - t_debut)/i)*10**3
		print "moyenne d'excution : ", tempParIter, " ms/iteration"

		if self.grille.a8192():
			print "8192 -> MEGA GROSSE VICTOIRE !! en ",i,"iterations"
			return 4,tempParIter

		elif self.grille.a4096():
			print "4096 -> GROSSE VICTOIRE !! en ",i,"iterations"
			return 3,tempParIter

		elif self.grille.a2048():
			print "2048 -> VICTOIRE !! en ",i,"iterations"
			#print self.grille.AfficherGrille()
			#raw_input()
			return 2,tempParIter
		elif self.grille.a1024():
			print "1024 assuré !! en ",i,"iterations"
			#print self.grille.AfficherGrille()
			#raw_input()
			return 1,tempParIter
		else:
			print "GAME OVER au bout de ",i,"iterations"
			#raw_input()
			return 0,tempParIter

		

	def test_IA(self,nb):
		"""Fonction de test de l'IA """
		tab_res = array([0,0,0,0,0])
		temp_moyen = 0
		i = 0
		while i < nb:
			print i," eme essai"
			self.grille = Grille()
			self.grille.initGrille()
			succes,temps_iter = self.play_IA(i)
			#raw_input()
			tab_res[succes] += 1
			temp_moyen += temps_iter
			i += 1

		print "Score max : "
		print "|0|1024|2014|4096|8192|"
		print tab_res
		print "Temps moyen par iteration : ", temp_moyen/nb



ia = IA()
ia.test_IA(25)




