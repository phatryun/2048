#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

import random
from scipy import *

class Grille:
	
	def __init__(self):
		"""fonction d'initialisation de la grille """
		self.tab = array([["      ","      ","      ","      "]
			,["      ","      ","      ","      "]
			,["      ","      ","      ","      "]
			,["      ","      ","      ","      "]])
		self.score = 0

	def initGrille(self):
		"""Permet l'ajout aléatoire des deux premieres tuiles"""
		self.ajoutAlea(0)
		self.ajoutAlea(0)
		

	def AfficherGrille(self):
		"""Fonction qui permet l'affichage de la grille"""
		res = "\n*******************\n"
		res += "score : " + str(self.score) + " \n"
		for i in range(0,4):
			for j in range(0,4):
				res = res + " | " + str(self.tab[i][j])
			res += " | \n" 

		res += "\n*******************\n"
		return res

	def ajoutNotAlea(self,position):
		"""Ajoute une nouvelle tuile en fonction des position donnée"""
		val = random.choice(["    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    4 "])
		self.tab[position[0]][position[1]] = val
		return val

	def ajoutAlea(self,mode):
		"""Ajoute aléatoirement une nouvelle tuile"""
		boolean = True
		if mode == 0:
			val = "    2 "
		else:# 10% -> 4 et 90% -> 2
			val = random.choice(["    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    4 "])

		while boolean:
			#print "oh shit"
			i = random.randint(0,4)
			j = random.randint(0,4)
			if self.tab[i][j] == "      ":
				self.tab[i][j] = val
				boolean = False
			

	def format(self, nb):
		"""Permet de transformer la valeur obtenue en chaine de caractère optimisé pour l'affichage"""
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


	def compresserList(self, liste):
		"""Fonction qui gère la compression d'une liste """
		boolPasCompre = True
		i = 0
		while i < 4:
			
			if liste[i] == "      ":
				i += 1
			else:
				if i != 0 :
					if liste[i-1] == "      ":
						liste[i-1] = liste[i]
						liste[i] = "      "
						i = i - 1 
					elif liste[i-1] == liste[i] and boolPasCompre:
						res = int(liste[i]) + int(liste[i-1])
						self.score += res
						liste[i-1] = self.format(res)
						liste[i] = "      "
						i += 1
						boolPasCompre = False
						
					else:
						i += 1
				else:
					i += 1
		return liste
	

	def preCompresser(self,liste,boolReverse):
		"""Permet de définir le sens de compression """
		isListeNOk = True
		listTemp = liste.copy()
		
		if boolReverse :
			self.InverseListe(self.compresserList(self.InverseListe(liste)))
		else :
			self.compresserList(liste)

		for elt in (listTemp==liste) :
			isListeNOk *= elt
			

		return isListeNOk,liste

	def jouerCoup(self, coup):
		"""Fonction qui permet de lancer la compression en fonction du coup donnée"""
		isMoveNOk = True
		if coup == "W":
			for i in range(0,4):
				isListNOk,self.tab[i] = self.preCompresser(self.tab[i], False)
				isMoveNOk *= isListNOk
		elif coup == "E":
			for i in range(0,4):
				isListNOk,self.tab[i] = self.preCompresser(self.tab[i], True)
				isMoveNOk *= isListNOk
		elif coup == "N":
			for i in range(0,4):
				isListNOk,self.tab[:,i] = self.preCompresser(self.tab[:,i], False) 
				isMoveNOk *= isListNOk
		elif coup == "S":
			for i in range(0,4):
				isListNOk,self.tab[:,i] = self.preCompresser(self.tab[:,i], True)
				isMoveNOk *= isListNOk
		else:
			print "Coup inconu"

		return isMoveNOk

	def InverseListe(self, liste):
		"""Fonction qui inverse l'ordre des valeurs d'une liste donnée en paramètre"""
		i,j = liste[0],liste[1]
		liste[0] = liste[3]
		liste[1] = liste[2]
		liste[2] = j
		liste[3] = i

		return liste

	def jouer(self):
		"""Main de notre jeu"""
		print "\n\nBonjour et bienvenue dans ce merveilleux programme du 2048 ! "
		self.initGrille()
		print self.AfficherGrille()
		saisi = raw_input("Jouer un coup N/S/E/W (q pour quitter): ")
		while saisi.lower() != 'q' and not self.a2048():
			CoupNOK = self.jouerCoup(saisi.upper())
			if CoupNOK:
				print "Coup Impossible!!!"
			else:
				self.ajoutAlea(1)
			print self.AfficherGrille()
			saisi = raw_input("Jouer un coup N/S/E/W (q pour quitter): ")
			print "saisi : " + saisi
		print "Au revoir"

	def a1024(self):
		"""Fonction permettant de savoir si la grille à un tuile 1024"""
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 1024 ":
					boolean = True

		return boolean

	def a2048(self):
		"""Fonction permettant de savoir si la grille à un tuile 2048"""
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 2048 ":
					boolean = True

		return boolean


	def a4096(self):
		"""Fonction permettant de savoir si la grille à un tuile 4096"""
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 4096 ":
					boolean = True

		return boolean

	def a8192(self):
		"""Fonction permettant de savoir si la grille à un tuile 8192"""
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 8192 ":
					boolean = True

		return boolean

	def gameOver(self):
		"""Fonction qui permet de savoir si le jeu est terminé : le joueur ne peux plus jouer de coup"""
		boolean = True
		grilleTemp = Grille()
		if self.a2048():
			return True
		else:
			return not self.asMove()


	def positionsAvaibleNewTitle(self):
		"""Permet de donner la liste des case vide de la grille"""
		list_res = list()
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == "      ":
					list_res.append([i,j])

		return list_res

	def asMove(self):
		"""Permet de donner les coup autorisaer """
		boolean = True
		grilleTemp = Grille()
		listeCoup = ["N","S","E","W"]
		for coup in listeCoup:
			grilleTemp.tab = self.tab.copy()
			boolean *= grilleTemp.jouerCoup(coup)
		return not boolean

	def val(self,x,y):
		if self.tab[x][y] =="      ":
			return 0
		else:
			return int(self.tab[x][y])

"""grille = Grille()
grille.initGrille()
grille.jouer()"""

