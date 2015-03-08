#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

import random
from scipy import *

class Grille:
	
	def __init__(self):
		self.tab = array([["      ","      ","      ","      "]
			,["      ","      ","      ","      "]
			,["      ","      ","      ","      "]
			,["      ","      ","      ","      "]])
		self.score = 0

	def initGrille(self):
		self.ajoutAlea(0)
		self.ajoutAlea(0)
		

	def AfficherGrille(self):
		res = "\n*******************\n"
		res += "score : " + str(self.score) + " \n"
		for i in range(0,4):
			for j in range(0,4):
				res = res + " | " + str(self.tab[i][j])
			res += " | \n" 

		res += "\n*******************\n"
		return res

	def ajoutNotAlea(self,position):
		val = random.choice(["    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    2 ","    4 "])
		self.tab[position[0]][position[1]] = val
		return val

	def ajoutAlea(self,mode):
		#print "yo"
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
		isMoveNOk = True
		if coup == "W":
			#print "Ouest"
			for i in range(0,4):
				isListNOk,self.tab[i] = self.preCompresser(self.tab[i], False)
				isMoveNOk *= isListNOk
		elif coup == "E":
			#print "Est"
			for i in range(0,4):
				isListNOk,self.tab[i] = self.preCompresser(self.tab[i], True)
				isMoveNOk *= isListNOk
		elif coup == "N":
			#print "Nord"
			for i in range(0,4):
				isListNOk,self.tab[:,i] = self.preCompresser(self.tab[:,i], False) 
				isMoveNOk *= isListNOk
		elif coup == "S":
			#print "Sud"
			for i in range(0,4):
				isListNOk,self.tab[:,i] = self.preCompresser(self.tab[:,i], True)
				isMoveNOk *= isListNOk
			#for i in range(0,4):
		else:
			print "Coup inconu"

		return isMoveNOk

	def InverseListe(self, liste):
		i,j = liste[0],liste[1]
		liste[0] = liste[3]
		liste[1] = liste[2]
		liste[2] = j
		liste[3] = i

		return liste

	def jouer(self):
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
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 1024 ":
					boolean = True

		return boolean

	def a2048(self):
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 2048 ":
					boolean = True

		return boolean


	def a4096(self):
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 4096 ":
					boolean = True

		return boolean

	def a8192(self):
		boolean = False
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == " 8192 ":
					boolean = True

		return boolean

	def gameOver(self):
		boolean = True
		grilleTemp = Grille()
		if self.a2048():
			return True
		else:
			return not self.asMove()


	def positionsAvaibleNewTitle(self):
		list_res = list()
		for i in range(0,4):
			for j in range(0,4):
				if self.tab[i][j] == "      ":
					list_res.append([i,j])

		return list_res

	def asMove(self):
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
print grille.AfficherGrille()
L = grille.positionsAvaibleNewTitle()
print L
print L[0]
grille.ajoutNotAlea(L[0])
print grille.AfficherGrille()"""
"""grille.jouer()"""

"""tab2 = array([["    4  ","    5  ","   12 ","   13 "]
			,["    3 ","    6 ","  11  ","   14 "]
			,["    2 ","    7 ","  10  ","   15 "]
			,["    1 ","    8 ","   9  ","   16 "]])

for m in range(0,4):
	for e in range(0,4):
		print int(tab2[m][e])*0.25**int(tab2[m][e])"""

"""grille.tab = tab2
print grille.AfficherGrille()"""
