from phBot import *
import QtBind
from threading import Timer
import struct
import json
import os
import urllib.request
import random
from operator import add, sub

name = 'Battle of Infinity'
version = 1.10
NewestVersion = 0
path = get_config_dir() + name + "\\"

Started = False
Registering = False
Attacking = False
Picking = False
WaitingforParty = False
Inside = False
SkillDelay = 500
RegDelay = 4000
DelayCounter = 0
ChangeAreaAttempts = 0
MoveAttempts = 0
GettingMorph = False
Backup = None
UnstuckAfter = 3.0
AttackAttempts = 0

SoloCount = 0
PartyCount = 0

CastSkills = []
ActiveSkills = []
MorphID = 0

gui = QtBind.init(__name__, name)

lbl = QtBind.createLabel(gui,'Attack Radius ',400,20)
txtRadius = QtBind.createLineEdit(gui,"40",470,15,25,20)
  
lbl = QtBind.createLabel(gui,'Wait for           party members to enter before starting',400,40)
lbl = QtBind.createLabel(gui,'*Dont include this char',600,50)
txtPartyMembers = QtBind.createLineEdit(gui,"1",442,35,25,20)

cbxChange = QtBind.createCheckBox(gui, 'cbxChange_clicked','Change to party mode when solo is complete', 400, 70)
lbl = QtBind.createLabel(gui,'Party mode profile ',430,90)
txtPartyProfile = QtBind.createLineEdit(gui,"",520,88,90,20)

cbxFinished = QtBind.createCheckBox(gui, 'cbxFinished_clicked','Return and start bot when finished', 400, 110)
lbl = QtBind.createLabel(gui,'Training profile ',430,130)
txtFinishedProfile = QtBind.createLineEdit(gui,"",520,128,90,20)
cbxTerminate = QtBind.createCheckBox(gui, 'cbxTerminate_clicked','Terminate Bot when finished', 400, 150)
cbxUseHighSkills = QtBind.createCheckBox(gui, 'cbxUseHighSkills_','Always Use Highest Skills', 400, 180)
cbxRandomTarget = QtBind.createCheckBox(gui, 'cbxRandomTarget_','Select Random Target', 400, 210)

lbl = QtBind.createLabel(gui,'Current Stage: ',10,250)
lblStage = QtBind.createLabel(gui,'0',85,250)

cbxSolo71to80 = QtBind.createCheckBox(gui, 'cbxSolo71to80_clicked','Solo Level (71-80)', 10, 20)
cbxPT71to80 = QtBind.createCheckBox(gui, 'cbxPT71to80_clicked','Party Level (71-80)', 10, 40)
cbxYeoha = QtBind.createCheckBox(gui, 'cbxYeoha_clicked','Yeoha (A)', 140, 30)
cbxSeiren = QtBind.createCheckBox(gui, 'cbxSeiren_clicked','Seiren (B)', 250, 30)

cbxSolo81to90 = QtBind.createCheckBox(gui, 'cbxSolo81to90_clicked','Solo Level (81-90)', 10, 70)
cbxPT81to90 = QtBind.createCheckBox(gui, 'cbxPT81to90_clicked','Party Level (81-90)', 10, 90)
cbxNiyaShaman = QtBind.createCheckBox(gui, 'cbxNiyaShaman_clicked','Niya Shaman (A)', 140, 80)
cbxSlaveWatcher = QtBind.createCheckBox(gui, 'cbxSlaveWatcher_clicked','Slave Watcher (B)', 250, 80)

cbxSolo91to100 = QtBind.createCheckBox(gui, 'cbxSolo91to100_clicked','Solo Level (91-100)', 10, 120)
cbxPT91to100 = QtBind.createCheckBox(gui, 'cbxPT91to100_clicked','Party Level (91-100)', 10, 140)
cbxDemonShaitan = QtBind.createCheckBox(gui, 'cbxDemonShaitan_clicked','Demon Shaitan (A)', 140, 130)
cbxImhotep = QtBind.createCheckBox(gui, 'cbxImhotep_clicked','Imhotep (B)', 250, 130)

