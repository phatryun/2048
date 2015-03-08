#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

from Jeu2048 import *
#from Arbre import *
import time

class Utile:
	"""
	Fonction utile pour notre IA
	"""

	def maxListeRacine(self, liste):
		max = 0
		parcour = ""
		for elt in liste:
			if elt[1] > max:
				max = elt[1]
				parcour = elt[0]

		return parcour

	def calculeScoreH(self, grilleTemp, heur,coup):
		score = -1
		if heur == 1:
			score = self.calculScoreNaif(grilleTemp)
		elif heur == 2:
			score = self.calculGradient(grilleTemp.tab,coup)
		elif heur == 3:
			score = self.calculeScorePosition(grilleTemp.tab)
		elif heur == 4:
			score = self.calculScoreH2_1(grilleTemp)


		return score

	def calculScoreNaif(self, grilleTemp):
		"""if grilleTemp.score == 0:
			print grilleTemp.AfficherGrille"""
		return grilleTemp.score


	"""Position des valeurs des cases"""
	def calculeScorePosition(self, tab,r=0.25):
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

	""" Gradient"""
	def calculGradient(self,tab,coup):
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

	def calculSmoothness(self, grilleTemp):
		score_smooth = 0
		i = 0
		val_max = 0
		for x in range(0,4):
			for y in range(0,4):
				s = 1000000
				val_max = max(val_max, grilleTemp.val(x,y))
				if grilleTemp.val(x,y) > 0:
					i += 1
					if x > 0: 
						s = min(s, abs(grilleTemp.val(x,y) - grilleTemp.val(x-1,y)))
	                if y > 0:
	                	s = min(s, abs(grilleTemp.val(x,y) - grilleTemp.val(x,y-1)))
	                if x < 3:
	                	s = min(s, abs(grilleTemp.val(x,y) - grilleTemp.val(x+1,y)))
	                if y < 3:
	                	s = min(s, abs(grilleTemp.val(x,y) - grilleTemp.val(x,y+1)))
	                score_smooth -= s

		return score_smooth/val_max

	
	def calculScoreH2_1(self, grilleTemp):
		res = 0
		#First calcul the monotonity (H2)
		res += self.calculeScorePosition(grilleTemp.tab)
		
		#res += self.calculGradient(grilleTemp.tab)
		#res += self.eval_monotone(grilleTemp)

		#Then the smoothness
		#res += self.calculSmoothness(grilleTemp)
		
		#finaly free title
		nbFreeTitle = len(grilleTemp.positionsAvaibleNewTitle())
		res += nbFreeTitle/16
		#res += -(16-nbFreeTitle)**2

		return res

	



class IA:
	"""
	IA de notre 2048

	"""

	def __init__(self):
		#self.arbre = Arbre()
		self.grille = Grille()
		self.utile = Utile()
		

	""" NAIF """
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
				score = self.utile.calculeScoreH(newBoard,heur,coup)
				if depth != 0:
					my_m,my_s = self.nextMoveRecur(newBoard,depth-1,depthMax,heur)
					score += my_s*pow(base,depthMax-depth+1)

				if score > bestScore:
					bestCoup = str(coup)
					bestScore = score

		return bestCoup, bestScore


	""" Expectimax """
	def player_max(self, grilleTemp, depth,heur):
		if depth == 0:
			return "A",self.utile.calculeScoreH(grilleTemp,heur)
			"""if grilleTemp.asMove():
													return "A",self.utile.calculeScoreH(grilleTemp,heur)
												else:
													return "A",0"""

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



	def coup_IA(self,depth=4,heur=2):
		
		print self.grille.AfficherGrille()
		
		meilleurCoup,score = self.nextMove(self.grille,depth,heur)
		#meilleurCoup,score = self.player_max(self.grille,depth,heur)

		print "Le meilleur coup calculer est : " + meilleurCoup + " avec un score de : "+ str(score)
		#raw_input() #permet de faire une pause
		self.grille.jouerCoup(meilleurCoup)
		
		

	def play_IA(self,essai):

		#Test"
		
		i = 1
		#while i < 1000:
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




