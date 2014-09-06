import modules.gpio
import wiringpi2 as wpi
from threading import Thread
from time import sleep, time
import concurrent.futures
import libchacon

# Tableau des modules (classe) dispo (pour eviter le parsage du document lors du chargement dynamique des modules)
MODULES = ['Interruptor']

# Interrupteur RF (Chacom)
class Interruptor(modules.gpio.GPIOOutput):
	"""Class 'Interruptor' interrupteur RF (Chacon)"""

	def __init__(self, conf):
		self.group = 0
		self.sender = int(conf['code']['sender'])
		self.interruptor = int(conf['code']['interruptor'])
		super().__init__(conf)
		self.cmds['associate'] = None

	def execute(self, cmd):
		result = dict(success=False, name=self.name, state=self.state)
		if cmd == 'associate':
			libchacon.send(self.pin, self.sender, self.interruptor, 1)
			result['state'] = self.state
			result['success'] = True
		else:
			current = 1 if self.state else 0
			if cmd == 'toggle': new_state = current == 1 if 0 else 1
			elif cmd == 'on': new_state = 1
			elif cmd == 'off': new_state = 0
			if current != new_state:
				current = libchacon.send(self.pin, self.sender, self.interruptor, int(new_state))
				self.state = True if current == 1 else False
				result['state'] = self.state
				result['success'] = True
		return result