cbxSolo101to110 = QtBind.createCheckBox(gui, 'cbxSolo101to110_clicked','Solo Level (101-110)', 10, 170)
cbxPT101to110 = QtBind.createCheckBox(gui, 'cbxPT101to110_clicked','Party Level (101-110)', 10, 190)
cbxNephthys = QtBind.createCheckBox(gui, 'cbxNephthys_clicked','Nephthys (A)', 140, 180)
cbxTombSnakeLady = QtBind.createCheckBox(gui, 'cbxTombSnakeLady_clicked','Tomb Snake Lady (B)', 250, 180)

buttonStartStop = QtBind.createButton(gui, 'button_start', '  Start  ', 25, 220)

RegCheckBoxes = [cbxSolo71to80,cbxPT71to80,cbxSolo81to90,cbxPT81to90,cbxSolo91to100,cbxPT91to100,cbxSolo101to110,cbxPT101to110]
MorphCheckBoxes = [cbxYeoha,cbxSeiren,cbxNiyaShaman,cbxSlaveWatcher,cbxDemonShaitan,cbxImhotep,cbxNephthys,cbxTombSnakeLady]

#type checkboxes
def cbxSolo71to80_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxYeoha,cbxSeiren)
		ClearGUI('Reg',cbxSolo71to80)
def cbxPT71to80_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxYeoha,cbxSeiren)
		ClearGUI('Reg',cbxPT71to80)
def cbxSolo81to90_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxNiyaShaman,cbxSlaveWatcher)
		ClearGUI('Reg',cbxSolo81to90)
def cbxPT81to90_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxNiyaShaman,cbxSlaveWatcher)
		ClearGUI('Reg',cbxPT81to90)
def cbxSolo91to100_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxDemonShaitan,cbxImhotep)
		ClearGUI('Reg',cbxSolo91to100)
def cbxPT91to100_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxDemonShaitan,cbxImhotep)
		ClearGUI('Reg',cbxPT91to100)
def cbxSolo101to110_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxNephthys,cbxTombSnakeLady)
		ClearGUI('Reg',cbxSolo101to110)
def cbxPT101to110_clicked(checked):
	if checked:
		ClearGUI('Morph',cbxNephthys,cbxTombSnakeLady)
		ClearGUI('Reg',cbxPT101to110)

#morph checkboxes...tard proof?
def cbxYeoha_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxPT71to80):
		if checked:
			ClearGUI('Morph',cbxYeoha)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxYeoha,False)
def cbxSeiren_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxPT71to80):
		if checked:
			ClearGUI('Morph',cbxSeiren)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxSeiren,False)
def cbxNiyaShaman_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxPT81to90):
		if checked:
			ClearGUI('Morph',cbxNiyaShaman)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxNiyaShaman,False)
def cbxSlaveWatcher_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxPT81to90):
		if checked:
			ClearGUI('Morph',cbxSlaveWatcher)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxSlaveWatcher,False)
def cbxDemonShaitan_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxPT91to100):
		if checked:
			ClearGUI('Morph',cbxDemonShaitan)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxDemonShaitan,False)
def cbxImhotep_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxPT91to100):
		if checked:
			ClearGUI('Morph',cbxImhotep)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxImhotep,False)
def cbxNephthys_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo101to110) or QtBind.isChecked(gui,cbxPT101to110):
		if checked:
			ClearGUI('Morph',cbxNephthys)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxNephthys,False)
def cbxTombSnakeLady_clicked(checked):
	if QtBind.isChecked(gui,cbxSolo101to110) or QtBind.isChecked(gui,cbxPT101to110):
		if checked:
			ClearGUI('Morph',cbxTombSnakeLady)
	else:
		log('Plugin: Wrong Selection!')
		QtBind.setChecked(gui,cbxTombSnakeLady,False)

def cbxTerminate_clicked(checked):
	if checked:
		QtBind.setChecked(gui,cbxFinished,False)

def cbxFinished_clicked(checked):
	if checked:
		QtBind.setChecked(gui,cbxTerminate,False)

def ClearGUI(type,DontClear,DontClear2=None):
	if type == 'Reg':
		for cbx in RegCheckBoxes:
			if cbx != DontClear and cbx != DontClear2:
				QtBind.setChecked(gui,cbx,False)
	elif type == 'Morph':
		for cbx in MorphCheckBoxes:
			if cbx != DontClear and cbx != DontClear2:
				QtBind.setChecked(gui,cbx,False)

