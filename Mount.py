from phBot import *
from threading import Timer
import QtBind
import struct


gui = QtBind.init(__name__, 'Mount')


button1 = QtBind.createButton(gui, 'button_clicked', ' Mount ', 10, 10)


def button_clicked():
	mount() 

def mount():
	pets = get_pets()
	if pets:
		for uid,pet in pets.items():
			if pet['type'] == "transport":
				p = b'\x01'
				p += struct.pack('I',uid)
				log('Mounting... ;)')
				inject_joymax(0x70CB,p, False)




def teleported():
	Timer(1.0, mount, ()).start()


log('[%s] Loaded' % __name__)