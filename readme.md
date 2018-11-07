# Visual Studio Code C++ Manager

## Description

This project aim to create a small bash command to create/manage C++ projects
for Visual Studio Code.

## Installation

In order to install the command for the user just clone the repository and use make.

```bash
git clone https://github.com/CuadrosNicolas/VSCppManager
cd ./VSCppManager
make install
```

## How to use

### Create a project

```bash
VSCppManager project_name -p
```

### Add files to the project

```bash
VSCppManager file_name
```

If you want to add only a header file you can use the -n parameter

```bash
VSCppManager file_name -n
```

### Rename project files

```bash
VSCppManager previous_file_name -r new_file_name
```

This command will also rename all references to this file in the others.

### Delete project files

```bash
VSCppManager file -e
```

This command will also erase all references to this file in the others.

## Author

Cuadros Nicolas