def button_start():
	global Started, Registering, Attacking, WaitingforParty, Picking, Inside
	stop_bot()
	if NewestVersion > int(str(version).replace(".","")):
		log('Plugin: There is an update avaliable for [%s]!' % name)
	if Started == False:
		if OptionsSelected():
			if Online():
				SaveConfig()
			Started = True
			QtBind.setText(gui,buttonStartStop,'  Stop  ')
			if WheresWaldo():
				log('Plugin: Start the Plugin Outside!')
			else:
				Registering = True
			return
	elif Started == True:
		Started = False
		Attacking = False
		Registering = False
		WaitingforParty = False
		Picking = False
		Inside = False
		QtBind.setText(gui,buttonStartStop,'  Start  ')


def Register():
	if OptionsSelected():
		npcs = get_npcs()
		for key, npc in npcs.items():
			if npc['servername'] == r"NPC_BATTLE_ARENA_MANAGER":
				type = GetBOIType()
				packet = struct.pack('<I', key)
				packet += b'\x02'
				packet += struct.pack('<I', type)
				inject_joymax(0x705A,packet,False)
				return
		log('Plugin: You are not near the Arena Manager')
		

def BeginBattle():
	move_to(14675.0, 2592.0, 0.0)
	npcs = get_npcs()
	for key, npc in npcs.items():
		if npc['name'] == r"Dungeon Manager" or npc['name'] == r"Zindan Müdürü":
			packet = struct.pack('<I', key)
			inject_joymax(0x7045,packet,False)
			Timer(2.0, inject_joymax, [0x7588, b'\x01', False]).start()
			Timer(3.0, inject_joymax, [0x704B, packet, False]).start()
			#move to change npcs
			Timer(3.0, move_to, [14709.0, 2592.0, 0.0]).start()
			Timer(8.0, ChangetoMob, ()).start()


def ChangetoMob():
	SetSkills()
	global Attacking, GettingMorph
	if QtBind.isChecked(gui,cbxYeoha):
		type = "Yeoha Morphstone"
	elif QtBind.isChecked(gui,cbxSeiren):
		type = "Seiren Morphstone"
	elif QtBind.isChecked(gui,cbxNiyaShaman):
		type = "Niya Shaman Morphstone"
	elif QtBind.isChecked(gui,cbxSlaveWatcher):
		type = "Slave Watcher Morphstone"
	elif QtBind.isChecked(gui,cbxDemonShaitan):
		type = "Demon Shaitan Morphstone"
	elif QtBind.isChecked(gui,cbxImhotep):
		type = "Imhotep Morphstone"
	elif QtBind.isChecked(gui,cbxNephthys):
		type = "Nephthys Morphstone"
	elif QtBind.isChecked(gui,cbxTombSnakeLady):
		type = "Tomb Snake Lady Morphstone"
	npcs = get_npcs()
	for key, npc in npcs.items():
		if npc['name'] == type:
			GettingMorph = True
			packet = b'\x03'
			packet += struct.pack('<I', key)
			inject_joymax(0x7588,packet,False)
			#move to attack area
			Timer(1.0, move_to, [14730.0, 2587.0, 0.0]).start()
			Timer(5.0, move_to, [14737.0, 2593.0, 0.0]).start()
			Timer(6.0, StartAttack, ()).start()

def StartAttack():
	global Attacking
	Attacking = True

def StartReg():
	global Registering
	Registering = True

