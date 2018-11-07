install :
	cp VSCppManager.py VSCppManager
	chmod +x VSCppManager
	mv ./VSCppManager ~/.local/bin/VSCppManager

uninstall :
	rm ~/.local/bin/VSCppManager