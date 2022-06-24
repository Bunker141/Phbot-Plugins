from phBot import *
from datetime import datetime
from threading import Timer
import shutil
import QtBind
import json
import urllib.request
import os

name = 'BackupRestorer'
version = 1.0
NewestVersion = 0
path = get_config_dir() + 'Backup'

gui = QtBind.init(__name__, name)

Configs = {"Profiles": []}
Loaded = False

lstProfiles = QtBind.createList(gui,10,50,150,200)
lblProfiles = QtBind.createLabel(gui,'Char Profiles (json)',40,23)

ProfileDates = QtBind.createList(gui,180,50,200,200)
lblProfileDates = QtBind.createLabel(gui,'Avaliable Backup Dates',220,23)
btnRestore = QtBind.createButton(gui, 'button_restore', ' Restore ', 240, 260)

lblChar = QtBind.createLabel(gui,'Char Name',400,50)
txtChar = QtBind.createLineEdit(gui,"DeRidder",470,48,120,20)
lblServer = QtBind.createLabel(gui,'Server Name',400,80)
txtServer = QtBind.createLineEdit(gui,"Theia",470,78,120,20)
btnLoadProfiles = QtBind.createButton(gui, 'button_load', ' Load Profiles ', 470, 120)

def button_load():
	global Loaded, Configs
	Configs = {"Profiles": []}
	QtBind.clear(gui,lstProfiles)
	Server = QtBind.text(gui, txtServer)
	Char = QtBind.text(gui, txtChar)
	if not Server or not Char:
		log('Plugin: Please enter a Server and Char Name to Search')
		return
	AllConfigs = os.listdir(path)
	for Config in AllConfigs:
		if Config.endswith('.json'):
			Config = Config[:-5]
			server = Config[:len(Server)]
			if Server == server:
				char = Config[len(Server)+1:len(Server + Char)+1]
				if Char == char:
					if '.' in Config:
						profile = Config[len(Server + Char)+2:].split('_')[0]
						if len(profile) > 0:
							date = Config[len(Server + Char)+2:].split('_')[1]
							if CheckIfProfileExist(profile):
								AddDate(profile,date)
							else:
								data = {'Profile': profile, 'Backups': [date]}
								Configs['Profiles'].append(data)
					else:
						profile = 'Default'	
						date = Config[len(Server + Char)+2:].split('_')[0]
						if CheckIfProfileExist(profile):
							AddDate(profile,date)
						else:
							data = {'Profile': profile, 'Backups': [date]}
							Configs['Profiles'].append(data)
	
	Loaded = True
	AppendProfiles()					

def button_restore():
	SelectedProfile = QtBind.text(gui,lstProfiles)
	SelectedDate = QtBind.text(gui,ProfileDates).split(' ')[0]
	Server = QtBind.text(gui, txtServer)
	Char = QtBind.text(gui, txtChar)
	if not SelectedProfile or not SelectedDate:
		log('Plugin: Select a Profile and Backup Date')
		return

	BackupFileName = BuildFileName('Backup',Server,Char,SelectedProfile,SelectedDate)
	ExistingFileName = BuildFileName('Existing',Server,Char,SelectedProfile,SelectedDate)
	ExistingPath = path[:-7] + '/' + ExistingFileName
	BackupPath = path + '/' + BackupFileName
	RestoreBackup(BackupPath,ExistingPath,SelectedDate)
	

def BuildFileName(type,server,charname,profile,date=''):
	FileName = server + '_' + charname
	if profile == 'Default':
		if type == 'Existing':
			FileName = FileName + '.json'
		elif type == 'Backup':
			FileName = FileName + '_' + date + '.json'
	
	else:
		if type == 'Existing':
			FileName = FileName + '.' + profile + '.json'
		elif type == 'Backup':
			FileName = FileName + '.' + profile + '_' + date + '.json'
	return FileName

def AddDate(profile,date):
	Profiles = Configs['Profiles']
	for slot, item in enumerate(Profiles):
		if item:
			Profile = item['Profile']
			if Profile == profile:
				item['Backups'].append(date)



def CheckIfProfileExist(profile):
	Profiles = Configs['Profiles']
	for slot, item in enumerate(Profiles):
		if item:
			Profile = item['Profile']
			if Profile == profile:
				return True
	return False


def AppendProfiles():
	Profiles = Configs['Profiles']
	for slot, item in enumerate(Profiles):
		if item:
			Profile = item['Profile']
			QtBind.append(gui,lstProfiles,Profile)

def LoadBackups(profile):
	QtBind.clear(gui,ProfileDates)
	Profiles = Configs['Profiles']
	for slot, item in enumerate(Profiles):
		if item:
			Profile = item['Profile']
			if Profile == profile:
				dates = item['Backups']
				for date in dates:
					Age = CalculateAge(date)
					date = date + ' (%s Days ago)' %Age
					QtBind.append(gui,ProfileDates,date)

def CalculateAge(date):
	backup = str(date)
	CurrentTime = datetime.now()
	BackupDate = datetime.strptime(backup, '%Y-%m-%d')
	Age = CurrentTime - BackupDate
	return Age.days

def RestoreBackup(BackupPath,ExistingPath,date):
	try:
		shutil.copyfile(BackupPath,ExistingPath)
		log('Plugin: Backup Successfully Restored from [%s]' %date)
	except Exception as ex:
		log('Plugin: ERROR RESTORING BACKUP [%s]')

PreviouslySelected = ''
def event_loop():
	global PreviouslySelected
	if Loaded:
		SelectedProfile = QtBind.text(gui,lstProfiles)
		if PreviouslySelected != SelectedProfile:
			PreviouslySelected = SelectedProfile
			LoadBackups(SelectedProfile)




def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/BackupRestorer.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8")).split()
				for num, line in enumerate(lines):
					if line == 'version':
						NewestVersion = int(lines[num+2].replace(".",""))
						CurrentVersion = int(str(version).replace(".",""))
						if NewestVersion > CurrentVersion:
							log('Plugin: There is an update avaliable for [%s]!' % name)
							lblUpdate = QtBind.createLabel(gui,'There is an Update Avaliable, Press Here to Update',100,283)
							button1 = QtBind.createButton(gui, 'button_update', ' Update Plugin ', 350, 280)
		except:
			pass


def button_update():
	pypath = path[:-13]
	if os.path.exists(pypath + "Plugins/" + "BackupRestorer.py"):
		try:
			os.rename(pypath + "Plugins/" + "BackupRestorer.py", pypath + "Plugins/" + "BackupRestorerBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/BackupRestorer.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(pypath + "Plugins/" + "BackupRestorer.py", "w+") as f:
					f.write(lines)
					os.remove(pypath + "Plugins/" + "BackupRestorerBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckForUpdate()

log('Plugin: [%s] Version %s Loaded' % (name,version))