def SetSkills():
	global CastSkills
	if QtBind.isChecked(gui,cbxUseHighSkills):
		CastSkills = [34605,34604]
	elif QtBind.isChecked(gui,cbxSolo71to80):
		if QtBind.isChecked(gui,cbxYeoha):
			CastSkills = [34575,34574]
		elif QtBind.isChecked(gui,cbxSeiren):
			CastSkills = [34577,34576]
	elif QtBind.isChecked(gui,cbxPT71to80):
		if QtBind.isChecked(gui,cbxYeoha):
			CastSkills = [34583,34582]
		elif QtBind.isChecked(gui,cbxSeiren):
			CastSkills = [34585,34584]

	elif QtBind.isChecked(gui,cbxSolo81to90):
		if QtBind.isChecked(gui,cbxNiyaShaman):
			CastSkills = [34579,34578]
		elif QtBind.isChecked(gui,cbxSlaveWatcher):
			CastSkills = [34581,34580]
	elif QtBind.isChecked(gui,cbxPT81to90):
		if QtBind.isChecked(gui,cbxNiyaShaman):
			CastSkills = [34587,34586]
		elif QtBind.isChecked(gui,cbxSlaveWatcher):
			CastSkills = [34589,34588]

	elif QtBind.isChecked(gui,cbxSolo91to100):
		if QtBind.isChecked(gui,cbxDemonShaitan):
			CastSkills = [34591,34590]
		elif QtBind.isChecked(gui,cbxImhotep):
			CastSkills = [34593,34592]
	elif QtBind.isChecked(gui,cbxPT91to100):
		if QtBind.isChecked(gui,cbxDemonShaitan):
			CastSkills = [34599,34598]
		elif QtBind.isChecked(gui,cbxImhotep):
			CastSkills = [34601,34600]

	elif QtBind.isChecked(gui,cbxSolo101to110):
		if QtBind.isChecked(gui,cbxNephthys):
			CastSkills = [34595,34594]
		elif QtBind.isChecked(gui,cbxTombSnakeLady):
			CastSkills = [34597,34596]
	elif QtBind.isChecked(gui,cbxPT101to110):
		if QtBind.isChecked(gui,cbxNephthys):
			CastSkills = [34603,34602]
		elif QtBind.isChecked(gui,cbxTombSnakeLady):
			CastSkills = [34605,34604]

def GetBOIType():
	if QtBind.isChecked(gui,cbxSolo71to80):
		return 228
	elif QtBind.isChecked(gui,cbxSolo81to90):
		return 229
	elif QtBind.isChecked(gui,cbxSolo91to100):
		return 232
	elif QtBind.isChecked(gui,cbxSolo101to110):
		return 233
	elif QtBind.isChecked(gui,cbxPT71to80):
		return 230
	elif QtBind.isChecked(gui,cbxPT81to90):
		return 231
	elif QtBind.isChecked(gui,cbxPT91to100):
		return 234
	elif QtBind.isChecked(gui,cbxPT101to110):
		return 235

def AttackMob(Skill,MobID):
	if MobID > 0:
		packet = b'\x01\x04'
		packet += struct.pack('<I',Skill)
		packet += b'\x01'
		packet += struct.pack('<I',MobID)
		inject_joymax(0x7074,packet,False)

		

def RemoveSkill(SkillID):
	if SkillID in ActiveSkills:
		ActiveSkills.remove(SkillID)

SelectedMob = 0
def UseSkill():
	global ActiveSkills, SkillDelay, Backup, AttackAttempts, SelectedMob
	if Started:
		SkillDelay = 500
		for skill in CastSkills:
			if skill not in ActiveSkills:
				MobID = GetMobID()
				if MobID == None:
					return
				SelectedMob = MobID
				if MobID > 0:
					AttackAttempts += 1
					if AttackAttempts >= 3:
						MovetoRandomPoint()
						AttackAttempts = 0
						Backup.cancel()
					AttackMob(skill,MobID)
					#skill cooldown minus alittle
					SkillDelay = 3000
					#for your viewing pleasure
					SelectMob(MobID)
					Backup = Timer(UnstuckAfter, UseSkill)
					Backup.start()
					return

def SelectMob(targetID):
	packet = struct.pack('<I',targetID)
	inject_joymax(0x7045,packet,False)

def GetMobID():
	global MoveAttempts
	MobIDs = []
	AttackRadius = int(QtBind.text(gui,txtRadius))
	Mobs = get_monsters()
	if Mobs:
		for key, mob in Mobs.items():
			dist = CalcRadiusFromME(mob['x'],mob['y'])
			if dist < AttackRadius:
				if QtBind.isChecked(gui,cbxRandomTarget):
					MobIDs.append(key)
				else:
					return key
			else:
				if QtBind.isChecked(gui,cbxRandomTarget):
					continue
				else:
					return 0
		if QtBind.isChecked(gui,cbxRandomTarget):
			if SelectedMob in MobIDs:
				return SelectedMob
			return random.choice(MobIDs) if MobIDs else None
			
	elif not AtAttackArea():
		#move back to center
		if MoveAttempts <= 5:
			MoveAttempts += 1
			move_to(14737.0, 2593.0, 0.0)
		else:
			MovetoRandomPoint()
	return 0

def MovetoRandomPoint():
	global MoveAttempts
	number = random.randint(1,10)
	ops = (add, sub)
	operator = random.choice(ops)
	X = operator(get_character_data()['x'], number)
	operator = random.choice(ops)
	Y = operator(get_character_data()['y'], number)
	move_to(X, Y, 0.0)
	log('Plugin: Possibly Stuck.. Moving')
	MoveAttempts = 0


