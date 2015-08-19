# -*- coding: utf-8 -*-

import core.controller
from modules import Module, EventManager
import time, os, logging, sqlite3

log_dir = '/var/log/piserver'
if not os.path.isdir(log_dir): os.mkdir(log_dir)
logging.basicConfig(filename=log_dir+'/piserver.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.getLogger("sqlite3").setLevel(logging.WARNING)

# Tableau des modules (classe) dispo (pour eviter le parsage du document lors du chargement dynamique des modules)
MODULES = ['Sensors']

def log(value):
	print(value)
	logging.debug(value)

class Sensors(Module):
	"""Class 'Sensors' (DHT11, BH1750) via ATMega368"""

	def __init__(self, conf):
		self._init_db()
		cmds = { 'temp': None, 'humidity': None, 'light': None, 'all': None }
		#self.hum = self.temp = self.lux = 0
		super().__init__(conf, cmds)
		EventManager.addEvent(sensors = [self._parseMessage])
		EventManager.send(3)

	def _init_db(self):
		conn = sqlite3.connect(core.controller.Controller.DB_NAME)
		cur = conn.cursor()
		if core.controller.Controller.DEBUG:
			cur.execute("DROP TABLE IF EXISTS sensors")
		cur.execute("CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, type TEXT NOT NULL, value REAL NOT NULL)")
		conn.commit()

	def _parseMessage(self, result):
		#print("Sensors::_parseMessage")
		result = list(map(float, result))
		self._check_value('lux', result[0])
		self._check_value('temp', result[1])
		self._check_value('hum', result[2])

	def _check_value(self, type, value):
		old = self._read_value(type)
		#log("Sensors::read " + type + ": old = " + str(old) + ", new = " + str(value))
		if old != value:
			self._save_value(type, value)

	def _read_value(self, type):
		value = 0
		try:
			conn = sqlite3.connect(core.controller.Controller.DB_NAME)
			cur = conn.cursor()
			qry = 'SELECT value FROM sensors WHERE type="'+str(type)+'" ORDER BY time DESC LIMIT 1'
			#print(qry)
			cur.execute(qry)
			rc = cur.fetchone()
			if rc != None: value = rc[0]
			cur.close()
			conn.close()
		except sqlite3.Error as e:
			print ("An error occurred:" + str(e.args[0]))
		return value

	def _save_value(self, type, value):
		try:
			conn = sqlite3.connect(core.controller.Controller.DB_NAME)
			cur = conn.cursor()
			qry = 'INSERT INTO sensors (type, value) VALUES ("'+type+'", '+str(value)+')'
			#print(qry)
			cur.execute(qry)
			#log("Sensors::saved " + type + " = " + str(value))
			conn.commit()
			cur.close()
			conn.close()
		except sqlite3.Error as e:
			print ("An error occurred:" + str(e.args[0]))

	def execute(self, cmd):
		log("Sensors::execute: " + cmd)
		if self._read_value('temp') == 0 or self._read_value('lux') == 0:
			self.controller.atmega.send(3, True)
		result = dict(success=True, name=self.name)
		if cmd == 'temp' or cmd == 'all':
			result['temp'] = self._read_value('temp')
			result['humidity'] = self._read_value('hum')
		if cmd == 'lux' or cmd == 'all':
			result['lux'] = self._read_value('lux')
		return result

	def eval_rule(self, prop, condition, value):
		# print("eval_rule", self.module_name, prop, condition, value)
		if prop in ['temp', 'hum', 'lux']:
			return eval(str(self._read_value(prop)) + " " + condition + " " + str(value))
		return False
