#!/usr/bin/env python
"""
VSCppManager
=============

This small python script is use as a command to initialize and manage a C++
project with the VScode Editor.
With this program you can :
	- Initialize a C++ project, creating a .VSCode folder, a makefile and a main.cpp source file.
	- Create source/header file
	- Rename source/header file and all of his occurences in the other files
	- Delete source/header file and all of his occurences in the other files

Author : Cuadros Nicolas

"""
import os
import glob
import re
import argparse
import json

"""
FILE TEMPLATES
"""
#VSCode launch file
vscode_launch = {
	"version": "0.2.0",
	"configurations": [
		{
			"name": "Launch ",
			"type": "cppdbg",
			"request": "launch",
			"program": "${workspaceFolder}/bin/",
			"args": [],
			"stopAtEntry": False,
			"cwd": "${workspaceFolder}",
			"environment": [],
			"externalConsole": True,
			"MIMode": "gdb",
			"setupCommands": [
				{
					"description": "Build and Launch the project",
					"text": "-enable-pretty-printing",
					"ignoreFailures": True
				}
			],
			"preLaunchTask": "build"
		}
	]
}
#VSCode tasks file
vscode_tasks ={
	"version": "2.0.0",
	"tasks": [
		{
			"label": "build",
			"type": "shell",
			"command": "make"
		},
		{
			"label": "clean",
			"type": "shell",
			"command": "make clean"
		}
	]
}
#Define the top and bottom part of a makefile
makefile_begin = """CC = g++-7
CFLAGS = -Wall -std=c++1z -g
EXEC_NAME = bin/"""

makefile_end = """OBJECTS = bin/objects/
DIR = bin bin/objects
OBJ_FILES =  $(OBJECTS)main.o

all : $(EXEC_NAME)

clean :
	rm $(EXEC_NAME) $(OBJ_FILES)


$(EXEC_NAME) : $(DIR) $(OBJ_FILES)
	$(CC) -o $(EXEC_NAME) $(OBJ_FILES)

$(OBJECTS)%.o: %.cpp
	$(CC) $(CFLAGS) -o $@ -c $<

$(DIR) :
	mkdir bin
	mkdir bin/objects"""

MAIN = """#include <iostream>
using namespace std;

int main(int argc,char* argv[])
{
	return 0;
}"""
debugFlags = "CFLAGS = -Wall -std=c++1z -g"
releaseFlags = "CFLAGS = -Wall -std=c++1z"
"""
PROGRAM
"""
def createArgParser():
	"""
	Create the arguments of the command.
	"""
	parser = argparse.ArgumentParser(description="Program used to create C++ project and manage source files.")
	parser.add_argument('name', metavar='N',nargs="?", type=str,help="Name of files/project.")
	parser.add_argument('-p','--project',action='store_true',help="Initialize a C++ project in the current directory.")
	parser.add_argument('-n','--noSource',action='store_true',help="Add only a header file.")
	parser.add_argument('-e','--erase',action='store_true',help="Erase the file and all his references in the other files")
	parser.add_argument('-r','--rename',type=str,help="Rename the file and all his references in the other files")
	parser.add_argument('-a','--all',action='store_true',help="Add all source files that are not in the makefile into it.")
	parser.add_argument('-i','--importFile',action='store_true',help="Add file to the makefile.")
	parser.add_argument('--release',action='store_true',help="Set the makefile in order to produce a release binary.")
	parser.add_argument('--debug',action='store_true',help="Set the makefile to produce a debug binary.")


	return parser
def getAllCurrentFile():
	"""
	Return a list containing all current file compiled by the makefile
	"""
	with open('./makefile',"r") as file:
		for line in file:
			if "OBJ_FILES = " in line:
				return re.findall("\\$\\(OBJECTS\\)(.*?)\\.o",line)
	pass

def importAll():
	"""
	Add all source file that are in the makefile into it.
	"""
	temp = [file.replace(".cpp","") for file in getCppFiles() if file.endswith(".cpp")]
	current =set(getAllCurrentFile())
	[addToMakefile(file) for file in temp if file not in current]
	pass

def importFile(name):
	"""
	Add a file to the makefile.
	:param name: Name of the file to add.
	"""
	if(name.endswith):
		src = getCppFiles()
		if(name+".cpp" in src):
			addToMakefile(name)
		else:
			print("Error : "+name+" is not a source file.")
	else:
		print("Error : "+name+" is not a source file.")
	pass

def setRelease():
	"""
	Change the CFLAGS variable in the makefile in order to remove the -g compiler flag.
	"""
	temp = ""
	with open('./makefile',"r") as file:
		for line in file:
			if("CFLAGS" in line):
				temp += releaseFlags+"\n"
			else:
				temp+= line
	with open('./makefile','w+') as out:
		out.write(temp)
	pass

def setDebug():
	"""
	Change the CFLAGS variable in the makefile in order to add the -g compiler flag.
	"""
	temp = ""
	with open('./makefile',"r") as file:
		for line in file:
			if("CFLAGS" in line):
				temp += debugFlags+"\n"
			else:
				temp+= line
	with open('./makefile','w+') as out:
		out.write(temp)
	pass