def AtAttackArea():
	X = 14737.0
	Y = 2593.0
	px = get_character_data()['x']
	py = get_character_data()['y']
	if px == X and py == Y:
		return True
	else:
		return False

def MovetoPick():
	move_to(14762.0, 2592.0, 0.0)
	move_to(14762.0, 2592.0, 0.0)
	set_training_position(0, 14762.0, 2592.0, 0)
	Timer(2.0, ConfirmAreaChanged,()).start()

def ConfirmAreaChanged():
	global ChangeAreaAttempts
	training_area = get_training_area()
	Setx = training_area['x']
	Sety = training_area['y']
	if Setx == 14762.0 and Sety == 2592.0:
		start_bot()
		ChangeAreaAttempts = 0
		return True
	elif ChangeAreaAttempts < 5:
		log('Plugin: Training Area Failed to move.. Retrying')
		ChangeAreaAttempts += 1
		MovetoPick()
		return
	log('Plugin: Failed to move training area')
	ChangeAreaAttempts = 0
	start_bot()


def CalcRadiusFromME(Px,Py):
	my = get_position()
	dist = ((my['x'] - Px)**2 + (my['y'] - Py)**2)**0.5
	return dist

def WheresWaldo():
	region = get_character_data()['region']
	if region == 27091 or region == 27092:
		return True


def party_count():
	pt = get_party()
	count = 0
	if pt:
		for key, char in pt.items():
			count += 1
	return count - 1

def CheckforParty():
	global WaitingforParty
	WaitFor = int(QtBind.text(gui,txtPartyMembers))
	MembersInside = 0
	party = get_party()
	if WaitingforParty and Started:
		if party:
			for key, player in party.items():
				if player['player_id'] > 0:
					MembersInside += 1
					if MembersInside >= WaitFor:
						log('Plugin: All party members have entered.. beginning battle')
						WaitingforParty = False
						Timer(5.0, BeginBattle, ()).start()
						return
			log('Plugin: Not all party members have entered..Waiting')
			Timer(5.0, CheckforParty, ()).start()

def OptionsSelected():
	if QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxSolo101to110) or QtBind.isChecked(gui,cbxPT71to80) or QtBind.isChecked(gui,cbxPT81to90) or QtBind.isChecked(gui,cbxPT91to100) or QtBind.isChecked(gui,cbxPT101to110):
		return True
	log('Plugin: Please select all the required options')
	return False

# script command BOI,type,morph
#ex..BOI,solo,A .... BOI,party,B
def BOI(args):
	ClearGUI('Morph',None)
	ClearGUI('Reg',None)
	type = args[1]
	morph = args[2]
	lvl =  get_character_data()['level']
	if lvl >= 71 and lvl <= 80:
		if type == 'solo':
			QtBind.setChecked(gui,cbxSolo71to80,True)
		if type == 'party':
			QtBind.setChecked(gui,cbxPT71to80,True)
		if morph == 'A':
			QtBind.setChecked(gui,cbxYeoha,True)
		if morph == 'B':
			QtBind.setChecked(gui,cbxSeiren,True)
	elif lvl >= 81 and lvl <= 90:
		if type == 'solo':
			QtBind.setChecked(gui,cbxSolo81to90,True)
		if type == 'party':
			QtBind.setChecked(gui,cbxPT81to90,True)
		if morph == 'A':
			QtBind.setChecked(gui,cbxNiyaShaman,True)
		if morph == 'B':
			QtBind.setChecked(gui,cbxSlaveWatcher,True)
	elif lvl >= 91 and lvl <= 100:
		if type == 'solo':
			QtBind.setChecked(gui,cbxSolo91to100,True)
		if type == 'party':
			QtBind.setChecked(gui,cbxPT91to100,True)
		if morph == 'A':
			QtBind.setChecked(gui,cbxDemonShaitan,True)
		if morph == 'B':
			QtBind.setChecked(gui,cbxImhotep,True)
	elif lvl >= 101 and lvl <= 110:
		if type == 'solo':
			QtBind.setChecked(gui,cbxSolo101to110,True)
		if type == 'party':
			QtBind.setChecked(gui,cbxPT101to110,True)
		if morph == 'A':
			QtBind.setChecked(gui,cbxNephthys,True)
		if morph == 'B':
			QtBind.setChecked(gui,cbxTombSnakeLady,True)
	log('Plugin: Setting Battle of infinity settings')
	Timer(1.0, button_start, ()).start()
	return 0

