from phBot import *
from time import localtime, strftime
from threading import Timer
import QtBind
import struct
import random
import json
import urllib.request
import os

name = 'AutoConsignment'
version = 1.3
NewestVersion = 0
path = get_config_dir()[:-7]

gui = QtBind.init(__name__, name)

PageIndex = 0
ItemCount = 0
Started = False


button1 = QtBind.createButton(gui, 'button_search', ' Search ', 500, 32)
lstItems = QtBind.createList(gui,10,62,580,200)

lblBuy = QtBind.createLabel(gui,'Auto Buy Settings',600,23)
lblBuy = QtBind.createLabel(gui,'Item Names',600,40)
txtAddItem = QtBind.createLineEdit(gui,"",600,55,120,20)
lstBuyItems = QtBind.createList(gui,600,102,120,80)
button1 = QtBind.createButton(gui, 'button_add', '                Add               ', 600, 77)
button1 = QtBind.createButton(gui, 'button_remove', '             Remove            ', 600, 182)


lblBuy = QtBind.createLabel(gui,'Max Price',600,205)
txtMaxPrice = QtBind.createLineEdit(gui,"0",600,218,120,20)

lblBuy = QtBind.createLabel(gui,'Min. Quantity',600,238)
txtQuantity = QtBind.createLineEdit(gui,"0",600,253,120,20)

buttonStart = QtBind.createButton(gui, 'button_start', '               Start               ', 600, 280)

lblClass = QtBind.createLabel(gui,'Class',10,10)
ComboClass = QtBind.createCombobox(gui,10,32,150,22)

lblType = QtBind.createLabel(gui,'Type',170,10)
ComboType = QtBind.createCombobox(gui,170,32,150,22)

lblDegree = QtBind.createLabel(gui,'Degree',330,10)
ComboDegree = QtBind.createCombobox(gui,330,32,150,22)

def button_start():
	global Started, PageIndex, ItemCount
	if not Started:
		Started = True
		QtBind.setText(gui,buttonStart,'               Stop               ')
		EnterConsignmentNPC()
	elif Started:
		PageIndex = 0
		ItemCount = 0
		Started = False
		QtBind.setText(gui,buttonStart,'               Start               ')
		ExitNPC()	

def button_search():
	global Started
	QtBind.clear(gui,lstItems)
	Started = 'Search'
	EnterConsignmentNPC()

def button_add():
	item = QtBind.text(gui,txtAddItem)
	QtBind.append(gui,lstBuyItems,item)
	QtBind.setText(gui, txtAddItem,"")
	log('Plugin: Item Added [%s]' %item)

def button_remove():
	item = QtBind.text(gui,lstBuyItems)
	QtBind.remove(gui,lstBuyItems,item)
	log('Plugin: Item Removed [%s]' %item)


def LoadList(List):
	QtBind.clear(gui,ComboType)
	QtBind.clear(gui,ComboDegree)
	if List == 'All':
		for item in ItemList:
			QtBind.append(gui,ComboClass,item)

def LoadDegree():
	QtBind.clear(gui,ComboDegree)
	for i in range(1,16):
		QtBind.append(gui,ComboDegree,str(i))

SelectedClass = ''
SelectedType = ''
NeedsDegree = ['Attribute Stone','Element','Alchemic Stone','Socket Stone','Earring','Necklace','Ring','Garment','Armor','Protector','Blade','Bow','Shield','Spear','Sword','Glaive','Heavy Armor','Light Armor','Robe','Clearic Rod','Crossbow','Dagger','Dual Axe','Harp','One-handed Sword','Staff','Two-handed Sword','Warlock Rod','Fortress Weapon','Job Accessories','Job Reinforcement','Job Armor','Job Weapons']


