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
			"name": "(gdb) Launch",
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
					"description": "Enable pretty-printing for gdb",
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

"""
PROGRAM
"""
def createArgParser():
	"""
	Create the arguments of the command.
	"""
	parser = argparse.ArgumentParser(description="Program used to create C++ project and manage source files.")
	parser.add_argument('name', metavar='N', type=str,help="Name of files/project.")
	parser.add_argument('-n','--noSource',action='store_true',help="Add only a header file.")
	parser.add_argument('-e','--erase',action='store_true',help="Erase the file and all his references in the other files")
	parser.add_argument('-r','--rename',type=str,help="Rename the file and all his references in the other files")
	parser.add_argument('-p','--project',action='store_true',help="Initialize a C++ project in the current directory.")


	return parser


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
		json.dump(vscode_launch,outfile)
	with open('./.vscode/tasks.json','w') as outfile:
		json.dump(vscode_tasks,outfile)
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
	temp = ""
	with open('./makefile',"r") as file:
		for line in file:
			if("OBJ_FILES = " in line):
				temp += line.replace('\n','') + " $(OBJECTS)"+name+".o\n"
			else:
				temp+= line
	with open('./makefile','w+') as out:
		out.write(temp)
	pass

def addHeader(name):
	"""
	Create a new Header file
	:param name: Name of the file
	"""
	with open(name+".h","w+") as out:
		out.write("#pragma once\n")
	pass

def addSource(name):
	"""
	Create a new source file
	:param name: Name of the file
	"""
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
	temp_o = "\\$\\(OBJECTS\\)"+name+"\\.o"
	eraseOccurence(temp_o,'./makefile')
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
	if(project == False and Erase == False and rename==None):
		if(noSource == False):
			SourceHeader(name)
		else:
			NoSource(name)
	else:
		if(Erase):
			suppFile(name)
		if(not rename is None):
			renameFile(name,rename)
		if(project):
			buildVScode(name)
	pass

if __name__=='__main__':
	main()
	pass