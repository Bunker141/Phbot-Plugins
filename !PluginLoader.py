from phBot import *
import QtBind
import os
import json

name = "PluginLoader"
version = 1.1

LoadPlugins = []

startupdata = get_startup_data()
savename = startupdata["server"] + "_" + startupdata["character"]

gui = QtBind.init(__name__,name)
QtBind.createLabel(gui,'Avaliable Plugins',50,11)
AvaliablePlugins = QtBind.createList(gui,10,30,200,200)

QtBind.createButton(gui, 'btnAdd', 'Add Plugin', 218, 100)
QtBind.createButton(gui, 'btnRemove', 'Remove Plugin', 215, 140)

QtBind.createLabel(gui,'Plugins to Load',350,11)
PluginsToLoad = QtBind.createList(gui,300,30,200,200)

EndPlugin = """from phBot import *
import os

def RenameAllPlugins():
	directory = os.getcwd() + "\Plugins"
	files = os.listdir(directory)
	for slot, file in enumerate(files):
		if file.endswith("314"):
			newname = file.rstrip("314")
			os.rename(f"{directory}\{file}", f"{directory}\{newname}")

RenameAllPlugins()

"""
def CheckForEndPlugin():
	directory = os.getcwd() + "\Plugins/"
	if not os.path.exists(directory + "_PluginLoader.py"):
		with open(directory + "_PluginLoader.py","w") as f:
			f.write(EndPlugin)

CheckForEndPlugin()

def GetAllPlugins():
	directory = os.getcwd() + "\Plugins"
	files = os.listdir(directory)
	for slot, file in enumerate(files):
		if file.endswith(".py") and "PluginLoader" not in file:
			QtBind.append(gui,AvaliablePlugins,file)

GetAllPlugins()

def btnAdd():
	SelectedPlugin = QtBind.text(gui, AvaliablePlugins)
	if not SelectedPlugin:
		log('Plugin: Please Select a Plugin')
		return
	if not PluginExisit(SelectedPlugin):
		QtBind.append(gui,PluginsToLoad,SelectedPlugin)
	SaveData()

def btnRemove():
	SelectedPlugin = QtBind.text(gui,PluginsToLoad)
	QtBind.remove(gui,PluginsToLoad,SelectedPlugin)
	SaveData()	
		
def PluginExisit(file):
	Plugins = QtBind.getItems(gui,PluginsToLoad)
	for Plugin in Plugins:
		if Plugin.lower() == file.lower():
			return True
	return False
	
def LoadData():
	global LoadPlugins
	data = {}
	if os.path.exists("PluginLoader.json"):
		with open("PluginLoader.json","r") as f:
			data = json.load(f)
			for char in data:
				if char == savename:
					LoadPlugins = data[savename]['PluginsToLoad']
					for plugin in LoadPlugins:
						QtBind.append(gui,PluginsToLoad,plugin)
					return
			#empty bot, can be used to load plugins by default		
			if "_" in data:
				LoadPlugins = data["_"]['PluginsToLoad']
				for plugin in LoadPlugins:
					QtBind.append(gui,PluginsToLoad,plugin)
LoadData()

def SaveData():
	data = {}
	if os.path.exists("PluginLoader.json"):
		with open("PluginLoader.json","r") as f:
			data = json.load(f)
	else:
		data = {}
	data[savename] = {"PluginsToLoad": QtBind.getItems(gui,PluginsToLoad)}
	with open("PluginLoader.json","w") as f:
		f.write(json.dumps(data, indent=4))
	

def RenamePlugins():
	directory = os.getcwd() + "\Plugins"
	files = os.listdir(directory)
	for slot, file in enumerate(files):
		if file.endswith(".py"):
			if file not in LoadPlugins and "PluginLoader" not in file:
				os.rename(f"{directory}\{file}", f"{directory}\{file}314")

RenamePlugins()

log('Plugin: [%s] Version %s Loaded' % (name,version))
