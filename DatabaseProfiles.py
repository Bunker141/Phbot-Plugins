from phBot import *
import QtBind
import os
import shutil
import urllib.request

name = "DatabaseProfiles"
version = 1.0
NewestVersion = 0

CurrentProfile = ""
Online = False

gui = QtBind.init(__name__,name)
QtBind.createButton(gui, 'btnCreate', 'Create db3 for this Profile', 20, 20)


def LoadNewDB(profile):
	CurrentDB = get_config_dir() + "/" + GetFilename() + ".db3"
	NewDB = get_config_dir() + "/" + GetFilename() + "." + profile + ".db3"
	if not os.path.exists(NewDB):
		log(f"Plugin: No Database Exists for [{profile}]")
		DefaultDB = get_config_dir() + "/" + GetFilename() + ".default.db3"
		if os.path.exists(DefaultDB):
			shutil.copyfile(DefaultDB,CurrentDB)
			log(f"Plugin: Loading Default Database")
		return
	shutil.copyfile(NewDB,CurrentDB)
	log(f"Plugin: Loading new Database [{profile}]")

		
def SaveCurrentDB(profile):
	CurrentDB = get_config_dir() + "/" + GetFilename() + ".db3"
	NewDB = get_config_dir() + "/" + GetFilename() + "." + profile + ".db3"
	if os.path.exists(NewDB):
		shutil.copyfile(CurrentDB,NewDB)
	
def GetFilename():
	serverdata = get_character_data()
	return serverdata['server'] + "_" + serverdata['name']
	
def CheckForDBProfile(profile):
	directory = get_config_dir()
	files = os.listdir(directory)
	filename = GetFilename() + "." + profile
	for file in files:
		if file.startswith(filename) and file.endswith("db3"):
			return True
	return False

def btnCreate():
	log(str(Online))
	if not Online:
		log(f"Plugin: You Must be In Game to Make a New Database!")
		return
	if not CheckForDBProfile("default"):
		DefaultDB = get_config_dir() + GetFilename() + ".db3"
		NewDB = get_config_dir() + GetFilename() + ".default.db3"
		shutil.copyfile(DefaultDB,NewDB)
	profile = get_profile()
	if CheckForDBProfile(profile):
		log(f"Plugin: Database for Profile [{profile}] Already Exisit!")
		return
	DefaultDB = get_config_dir() + GetFilename() + ".default.db3"
	NewDB = get_config_dir() + GetFilename() + "." + profile + ".db3"
	shutil.copyfile(DefaultDB,NewDB)
	log(f"Plugin: Creating New Database for Profile [{profile}]")
	LoadNewDB(profile)

def CheckOnline():
	global Online
	if get_character_data()["name"]:
		Online = True

def joined_game():
	global Online
	Online = True
	
def event_loop():
	global CurrentProfile
	if not Online:
		return
	profile = get_profile()
	if profile == None:
		return
	if profile == "":
		profile = "default"
	if profile != CurrentProfile:
		SaveCurrentDB(CurrentProfile)
		CurrentProfile = profile
		LoadNewDB(CurrentProfile)

def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/DatabaseProfiles.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8")).split()
				for num, line in enumerate(lines):
					if line == 'version':
						NewestVersion = int(lines[num+2].replace(".",""))
						CurrentVersion = int(str(version).replace(".",""))
						if NewestVersion > CurrentVersion:
							log('Plugin: There is an update avaliable for [%s]!' % name)
							lblUpdate = QtBind.createLabel(gui,'There is an Update Avaliable, Press Here to Update',150,283)
							button1 = QtBind.createButton(gui, 'button_update', ' Update Plugin ', 400, 280)
		except:
			pass

def button_update():
	path = get_config_dir()[:-7]
	if os.path.exists(path + "Plugins/" + "DatabaseProfiles.py"):
		try:
			os.rename(path + "Plugins/" + "DatabaseProfiles.py", path + "Plugins/" + "DatabaseProfilesBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/DatabaseProfiles.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(path + "Plugins/" + "DatabaseProfiles.py", "w+") as f:
					f.write(lines)
					os.remove(path + "Plugins/" + "DatabaseProfilesBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckOnline()
CheckForUpdate()
log('Plugin: [%s] Version %s Loaded' % (name,version))
