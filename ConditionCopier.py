from phBot import *
import QtBind
import json
import os

name = 'ConditionCopier'
version = 1.1
path = get_config_dir()

gui = QtBind.init(__name__, name)

lblCharName = QtBind.createLabel(gui,'Character Name',85,20)
lblCharFrom = QtBind.createLabel(gui,'Copy From',20,50)
txtCharFrom = QtBind.createLineEdit(gui,"",75,48,120,20)
lblCharTo = QtBind.createLabel(gui,'Copy To',20,80)
txtCharTo = QtBind.createLineEdit(gui,"",75,78,120,20)

lblServerName = QtBind.createLabel(gui,'Server Name',240,20)
txtServerFrom = QtBind.createLineEdit(gui,"",220,48,120,20)
txtServerTo = QtBind.createLineEdit(gui,"",220,78,120,20)


lblProfileName = QtBind.createLabel(gui,'Profile Name',390,20)
txtProfileFrom = QtBind.createLineEdit(gui,"",370,48,120,20)
txtProfileTo = QtBind.createLineEdit(gui,"",370,78,120,20)

btnCopy = QtBind.createButton(gui, 'button_copy', ' Copy Conditions ', 70, 120)

def button_copy():
	FromChar = QtBind.text(gui,txtCharFrom)
	FromServer = QtBind.text(gui,txtServerFrom)
	FromProfile = QtBind.text(gui,txtProfileFrom)
	if FromChar == '':
		log('Plugin: Please Enter a FROM Character Name')
		return
	if FromServer == '':
		log('Plugin: Please Enter a FROM Server Name')
		return
	FromFile = "%s_%s.json" %(FromServer,FromChar)
	if len(FromProfile) > 0:
		FromFile = "%s_%s.%s.json" %(FromServer,FromChar,FromProfile)
	if os.path.exists(path + FromFile):
		with open(path + FromFile,"r", encoding = "utf-8") as f:
			Fromdata = json.load(f)
			FromConditions = Fromdata['Conditions']
	else:
		log('Plugin: FROM Config file doesnt exist')
		return

	ToChar = QtBind.text(gui,txtCharTo)
	ToServer = QtBind.text(gui,txtServerTo)
	ToProfile = QtBind.text(gui,txtProfileTo)
	if ToChar == '':
		log('Plugin: Please Enter a TO Character Name')
		return
	if ToServer == '':
		log('Plugin: Please Enter a TO Server Name')
		return
	ToFile = "%s_%s.json" %(ToServer,ToChar)
	if len(ToProfile) > 0:
		ToFile = "%s_%s.%s.json" %(ToServer,ToChar,ToProfile)
	if os.path.exists(path + ToFile):
		with open(path + ToFile,"r", encoding = "utf-8") as f:
			Todata = json.load(f)
			Todata['Conditions'] = FromConditions
	else:
		log('Plugin: TO Config file doesnt exist')
		return
	log(str(FromConditions))
	with open(path + ToFile ,"w", encoding = "utf-8") as f:
		f.write(json.dumps(Todata, indent=4,))
		log('Plugins: Conditions Successfully copied from [%s] to [%s]' %(FromFile,ToFile))		



log('Plugin: [%s] Version %s Loaded' % (name,version))