def RemoveMorph():
	skills = get_active_skills()
	for ID, skill in skills.items():
		if skill['servername'].startswith('SKILL_MUHAN'):
			packet = b'\x01\x05'
			packet += struct.pack('<I', ID)
			packet += b'\x00'
			inject_joymax(0x7074,packet,False)
			

def ChangetoParty():
	ClearGUI('Morph',None)
	ClearGUI('Reg',None)
	lvl =  get_character_data()['level']
	profile = QtBind.text(gui,txtPartyProfile)
	if profile:
		set_profile(profile)
	if lvl >= 71 and lvl <= 80:
		QtBind.setChecked(gui,cbxPT71to80,True)
		QtBind.setChecked(gui,cbxYeoha,True)
	elif lvl >= 81 and lvl <= 90:
		QtBind.setChecked(gui,cbxPT81to90,True)
		QtBind.setChecked(gui,cbxNiyaShaman,True)
	elif lvl >= 91 and lvl <= 100:
		QtBind.setChecked(gui,cbxPT91to100,True)
		QtBind.setChecked(gui,cbxDemonShaitan,True)
	elif lvl >= 101 and lvl <= 110:
		QtBind.setChecked(gui,cbxPT101to110,True)
		QtBind.setChecked(gui,cbxNephthys,True)


def ReturntoTraining():
	global Started, Registering, Attacking, WaitingforParty, Picking, PartyCount, SoloCount, Inside
	if QtBind.isChecked(gui,cbxFinished):
		log('Plugin: Returning to training area')
		ClearGUI('Morph',None)
		ClearGUI('Reg',None)
		Started = False
		Attacking = False
		Registering = False
		WaitingforParty = False
		Picking = False
		Inside = False
		PartyCount = 0
		SoloCount = 0
		QtBind.setText(gui,buttonStartStop,'  Start  ')
		profile = QtBind.text(gui,txtFinishedProfile)
		if profile:
			set_profile(profile)
		Timer(1.0, use_return_scroll, ()).start()
		Timer(10.0, start_bot, ()).start()

#conditions
def SoloDone():
	if SoloCount >= 2:
		return True
	else:
		return False

def PartyDone():
	if PartyCount >= 2:
		return True
	else:
		return False



def teleported():
	global Registering, Attacking, Picking, WaitingforParty, SoloCount, PartyCount, Inside
	if Started:
		if Registering:
			if QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxSolo101to110):
				SoloCount += 1
				PartyCount = 0
			if QtBind.isChecked(gui,cbxPT71to80) or QtBind.isChecked(gui,cbxPT81to90) or QtBind.isChecked(gui,cbxPT91to100) or QtBind.isChecked(gui,cbxPT101to110):
				PartyCount += 1
				SoloCount = 0
			Registering = False
			Inside = True
			log('Plugin: Successfully Entered the Battle')
			if not get_party():
				Timer(5.0, BeginBattle, ()).start()
			else:
				WaitingforParty = True
				log('Plugin: Waiting for Party Members to Enter')
				Timer(8.0, CheckforParty, ()).start()
		#failed
		elif Attacking:
			Inside = False
			if PartyCount >= 2:
				Timer(0.1, ReturntoTraining, ()).start()
			Attacking = False
			Timer(5.0, StartReg, ()).start()
			QtBind.setText(gui,lblStage,'0')
		#successful
		elif Picking:
			if PartyCount >= 2:
				Timer(0.1, ReturntoTraining, ()).start()
			Timer(5.0, StartReg, ()).start()
			Picking = False
			Inside = False
			stop_bot()
			QtBind.setText(gui,lblStage,'0')
			log('Plugin: Battle of Infinity loop finished')
		#party didnt enter
		elif WaitingforParty:
			if PartyCount >= 2:
				Timer(0.1, ReturntoTraining, ()).start()
			log('Plugin: Party member didnt enter in time')
			WaitingforParty = False
			Timer(5.0, StartReg, ()).start()
			Inside = False
			QtBind.setText(gui,lblStage,'0')