def event_loop():
	global SelectedClass, SelectedType
	if not Started:
		CurrentClass = QtBind.text(gui, ComboClass)
		CurrentType = QtBind.text(gui, ComboType)

		if SelectedClass != CurrentClass:
			QtBind.clear(gui,ComboType)
			QtBind.clear(gui,ComboDegree)
			SelectedClass = CurrentClass
			for item in ItemList[SelectedClass][0]:
				QtBind.append(gui,ComboType,item)

		if SelectedType != CurrentType:
			SelectedType = CurrentType
			if SelectedType in NeedsDegree:
				LoadDegree()
			else:
				QtBind.clear(gui,ComboDegree)


#page starts with 0.. so page 1 is 0 in the packet
def RequestPage(Page):
	if Page == 0:
		p = b'\x01'
	if Page >= 1:
		p = b'\x03'
	p += struct.pack('B',Page)

	#search settings
	CurrentClass = QtBind.text(gui, ComboClass)
	CurrentType = QtBind.text(gui, ComboType)
	CurrentDegree = QtBind.text(gui, ComboDegree)
	if CurrentDegree == '':
		CurrentDegree = 0
	ItemIndex = ItemList[SelectedClass][0][CurrentType]
	p += struct.pack('<I',ItemIndex)
	p += struct.pack('<H',int(CurrentDegree))
	p += b'\x00'
	inject_joymax(0x750C,p,False)


def EnterConsignmentNPC():
	npcs = get_npcs()
	for key, npc in npcs.items():
		if npc['servername'].startswith('NPC_OPEN_MARKET'):
			log("Plugin: Entering NPC")
			p = struct.pack('<I', key)
			inject_joymax(0x7045,p, False)
			p += b'\x21'
			inject_joymax(0x7046,p, False)
			Timer(2.0,RequestPage(0)).start()
			return
	log('Plugin: You are not near a Consignment NPC')
			
def ExitNPC():
	#exit trade window 
	inject_joymax(0x7507,b'',False)
	#exit npc window
	npcs = get_npcs()
	for key, npc in npcs.items():
		if npc['servername'].startswith('NPC_OPEN_MARKET'):
			log("Plugin: Exiting NPC")
			inject_joymax(0x704B, struct.pack('<I', key), False)

def BuyItem(CharName,ListingID,ItemID):
	p = struct.pack("H", int(len(CharName)))
	p += CharName.encode('ascii')
	p += struct.pack("<I", ListingID)
	p += struct.pack("<I", ItemID)
	inject_joymax(0x750A,p, False)
	Timer(3.0, ExitNPC, ()).start()

def handle_joymax(opcode,data):
	if opcode == 0xB50C:
		global PageIndex, ItemCount, Started
		if data[0] == 1 and Started or Started == 'Search':

			BuyItems = QtBind.getItems(gui,lstBuyItems)
			BuyQuantity = int(QtBind.text(gui, txtQuantity))
			BuyMaxPrice = int(QtBind.text(gui, txtMaxPrice))

			Index = 1
			NumberItemsOnPage = data[Index]
			Index += 1
			NumberOfPages = data[Index]
			Index += 1
			for i in range(NumberItemsOnPage):
				#used to purchase i think
				ListingID = struct.unpack_from('<I',data,Index)[0]
				Index += 4
				NameLength = struct.unpack_from('<H',data,Index)[0]
				Index += 2
				CharName = struct.unpack_from('<' + str(NameLength) + 's',data,Index)[0].decode('cp1252')
				Index += NameLength + 1
				#in the database
				ItemID = struct.unpack_from('<I',data,Index)[0]
				ItemName = get_item(ItemID)['name']
				Index += 4
				Quantity = int(struct.unpack_from('<I',data,Index)[0])
				Index += 4
				Price = int.from_bytes(struct.unpack_from('<8s',data,Index)[0], "little")
				Index += 8
				#no idea what next 8 bytes are..skip them
				Index += 8
				ItemCount += 1
				if ItemName in BuyItems and Price <= BuyMaxPrice and Quantity >= BuyQuantity:
					log('Buying [%s][%s] from [%s] for [%s]' %(ItemName,Quantity,CharName,Price))
					BuyItem(CharName,ListingID,ItemID)
					PageIndex = 0
					ItemCount = 0
					#start again in 10 seconds
					Timer(10.0, EnterConsignmentNPC, ()).start()
					return

				itemdata = 'Seller: [%s] Quantity: [%s] Price: [%s] Item :[%s]' %(CharName,Quantity,Price,ItemName)
				QtBind.append(gui,lstItems,itemdata)
			#request next page
			if PageIndex < NumberOfPages:
				PageIndex += 1
				Timer(1.0,RequestPage(PageIndex)).start()
			else:
				log("Plugin: Finished Checking all Items.. Total Items[%s]" %ItemCount)
				PageIndex = 0
				ItemCount = 0
				Timer(1.0, ExitNPC, ()).start()
				#start again in 20 seconds
				if Started != 'Search':
					Timer(20.0, EnterConsignmentNPC, ()).start()
				else:
					Started = False
			return False

	return True