def buildVScode(name):
	"""
	Create a VSCode project setup (makefile, main and .VSCode folder)
	:param name: Name of the project, this name will be use for the executable name.
	:type name: str
	"""
	if not os.path.exists("./.vscode/"):
		os.makedirs("./.vscode")
	vscode_launch["configurations"][0]["program"]+=name
	with open('./.vscode/launch.json','w') as outfile:
		TempLaunch = vscode_launch
		TempLaunch["configurations"][0]["name"] += name
		json.dump(TempLaunch,outfile)
	with open('./.vscode/tasks.json','w') as outfile:
		json.dump(vscode_tasks,outfile)
	if not os.path.exists("./main.cpp"):
		with open('./main.cpp','w') as outfile:
			outfile.write(MAIN)
	with open('./makefile','w') as outfile:
		outfile.write(makefile_begin+name+"\n"+makefile_end)

	pass

def getCppFiles():
	"""
	Get all the C++ source files path of the current directory.
	"""
	out = []
	out += glob.glob("*.h")
	out += glob.glob("*.cpp")
	return out
def replaceOccurence(previous,new,file):
	"""
	Replace all string matching the regex previous to the new str in a file
	:param previous: Regex to match
	:param new: String to apply
	:param file: name of the file to inspect
	"""
	temp =""
	with open(file,"r") as f:
		for line in f:
			temp += re.sub(previous,new,line)
	with open(file,'w+') as out:
		out.write(temp)
	pass
def eraseOccurence(str,file):
	"""
	Erase all string matching the regex previous to the new str in a file
	:param previous: Regex to match
	:param file: name of the file to inspect
	"""
	replaceOccurence(str,'',file)
def addToMakefile(name):
	"""
	Add a new source file to compile in the makefile
	:param name: Name of the source file
	"""
	if os.path.exists("./"+name+".cpp"):
		gr = getAllCurrentFile()
		if(not name in gr):
			temp = ""
			with open('./makefile',"r") as file:
				for line in file:
					if("OBJ_FILES = " in line):
						temp += line.replace('\n','') + " $(OBJECTS)"+name+".o\n"
					else:
						temp+= line
			with open('./makefile','w+') as out:
				out.write(temp)
	else:
		print("Error : "+name+" does not exist or is not a source file.")
	pass

def addHeader(name):
	"""
	Create a new Header file
	:param name: Name of the file
	"""
	if not os.path.exists("./"+name+".h"):
		with open(name+".h","w+") as out:
			out.write("#pragma once\n")
	pass

def addSource(name):
	"""
	Create a new source file
	:param name: Name of the file
	"""
	if not os.path.exists("./"+name+".cpp"):
		with open(name+".cpp","w+") as out:
			out.write("#include \""+name+".h"+"\"\n")
	pass

def NoSource(name):
	"""
	Create only a header file
	:param name: Name of the file to add
	"""
	addHeader(name)
	pass

def SourceHeader(name):
	"""
	Create a couple header/source file
	:param name: Name of the couple
	"""
	addHeader(name)
	addSource(name)
	addToMakefile(name)
	pass

def suppFile(name):
	"""
	Delete header/source file and all of his reference in the other sources.
	:param name: Name of the file to delete.
	"""
	if os.path.exists("./"+name+".h"):
		os.remove("./"+name+".h")
	if os.path.exists("./"+name+".cpp"):
		os.remove("./"+name+".cpp")
	temp_o = "\\$\\(OBJECTS\\)"+"\\.o"
	eraseOccurence(temp_o,'./makefilAdd all source file that are in the makefile into it.')
	for f in getCppFiles():
		eraseOccurence("\\s*\\#\\s*include\\s*\""+name+".h\"",f)

def renameFile(name,newName):
	"""
	Rename header/source file and all of his reference in the other sources.
	:param name: Name of the file to rename.
	:param newName: new name for the file.
	"""
	if os.path.exists("./"+name+".h"):
		os.rename("./"+name+".h","./"+newName+".h")
	if os.path.exists("./"+name+".cpp"):
		os.rename("./"+name+".cpp","./"+newName+".cpp")
	temp_o = "\\$\\(OBJECTS\\)"+name+"\\.o"
	temp_oNew =  "$(OBJECTS)"+newName+".o"
	replaceOccurence(temp_o,temp_oNew,'./makefile')
	for f in getCppFiles():
		replaceOccurence("\\s*\\#\\s*include\\s*\""+name+".h\"","#include \""+newName+".h\"",f)
	pass
def testGiveAName(var):
	if(var != ""):
		return True
	else:
		print("Error : you need to give a name.")
def main():
	"""
	Main function
	"""
	parser = createArgParser()
	args = parser.parse_args()
	name = args.name
	Erase = args.erase
	noSource = args.noSource
	rename=args.rename
	project = args.project
	release = args.release
	debug =args.debug
	importA = args.all
	imp = args.importFile
	#Adding files
	if(project == False and Erase == False and rename==None and name != "" and not(name is None)):
		if(noSource == False):
			SourceHeader(name)
		else:
			NoSource(name)
	else:
		if(Erase):
			suppFile(name)
		if(not rename is None):
			if(testGiveAName(name)):
				renameFile(name,rename)
		if(project):
			if(testGiveAName(name)):
				buildVScode(name)
		if(release):
			setRelease()
		if(debug):
			setDebug()
		if(imp):
			if(testGiveAName(name)):
				addToMakefile(name)
		if(importA):
			importAll()
	pass

if __name__=='__main__':
	main()
	pass