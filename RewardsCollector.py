from phBot import *
from threading import Timer
import struct
import QtBind
import urllib.request

name = 'RewardsCollector'
version = 1.1
NewestVersion = 0

CollectMessageID = 0

gui = QtBind.init(__name__, name)

button = QtBind.createButton(gui, 'button_collect', '  Collect Rewards ', 20, 20)

def button_collect():
	log('Plugin: Receiving all Rewards...')
	GetMessages()

def handle_joymax(opcode,data):
	global CollectMessageID
	if opcode == 0x38DD and data[0] == 1 and data[1] == 1:
		log('Plugin: Reward Message Recevied...')
		CollectMessageID = struct.unpack_from('<Q', data, 2)[0]

	if opcode == 0xB0DE:
		if data[0] == 2 and data[1] == 5 and data[2] == 7 and data[3] == 220:
			log('Plugin: Error Receiving Messages... Please teleport')
			return True
		if data[0] == 1 and data[1] == 5:	
			messageCount = struct.unpack_from('<H', data, 2)[0]
			Index = 6
			for i in range(messageCount):
				Index += 1
				messageID = struct.unpack_from('<Q', data, Index)[0]
				Index += 9
				MessageSenderLength = struct.unpack_from('<H', data, Index)[0]
				Index += 2
				messageSender = struct.unpack_from('<' + str(MessageSenderLength) + 's',data,Index)[0].decode('cp1252')
				Index += MessageSenderLength
				messageTypeLength = struct.unpack_from('<H', data, Index)[0]
				Index += 2
				messageType = struct.unpack_from('<' + str(messageTypeLength*2) + 's',data,Index)[0].decode('utf-16')
				log(messageType)
				Index += messageTypeLength*2
				Index += 8
				itemAmount = struct.unpack_from('<B', data, Index)[0]
				Index += (itemAmount * 4) + 1

				if messageType.endswith(('UIIT_STYRIA_SERVER_TITLE', 'UIIT_INFINITY_SERVER_TITLE')):
					if GetRemainingSlots() < 3:
						log('Plugin: Not Enough Inventory Slots to Claim Items...')
						return True
					receiveItemFromMessage(messageID)
					#Timer(0.3, DeleteMessage, [messageID]).start()
	return True

def GetMessages():
	p = b'\x05'
	inject_joymax(0x70DE,p, False)


def receiveItemFromMessage(messageID):
	p = b'\x01'
	p += struct.pack('<Q', messageID)
	inject_joymax(0x70DF, p, False)
	log('Plugin: Claiming Items From Message [%s]' %messageID)

def DeleteMessage(messageID):
	p = b'\x04\x01'
	p += struct.pack('<Q', messageID)
	inject_joymax(0x70DE, p, False)
	log('Plugin: Deleting Message [%s]' %messageID)

def GetRemainingSlots():
	Size = get_inventory()['size'] - 13
	Items = get_inventory()['items']
	TotalItems = 0
	for slot, Item in enumerate(Items):
		if slot >= 13:
			if Item:
				TotalItems += 1
	return Size - TotalItems

def teleported():
	global CollectMessageID
	if CollectMessageID != 0:
		if GetRemainingSlots() < 3:
			log('Plugin: Not Enough Inventory Slots to Claim Items...')
			return
		Timer(5.0, receiveItemFromMessage, [CollectMessageID]).start()
		CollectMessageID = 0
	

def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/RewardsCollector.py', headers={'User-Agent': 'Mozilla/5.0'})
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
	path = get_config_dir()[:-7]
	if os.path.exists(path + "Plugins/" + "RewardsCollector.py"):
		try:
			os.rename(path + "Plugins/" + "RewardsCollector.py", path + "Plugins/" + "RewardsCollectorBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/RewardsCollector.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(path + "Plugins/" + "RewardsCollector.py", "w+") as f:
					f.write(lines)
					os.remove(path + "Plugins/" + "RewardsCollectorBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckForUpdate()
log('Plugin: [%s] Version %s Loaded' % (name,version))