ItemList = {
    "Alchemy": [
        {
            'Attribute Stone': 37,
            'Element': 35,
            'Elixir': 33,
            'Alchemic Stone': 36,
            'Alchemic Ingredient': 39,
            'Upgrade Ingredient': 63,
            'Socket Stone': 34
        }
    ],
    "Expendables": [
        {
            'Arrow': 46,
            'Pills': 43,
            'Enchancement': 45,
            'Recovery Potion': 42,
            'Return/Res.': 44
        }
    ],
    "Chinese Accessory": [
        {
            'Earring': 11,
            'Necklace': 10,
            'Ring': 12
        }
    ],
    "Chinese Armor": [
        {
            'Garment': 9,
            'Armor': 7,
            'Protector': 8
        }
    ],
    "Chinese Weapon": [
        {
            'Blade': 2,
            'Bow': 5,
            'Shield': 6,
            'Spear': 3,
            'Sword': 1,
            'Glaive': 4
        }
    ],
    "COS": [
        {
            'COS': 40,
            'COS Items': 41,
            'Fellow Items': 64
        }
    ],
    "Dress": [
        {
            'Avatar Dress': 30,
            'Additional Dress': 31,
            'Awakening Item': 32,
            'Triangluar Conflict': 29
        }
    ],
    "Others": [
        {
            'Transformation': 52,
            'Chatting': 55,
            'Others': 57,
            'Repair': 56,
            'Skill': 54,
            'Special Items': 53
        }
    ],
    "European Accessory": [
        {
            'Earring': 36,
            'Necklace': 26,
            'Ring': 28
        }
    ],
    "European Armor": [
        {
            'Heavy Armor': 23,
            'Light Armor': 24,
            'Robe': 25
        }
    ],
    "European Weapon": [
        {
            'Clearic Rod': 17,
            'Crossbow': 19,
            'Dagger': 20,
            'Dual Axe': 15,
            'Harp': 21,
            'Shield': 22,
            'One-handed Sword': 13,
            'Staff': 18,
            'Two-handed Sword': 14,
            'Warlock Rod': 16
        }
    ],
    "Event": [
        {
            'Event Items': 51
        }
    ],
    "Exchange": [
        {
            'Coin': 50
        }
    ],
    "Fortress War": [
        {
            'Fortress Item': 49,
            'Fortress Weapon': 48
        }
    ],
    "Guild": [
        {
            'Guild Items': 28
        }
    ],
    "Job Equipment": [
        {
            'Job Accessories': 60,
            'Job Reinforcement': 61,
            'Job Armor': 59,
            'Job Items': 62,
            'Job Weapons': 58
        }
    ]
}

def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/AutoConsignment.py', headers={'User-Agent': 'Mozilla/5.0'})
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
	if os.path.exists(path + "Plugins/" + "AutoConsignment.py"):
		try:
			os.rename(path + "Plugins/" + "AutoConsignment.py", path + "Plugins/" + "AutoConsignmentBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/AutoConsignment.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(path + "Plugins/" + "AutoConsignment.py", "w+") as f:
					f.write(lines)
					os.remove(path + "Plugins/" + "AutoConsignmentBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckForUpdate()

LoadList('All')

log('Plugin: [%s] Version %s Loaded' % (name,version))
