from phBot import *
from threading import Timer
import QtBind
import struct
import random

PluginName = 'EnterVicious'
PluginVersion = '1.0.0'
gui = QtBind.init(__name__, PluginName)



###____USER SETTINGS____###

Leader = "Bunker"     #Enter the characters name that will control all others


###____GLOBALS____###

GotTicket = False


###____GUI____###

lblTitle = QtBind.createLabel(gui,'For Entering Sealed Dungeon of Vicious Shadows.. Type ENTER in Party Chat to Enter your Party',10,10)

btnCheckItems = QtBind.createButton(gui,'btnEnter',"    Enter Dungeon    ",10,30)




def btnEnter():
	log('Plugin: Trying To Enter....')
	Timer(random.uniform(1,8), enter_vicious, ()).start()


###____FUNCTIONS____###

def got_ticket():
	global GotTicket
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			name = item['name']
			number = item['quantity']
			# Search by servername
			if name == r"Chamber of Vicious Shadows Entrance Ticket":
				GotTicket = True
				return
	log('Plugin: You have a Dont Have any Entrance Tickets')
	GotTicket = False

def enter_vicious():
	got_ticket()
	global GotTicket
	if GotTicket:
		tele = get_teleport_data('Mysterious Priest', 'Sealed Dungeon of Vicious Shadows')
		if tele:
			npcs = get_npcs()
			for key, npc in npcs.items():
				if npc['name'] == 'Mysterious Priest':
					log("Plugin: Selecting Mysterious Priest")
					# select npc
					inject_joymax(0x7045, struct.pack('<I', key), False)
					# teleport data
					Timer(2.0, inject_joymax, [0x705A,struct.pack('<IBI', key, 2, tele[1]),False]).start()
					Timer(2.0, log, ["Plugin: Teleporting to [Sealed Dungeon of Vicious Shadows]"]).start()
					# confrim
					Timer(5.0, inject_joymax, [0x3080,b'\x01\x01',False]).start()
					Timer(5.0, log, ["Plugin: Confirm Entrance...Using Ticket"]).start()
					return
			log('Plugin: You are not near Mysterious Priest')


def handle_chat(t,player,msg):
	if player == Leader:
		# Parsing message command
		if msg == "ENTER":
			Timer(random.uniform(1,8), enter_vicious, ()).start()



log("Plugin: "+PluginName+" v"+PluginVersion+" successfully loaded")