def event_loop():
	global DelayCounter
	if Started and Attacking:
		DelayCounter += 500
		if DelayCounter >= SkillDelay:
			DelayCounter = 0
			UseSkill()
			return
	if Started and Registering:
		DelayCounter += 500
		if DelayCounter >= RegDelay:
			DelayCounter = 0
			if QtBind.isChecked(gui,cbxPT71to80) or QtBind.isChecked(gui,cbxPT81to90)  or QtBind.isChecked(gui,cbxPT91to100) or QtBind.isChecked(gui,cbxPT101to110):
				partycount = party_count()
				WaitFor = int(QtBind.text(gui,txtPartyMembers))
				if partycount >= WaitFor:
					Register()
				else:
					log('Plugin: Waiting for Party Members before registering')
			else:
				Register()


def handle_joymax(opcode, data):
	global Attacking, Picking, GettingMorph, Backup, AttackAttempts
	if opcode == 0xB05A and Registering:
		if data[0] == 2 and data[2] == 28:
			response = data[1]
			if response == 60:
				log('Plugin: You cannot re-enter the Dungeon yet!')	
			elif response == 42:
				log('Plugin: You are not in a Party!')
			elif response == 44:
				log('Plugin: You are not the required level to enter!')
			elif response == 39:
				log("Plugin: You've entered too many times!")
				#for solo only
				if not QtBind.isChecked(gui,cbxChange) and QtBind.isChecked(gui,cbxFinished):
					ReturntoTraining()
				elif QtBind.isChecked(gui,cbxChange) and QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxSolo101to110):
					ChangetoParty()
				elif QtBind.isChecked(gui,cbxFinished) and QtBind.isChecked(gui,cbxPT71to80) or QtBind.isChecked(gui,cbxPT81to90)  or QtBind.isChecked(gui,cbxPT91to100) or QtBind.isChecked(gui,cbxPT101to110):
					ReturntoTraining()
				elif QtBind.isChecked(gui,cbxTerminate):
					Terminate()
			elif response == 40:
				log("Plugin: The Party Master must enter first!")
				if PartyCount >= 2:
					if QtBind.isChecked(gui,cbxTerminate):
						Terminate()
					elif QtBind.isChecked(gui,cbxFinished):
						ReturntoTraining()
			elif response == 66:
				log("Plugin: You cannot be in a party to enter solo")
				if QtBind.isChecked(gui,cbxSolo71to80) or QtBind.isChecked(gui,cbxSolo81to90) or QtBind.isChecked(gui,cbxSolo91to100) or QtBind.isChecked(gui,cbxSolo101to110):
					#leave party
					inject_joymax(0x7061,b'',False)
					log('Plugin: Leaving Party')


	#Skill added...maybe not perfect
	elif opcode == 0xB0BD and Inside and not Picking:
		global MorphID
		if GettingMorph:
			SelfID = get_character_data()['player_id']
			packetIndex = 0
			PlayerID  = struct.unpack_from("<I",data,packetIndex)[0]
			if SelfID == PlayerID:
				packetIndex = 8
				MorphID = struct.unpack_from("<I",data,packetIndex)[0]
				GettingMorph = False
	#Skill removed
	elif opcode == 0xB072 and Inside and not Picking:
		packetIndex = 1
		SkillID  = struct.unpack_from("<I",data,packetIndex)[0]
		if SkillID == MorphID:
			log('Plugin: Morph lost.. Morphing Again')
			Attacking = False
			Timer(1.0, move_to, [14709.0, 2592.0, 0.0]).start()
			Timer(3.0, ChangetoMob, ()).start()	
	#died
	elif opcode == 0x3011 and Attacking:
		p = b'\x81' 
		inject_joymax(0x3053,p,True)
		Attacking = False
		Timer(3.0, move_to, [14709.0, 2592.0, 0.0]).start()
		Timer(7.0, ChangetoMob, ()).start()
	#stage
	elif opcode == 0x3592 and Inside:
		if data[0] == 255 and data[1] == 65:
			stage = int(data[2])
			if stage:
				QtBind.setText(gui,lblStage,str(stage))
		elif data[0] == 255 and data[1] == 66:
			if data[2] == 1:
				QtBind.setText(gui,lblStage,'Finished')
				Attacking = False
				Picking = True
				RemoveMorph()
				MovetoPick()
				
	#skill logging
	elif opcode == 0xB070 and Attacking:
		if data[1] == 2:
			packetIndex = 3
			Skill  = struct.unpack_from("H",data,packetIndex)[0]
			packetIndex = 7
			AttackerID  = struct.unpack_from("<I",data,packetIndex)[0]
			SelfID = get_character_data()['player_id']
			if AttackerID == SelfID:
				ActiveSkills.append(Skill)
				Backup.cancel()
				AttackAttempts = 0
				CoolDown = 5
				Timer(CoolDown,RemoveSkill,[Skill]).start()
				


	return True


