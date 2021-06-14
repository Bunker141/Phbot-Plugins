from phBot import *
import urllib.request
from threading import Timer
from datetime import datetime, timedelta
import datetime
import os
import signal
import struct
import subprocess

name = 'ScriptCommands'
version = 1.0
NewestVersion = 0


#get phbot folder path
path = get_config_dir()[:-7]

StartBotAt = 0
CloseBotAt = 0
CheckStartTime = False
CheckCloseTime = False
SkipCommand = False
delay_counter = 0


def LeaveParty(args):
	if get_party():
		inject_joymax(0x7061,b'',False)
		log('Plugin: Leaving Party')
	return 0

#Notification,title,message..show a windows notification, bot must be minimized
def Notification(args):
	if len(args) == 3:
		title = args[1]
		message = args[2]
		show_notification(title, message)
		return 0
	log('Plugin: Incorrect Notification command')
	return 0

#NotifyList,message.. Create a notification in the list
def NotifyList(args):
	if len(args) == 2:
		message = args[1]
		create_notification(message)
		return 0
	log('Plugin: Incorrect NotifyList command')
	return 0

#PlaySound,ding.wav...wav file must be in your phbot folder
def PlaySound(args):
	FileName = args[1]
	if os.path.exists(path + FileName):
		play_wav(path + FileName)
		log('Plugin: Playing [%s]' %FileName)
		return 0
	log('Plugin: Sound file [%s] doesnt exist' %FileName)
	return 0

#example - SetScript,Mobs103.txt
#script must be in your phbot folder
def SetScript(args):
	name = args[1]
	if os.path.exists(path + name):
		set_training_script(path + name)
		log('Plugin: Changing Script to [%s]' %name)
		return 0
	log('Plugin: Script [%s] doesnt exist' %name)
	return 0

#CloseBot..kills the bot immediately
#CloseBot,in,5... kills the bot in 5 mins
#CloseBot,at,05:30..kills the bot at a specific time.. 24hour clock
def CloseBot(args):
	global CloseBotAt, CheckCloseTime
	CheckCloseTime = True
	if len(args) == 1:
		Terminate()
		return 0
	type = args[1]
	time = args[2]
	if type == 'in':
		CloseBotAt = str(datetime.datetime.now() + timedelta(minutes=int(time)))[11:16]
		log('Plugin: Closing Bot At [%s]' %CloseBotAt)
	elif type == 'at':
		CloseBotAt = time
		log('Plugin: Closing Bot At [%s]' %CloseBotAt)
	return 0

def Terminate():
	log("Plugin: Closing bot...")
	#os.kill(os.getpid(),9)

#GoClientless.. Kills the Client instantly
def GoClientless(args):
	pid = get_client()['pid']
	if pid:
		os.kill(pid, signal.SIGTERM)
		return 0
	log('Plugin: Client is not open!')
	return 0


#Stop and Start the bot at specified time
#Ex StartBot,in,5.. Starts bot in 5 mins
#Ex StartBot,at,05:30.. Starts bot at specified time.. 24hour clock
def StartBot(args):
	global StartBotAt, CheckStartTime, SkipCommand
	#avoid bot doing command again after restarting
	if SkipCommand:
		SkipCommand = False
		return 0
	stop_bot()
	type = args[1]
	time = args[2]
	CheckStartTime = True
	if type == 'in':
		StartBotAt = str(datetime.datetime.now() + timedelta(minutes=int(time)))[11:16]
		log('Plugin: Starting Bot At [%s]' %StartBotAt)
	elif type == 'at':
		StartBotAt = time
		log('Plugin: Starting Bot At [%s]' %StartBotAt)
	return 0

#StopStart..Stops and starts the bot 1 second later
def StopStart(args):
	global SkipCommand
	#avoid bot doing command again after restarting
	if SkipCommand:
		SkipCommand = False
		return 0
	stop_bot()
	Timer(1.0, start_bot, ()).start()
	SkipCommand = True
	return 0

#StartTrace,player..Starts tracing a player
def StartTrace(args):
	if len(args) == 2:
		player = args[1]
		start_trace(player)
	log('Plugin: Incorrect StartTrace format')

#RemoveSkill,skillname...Remove the skill if active
def RemoveSkill(args):
	locale = get_locale()
	if locale == 18 or locale == 56:
		RemSkill = args[1]
		skills = get_active_skills()
		for ID, skill in skills.items():
			if skill['name'] == RemSkill:
				packet = b'\x01\x05'
				packet += struct.pack('<I', ID)
				packet += b'\x00'
				inject_joymax(0x7074,packet,False)
				log('Plugin: Removing skill [%s]' %RemSkill)
				return 0
		log('Plugin: Skill is not active')
		return 0
	log('Plugin: Only supported on iSRO or TRSRO, contact me to add support for your server')
	return 0

#Drop,itemname... drops the first stack of the specified item
def Drop(args):
	locale = get_locale()
	if locale == 18 or locale == 56:
		DropItem = args[1]
		items = get_inventory()['items']
		for slot, item in enumerate(items):
			if item:
				name = item['name']
				if name == DropItem:
					p = b'\x07' # static stuff maybe
					p += struct.pack('B', slot)
					log('Plugin: Dropping item [%s][%s]' %(item['quantity'],name))
					inject_joymax(0x7034,p,True)
					return 0
		log(r'Plugin: You Dont Have any Items to Drop')
		return 0
	log('Plugin: Only supported on iSRO or TRSRO, contact me to add support for your server')
	return 0

#OpenphBot,commandlinearguments..opens a bot with the specified arguements
def OpenphBot(args):
	cmdargs = args[1]
	if os.path.exists(path + "phBot.exe"):
		subprocess.Popen(path + "phBot.exe " + cmdargs)
		log('Plugin: Opening a new bot')
		return 0
	log('Plugin: Invalid path to bot')
	return 0

	
def event_loop():
	global delay_counter, CheckStartTime, SkipCommand, CheckCloseTime
	if CheckStartTime:
		delay_counter += 500
		if delay_counter >= 60000:
			delay_counter = 0
			CurrentTime = str(datetime.datetime.now())[11:16]
			if CurrentTime == StartBotAt:
				CheckStartTime = False
				SkipCommand = True
				log('Plugin: Starting Bot')
				start_bot()

	elif CheckCloseTime:
		delay_counter += 500
		if delay_counter >= 60000:
			delay_counter = 0
			CurrentTime = str(datetime.datetime.now())[11:16]
			if CurrentTime == CloseBotAt:
				CheckCloseTime = False
				Terminate()



def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/ScriptCommands.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8")).split()
				for num, line in enumerate(lines):
					if line == 'version':
						NewestVersion = int(lines[num+2].replace(".",""))
						CurrentVersion = int(str(version).replace(".",""))
						if NewestVersion > CurrentVersion:
							log('Plugin: There is an update avaliable for [%s]!' % name)
		except:
			pass


CheckForUpdate()
log('Plugin: [%s] Version %s Loaded' % (name,version))