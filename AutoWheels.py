from phBot import *
from threading import Timer
import struct
import QtBind
import urllib.request
import os
import sqlite3

name = 'AutoWheels'
version = 1.0
NewestVersion = 0


gui = QtBind.init(__name__, name)

lbl = QtBind.createLabel(gui,'Stop if total STR >= ',20,20)
txt_STR_limit = QtBind.createLineEdit(gui,"1",120,17,40,20)

lbl = QtBind.createLabel(gui,'Stop if total INT >= ',20,50)
txt_INT_limit = QtBind.createLineEdit(gui,"1",120,47,40,20)

lbl = QtBind.createLabel(gui,'Stop if total HP >= ',20,80)
txt_HP_limit = QtBind.createLineEdit(gui,"1",120,77,40,20)

lbl = QtBind.createLabel(gui,'Stop if total MP >= ',20,110)
txt_MP_limit = QtBind.createLineEdit(gui,"1",120,107,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Durability % >= ',20,140)
txt_DUR_limit = QtBind.createLineEdit(gui,"1",160,137,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Parry Rate % >= ',20,170)
txt_ER_limit = QtBind.createLineEdit(gui,"1",170,167,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Attack Rate % >= ',20,200)
txt_HR_limit = QtBind.createLineEdit(gui,"1",170,197,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Critcal >= ',20,230)
txt_CRITICAL_limit = QtBind.createLineEdit(gui,"1",130,227,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Block Rate >= ',20,260)
txt_BLOCK_limit = QtBind.createLineEdit(gui,"1",150,257,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Frostbite % >= ',300,20)
txt_FROSTBITE_limit = QtBind.createLineEdit(gui,"1",440,17,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Shock % >= ',300,50)
txt_ESHOCK_limit = QtBind.createLineEdit(gui,"1",425,47,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Burn % >= ',300,80)
txt_BURN_limit = QtBind.createLineEdit(gui,"1",420,77,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Poison % >= ',300,110)
txt_POISON_limit = QtBind.createLineEdit(gui,"1",430,107,40,20)

lbl = QtBind.createLabel(gui,'Stop if total Zombie % >= ',300,140)
txt_ZOMBIE_limit = QtBind.createLineEdit(gui,"1",430,137,40,20)

cbxFate = QtBind.createCheckBox(gui, 'cbxFate_clicked','Use Wheel of Fate', 300, 170)
cbxFortune = QtBind.createCheckBox(gui, 'cbxFate_clicked','Use Wheel of Fortune', 300, 200)

lbl = QtBind.createLabel(gui,'Stop if total Lines >= ',300,230)
txt_lines_limit = QtBind.createLineEdit(gui,"1",410,227,40,20)

lbl = QtBind.createLabel(gui,'Delay Between Wheels (ms)',300,260)
txt_delay = QtBind.createLineEdit(gui,"5000",440,257,40,20)

lbl = QtBind.createLabel(gui,'Current Items',520,20)
combo_items = QtBind.createCombobox(gui,520,35,200,30)
button = QtBind.createButton(gui, 'button_refresh', '  Refresh Items ', 520, 70)
display = QtBind.createList(gui,520,100,200,165)

buttonStartStop = QtBind.createButton(gui, 'button_start', ' Start ', 520, 270)

lbl = QtBind.createLabel(gui,'**USE AT YOUR OWN RISK**',20,285)
lbl = QtBind.createLabel(gui,'**THIS PLUGIN DOESNT KNOW EXISTING MAGIC OPTIONS, THE FIRST TIME YOU USE THIS ON AN ITEM IT WILL ALWAYS USE A WHEEL**',20,300)

started = False
def button_start():
	global started, thread_
	if not started:
		started = True
		QtBind.setText(gui,buttonStartStop,'  Stop  ')
		use_wheel_fate()
	
	elif started:
		stop_wheeling()
		
def stop_wheeling():
	global started, thread_
	started = False
	QtBind.setText(gui,buttonStartStop,'  Start  ')
	if thread_:
		thread_.cancel()
		thread_ = None
	close_database_connection()

current_items = {}
def button_refresh():
	global 	current_items
	current_items = {}
	index = 0
	QtBind.clear(gui,combo_items)
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			item_data = get_item(item['model'])
			#skip equipped items
			if slot <= 13:
				continue
			#equipable items
			if item_data['tid1'] == 1:
				current_items.update({index: slot})
				index += 1
				QtBind.append(gui,combo_items,f"{item['name']} +{item['plus']}")
	
thread_ = None
def handle_joymax(opcode,data):
	global thread_
	if opcode == 0xB151:
		connect_to_database()
		magic_options = {}
		QtBind.clear(gui,display)
		index = 0
		result = struct.unpack_from('<B', data, index)[0]
		index += 1
		action = struct.unpack_from('<B', data, index)[0]
		index += 1
		is_success = struct.unpack_from('<B', data, index)[0]
		if is_success == 1:
			index += 2
			#skip next byte
			slot = struct.unpack_from('<B', data, index)[0]
			index += 1
			rental_type = struct.unpack_from('<I', data, index)[0]
			index += 4
			item_id = struct.unpack_from('<I', data, index)[0]
			index += 4
			plus = struct.unpack_from('<B', data, index)[0]
			index += 1
			attributes = struct.unpack_from('<Q', data, index)[0]
			index += 8
			durability = struct.unpack_from('<I', data, index)[0]
			index += 4
			number_of_magiclines = struct.unpack_from('<B', data, index)[0]
			index += 1	
			for x in range(number_of_magiclines):
				id = struct.unpack_from('<I', data, index)[0]
				index += 4
				amount = struct.unpack_from('<I', data, index)[0]
				index += 4
				if id == 0:
					continue
				magic_option_data = get_magic_option(id)
				QtBind.append(gui,display,f"{magic_option_data['name']}: {amount}")
				
				attr = magic_option_data['name']
				if attr in magic_options:
					magic_options[attr] += amount
				else:
					magic_options[attr] = amount
				
			if not check_options_complete(magic_options):
				if started:
					delay = int(QtBind.text(gui,txt_delay)) / 1000
					thread_ = Timer(delay, use_wheel_fate)
					thread_.start()
			else:
				stop_wheeling()
		close_database_connection()

def check_options_complete(magic_options):
	for key, value in magic_options.items():
		if len(magic_options) >= int(QtBind.text(gui,txt_lines_limit)):
			log(f"Plugin: Stopping due to max number of lines reached [{len(magic_options)}]")
			return True
		if 'STR' in key:
			max_value = int(QtBind.text(gui,txt_STR_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to STR limit reached [{value}]")
				return True
		if 'INT' in key:
			max_value = int(QtBind.text(gui,txt_INT_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to INT limit reached [{value}]")
				return True				
		if 'HP' in key:
			max_value = int(QtBind.text(gui,txt_HP_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to HP limit reached [{value}]")
				return True		
		if 'MP' in key:
			max_value = int(QtBind.text(gui,txt_STR_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to MP limit reached [{value}]")
				return True				
		if 'DUR' in key:
			max_value = int(QtBind.text(gui,txt_DUR_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Durabiliy limit reached [{value}]")
				return True
		if 'ER' in key:
			max_value = int(QtBind.text(gui,txt_ER_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Parry Rate limit reached [{value}]")
				return True
		if 'HR' in key:
			max_value = int(QtBind.text(gui,txt_HR_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Attack Rate limit reached [{value}]")
				return True
		if 'CRITICAL' in key:
			max_value = int(QtBind.text(gui,txt_CRITICAL_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Critcal limit reached [{value}]")
				return True
		if 'BLOCK' in key:
			max_value = int(QtBind.text(gui,txt_BLOCK_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Block limit reached [{value}]")
				return True
		if 'FROSTBITE' in key:
			max_value = int(QtBind.text(gui,txt_FROSTBITE_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Frostbite limit reached [{value}]")
				return True
		if 'ESHOCK' in key:
			max_value = int(QtBind.text(gui,txt_ESHOCK_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Shock limit reached [{value}]")
				return True
		if 'BURN' in key:
			max_value = int(QtBind.text(gui,txt_BURN_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Burn limit reached [{value}]")
				return True
		if 'POISON' in key:
			max_value = int(QtBind.text(gui,txt_POISON_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Poison limit reached [{value}]")
				return True
		if 'ZOMBIE' in key:
			max_value = int(QtBind.text(gui,txt_ZOMBIE_limit))
			if value >= max_value:
				log(f"Plugin: Stopping due to Zombie limit reached [{value}]")
				return True
	return False


def use_wheel_fate():
	wheels = []
	item_slot = None
	if QtBind.isChecked(gui,cbxFate):
		wheels.append('Wheel of Fate')
	if QtBind.isChecked(gui,cbxFortune):
		wheels.append('Wheel of Fortune')
	
	if current_items:
		item_slot = current_items[QtBind.currentIndex(gui,combo_items)]
	if not item_slot:
		log(f"Plugin: Please Select an Item")
		stop_wheeling()
		return
		
	wheel_slot = get_wheel_slot(wheels)
	if wheel_slot == -1:
		log(f"Plugin: No Wheels left.. stopping")
		stop_wheeling()	
		return
		
	
	p = b'\x02' #alchemy action fuse
	p += b'\x19' #type
	p += b'\x02'
	p += struct.pack('B',item_slot) #item slot
	p += struct.pack('B',wheel_slot) #wheel slot
	inject_joymax(0x7151,p,False)
	log(f"Plugin: Using {get_item_at_slot(wheel_slot)['name']} on [{get_item_at_slot(item_slot)['name']}]")
	
def get_wheel_slot(type):
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			if item['name'] in type:
				return slot
	return -1

def get_item_at_slot(slot_):
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			if slot == slot_:
				return item
	return None	
	
def get_magic_option(magic_id):
	connect_to_database()
	if db3_connection:
		result = db3_connection.cursor().execute('SELECT * FROM magicoption WHERE id=?',(magic_id,)).fetchone()
		if result:
			return  {"name": result[1], "degree": result[3], "max_value": result[5]}
	return None

db3_connection = None
def connect_to_database():
	global db3_connection
	if not db3_connection:
		bot_path = os.getcwd()
		locale = get_locale()
		if locale == 18:
			path = f'{bot_path}/Data/iSRO.db3'
		if locale == 56:
			path = f'{bot_path}/Data/TRSRO.db3'
		db3_connection = sqlite3.connect(path, check_same_thread=False)
	
def close_database_connection():
	global db3_connection
	if db3_connection:
		db3_connection.close()
		db3_connection = None

def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/AutoWheels.py', headers={'User-Agent': 'Mozilla/5.0'})
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
	if os.path.exists(path + "Plugins/" + "AutoWheels.py"):
		try:
			os.rename(path + "Plugins/" + "AutoWheels.py", path + "Plugins/" + "AutoWheelsBACKUP.py")
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/AutoWheels.py', headers={'User-Agent': 'Mozilla/5.0'})
			with urllib.request.urlopen(req) as f:
				lines = str(f.read().decode("utf-8"))
				with open(path + "Plugins/" + "AutoWheels.py", "w+") as f:
					f.write(lines)
					os.remove(path + "Plugins/" + "AutoWheelsBACKUP.py")
					log('Plugin Successfully Updated, Please Reload the Plugin to Use')
		except Exception as ex:
			log('Error Updating [%s] Please Update Manually or Try Again Later' %ex)

CheckForUpdate()
log('Plugin: [%s] Version %s Loaded' % (name,version))