def Online():
	if get_character_data()['player_id'] > 0:
		return True
	else:
		return False

def joined_game():
	Timer(4.0, loadDefaults, ()).start()


def GetConfig():
	return path + get_character_data()['server'] + "_" + get_character_data()['name'] + ".json"

def SaveConfig():
	data = {}
	data["AttackRadius"] = int(QtBind.text(gui,txtRadius))
	data["PartyAmount"] = int(QtBind.text(gui,txtPartyMembers))
	data["PartyMode"] = QtBind.isChecked(gui,cbxChange)
	data["PartyProfile"] = QtBind.text(gui,txtPartyProfile)
	data["Finished"] = QtBind.isChecked(gui,cbxFinished)
	data["TrainingAreaProfile"] = QtBind.text(gui,txtFinishedProfile)
	data["Terminate"] = QtBind.isChecked(gui,cbxTerminate)
	data["UseHighSkills"] = QtBind.isChecked(gui,cbxUseHighSkills)
	data["RandomTarget"] = QtBind.isChecked(gui,cbxRandomTarget)
	with open(GetConfig(),"w") as f:
		f.write(json.dumps(data, indent=4))
	log("Plugin: configs has been saved")

def LoadConfigs():
	if os.path.exists(GetConfig()):
		data = {}
		with open(GetConfig(),"r") as f:
			data = json.load(f)
		if "AttackRadius" in data:
			QtBind.setText(gui,txtRadius,str(data["AttackRadius"]))
		if "PartyAmount" in data:
			QtBind.setText(gui,txtPartyMembers,str(data["PartyAmount"]))
		if "PartyMode" in data:
			QtBind.setChecked(gui,cbxChange,data["PartyMode"])
		if "PartyProfile" in data:
			QtBind.setText(gui,txtPartyProfile,data["PartyProfile"])
		if "Finished" in data:
			QtBind.setChecked(gui,cbxFinished,data["Finished"])
		if "TrainingAreaProfile" in data:
			QtBind.setText(gui,txtFinishedProfile,data["TrainingAreaProfile"])
		if "Terminate" in data:
			QtBind.setChecked(gui,cbxTerminate,data["Terminate"])
		if "UseHighSkills" in data:
			QtBind.setChecked(gui,cbxUseHighSkills,data["UseHighSkills"])
		if "RandomTarget" in data:
			QtBind.setChecked(gui,cbxRandomTarget,data["RandomTarget"])

#reloading
def loadDefaults():
	LoadConfigs()
	lvl =  get_character_data()['level']
	if lvl >= 71 and lvl <= 80:
		QtBind.setChecked(gui,cbxSolo71to80,True)
		QtBind.setChecked(gui,cbxYeoha,True)
	elif lvl >= 81 and lvl <= 90:
		QtBind.setChecked(gui,cbxSolo81to90,True)
		QtBind.setChecked(gui,cbxNiyaShaman,True)
	elif lvl >= 91 and lvl <= 100:
		QtBind.setChecked(gui,cbxSolo91to100,True)
		QtBind.setChecked(gui,cbxDemonShaitan,True)
	elif lvl >= 101 and lvl <= 110:
		QtBind.setChecked(gui,cbxSolo101to110,True)
		QtBind.setChecked(gui,cbxNephthys,True)



def CheckForUpdate():
	global NewestVersion
	#avoid request spam
	if NewestVersion == 0:
		try:
			req = urllib.request.Request('https://raw.githubusercontent.com/Bunker141/Phbot-Plugins/master/BattleofInfinity.py', headers={'User-Agent': 'Mozilla/5.0'})
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

def Terminate():
	os.kill(os.getpid(),9)


Timer(1.0, loadDefaults, ()).start()
log('Plugin: [%s] Version %s Loaded' % (name,version))


if not os.path.exists(path):
	os.makedirs(path)
	log('Plugin: [%s] folder has been created' % name)


CheckForUpdate()
