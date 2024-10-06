from phBot import *
from threading import Timer
import struct
import QtBind
import urllib.request

name = 'ItemStorage'
version = 1.0
NewestVersion = 0

gui = QtBind.init(__name__, name)

button = QtBind.createButton(gui, 'button_getlist', '  Get List  ', 20, 20)
button = QtBind.createButton(gui, 'button_claim', '  Claim Selected  ', 200, 20)
button = QtBind.createButton(gui, 'button_claimall', '  Claim All  ', 400, 20)
lstItems = QtBind.createList(gui,10,62,580,200)

def button_getlist():
	global count
	count = 0
	QtBind.clear(gui,lstItems)
	OpenItemList(1)
	
def button_claim():
	SelectedItem = QtBind.text(gui,lstItems)
	messageID = SelectedItem.split(" ")[0].strip("[]")
	receiveItem(int(messageID))

def button_claimall():
	inject_joymax(0x7558 , b'\x00\x00\x00\x00\x00\x00\x00\x00', False)

count = 0
def handle_joymax(opcode,data):
	global count
	if opcode == 0xB557:
		locale = get_locale()
		if data[0] == 1:
			PageCount = struct.unpack_from('<B', data, 1)[0]
			CurrentPage = struct.unpack_from('<B', data, 2)[0]
			ItemCount = struct.unpack_from('<B', data, 3)[0]
			Index = 4
			for i in range(ItemCount):
				if locale == 18 or locale == 56: #isro and trsro
					try:
						messageID = struct.unpack_from('<Q', data, Index)[0]
						Index += 8
						Type = struct.unpack_from('<I', data, Index)[0]
						Index += 4
						if Type == 3:
							ItemID = struct.unpack_from('<I', data, Index)[0]
							ItemName = get_item(ItemID)['name']
							Index += 4
							Quantity = struct.unpack_from('<I', data, Index)[0]
							Index += 12
							QtBind.append(gui,lstItems,f"[{messageID}] - [{ItemName}]")
							count += 1
							continue
						ItemNameLength = struct.unpack_from('<H', data, Index)[0]
						Index += 2
						ItemName = struct.unpack_from('<' + str(ItemNameLength*2) + 's',data,Index)[0].decode('utf-16')
						Index += ItemNameLength*2
						Index += 12
						QtBind.append(gui,lstItems,f"[{messageID}] - [{ItemName}]")
						count += 1
					except Exception as ex:
						data = str(' '.join('{:02X}'.format(x) for x in data))
						log(f"Plugin: Error parsing Item Storage data, send this data in discord [{data}] [{get_locale()}]")
						pass
				else: #all other servers? based on private servers but probably doesnt work because this example only has type 3
					try:
						messageID = struct.unpack_from('<Q', data, Index)[0]
						Index += 8
						Type = struct.unpack_from('<I', data, Index)[0]
						Index += 4
						if Type == 3:
							ItemID = struct.unpack_from('<I', data, Index)[0]
							ItemName = get_item(ItemID)['name']
							Index += 4
							Quantity = struct.unpack_from('<I', data, Index)[0]
							Index += 8
							QtBind.append(gui,lstItems,f"[{messageID}] - [{ItemName}]")
							count += 1
					except Exception as ex:
						data = str(' '.join('{:02X}'.format(x) for x in data))
						log(f"Plugin: Error parsing Item Storage data, send this data in discord [{data}] [{get_locale()}]")
						pass	
							
			log(f"Plugin: Finished Checking Page [{CurrentPage}] of [{PageCount}]")
			if CurrentPage < PageCount:
				Timer(1.0,OpenItemList,[CurrentPage+1]).start()
			else:
				log(f"Plugin: Finished checking all, total items [{count}]")
				
	if opcode == 0xB558:
		if data[0] == 2:
			log(f"Plugin: Failed to collect silk item, is your inventory full?")
		
	return True

def OpenItemList(page):
	p = struct.pack('B',page)
	inject_joymax(0x7557,p, False)


def receiveItem(messageID):
	p = struct.pack('<Q', messageID)
	inject_joymax(0x7558 , p, False)

def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/ItemStorage.py', headers={'User-Agent': 'Mozilla/5.0'})
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
	if os.path.exists(path + "Plugins/" + "ItemStorage.py"):
		try:
			os.rename(path + "Plugins/" + "ItemStorage.py", path + "Plugins/" + "ItemStorageBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/ItemStorage.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(path + "Plugins/" + "ItemStorage.py", "w+") as f:
					f.write(lines)
					os.remove(path + "Plugins/" + "ItemStorageBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckForUpdate()
log('Plugin: [%s] Version %s Loaded' % (name,version))
