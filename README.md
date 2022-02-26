# tlg-ply
Liste des fonctionnalitées implémantées:
- Votre interpréteur devra gérer les noms de variables à plusieurs caractères
- affectation
- affichage d’expressions numériques (pouvant contenir des variables numériques)
- instructions conditionnelles : implémenter le si-alors-sinon/si-alors
- structures itératives : implémenter le while et le for
- Affichage de l’arbre de syntaxe (sur la console ou avec graphViz)
- Gérer les fonctions avec/ sans paramètre sans valeur de retour
- Gérer le scope des variables
- Gérer la déclaration explicite des variables
- incrémentation et affectation élargie

# affectation, print  fichier1.txt
#'var x=4; x=x+3; print(x);'

# affectation élargie, affectation  fichier2.txt
#'var x=9; x-=4; print(x);'

# while, for  fichier3.txt
#’’’var x=4; while(x<30) { x=x+3; print(x); }; for(var i=0; i<4; i=i+1) { print(i*i); };’’’

# fonctions void avec paramètres et scopes des variables  fichier4.txt
#'function toto(a, b) { print(a+b) ; }; toto(3, 5);’

# preuve du scope des variables  fichier5.txt
#'function toto(a, b) { var x = 2; print(a+b+x); }; toto(3, 5); print(x);’