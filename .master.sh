#!/bin/zsh
# questo script è per eseguire il merge fra un mio branch privato e master

echo "Ricordati di aggiornare la versione delle librerie, eventualmente"
echo
echo

git status

echo "Attenzione! Non ci devono essere file modificati. Seguira un git commit automatico. Continuare? [yn]"
read c

if [[ "$c" == "y" ]]
then
	# elimina il file .gitmodules
	rm .gitmodules

	# elimina le librerie gestite da submodules
	rm -r src/lib/fbwrapper

	git commit -am "Eliminato .gitmodules e lib"
	
	# aggiunge le librerie come subtree
	git subtree add --prefix=src/lib/fbwrapper https://github.com/matteoalessiocarrara/facebook-wrapper v1.0.1 --squash

else
	echo "Annullato"
fi



