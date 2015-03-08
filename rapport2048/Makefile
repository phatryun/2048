all : compil
	echo "FIN DU MAKEFILE"
compil :
	latex rapport.tex
	latex rapport.tex
	dvips rapport.dvi
	ps2pdf rapport.ps
	xpdf rapport.pdf
	
clean :
	rm -rf *~

cleanAll :
	rm -rf Incompletude.aux
	rm -rf Incompletude.log
	rm -rf Incompletude.ps
	rm -rf Incompletude.toc
	rm -rf Incompletude.dvi
	rm -rf Incompletude.pdf
	rm -rf q.log
	rm -rf *~