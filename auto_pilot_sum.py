import requests
from collections import OrderedDict
from pyproj import Geod
import json

class Car():

	#получает файл сообщений, преобразует в список
	def __init__(self, url):
		__req = requests.get(url)
		self.__list_reports = __req.text.split('\n')
		self.__get_dict_reports()


	#преобразует полученный список сообщений в словарь и сортирует по ts
	def __get_dict_reports(self):
		self.__dictionary_reports = {}			   
		for __text in self.__list_reports:	
			if __text != '':
				__data = json.loads(__text)
				__key = __data["ts"]
				if "control_switch_on" in __data:														#exemple {"control_switch_on":false,"ts":1546824945154817766}		
					__value = __data["control_switch_on"]
				else:																				#exemple {"geo":{"lat":36.104064590834020976,"lon":-115.16390984327611591},"ts":1546825180350798251}
					__value = __data["geo"]
				self.__dictionary_reports[__key] = __value

		#отсортирует по возрастанию ключей словаря
		self.__dictionary_reports = OrderedDict(sorted(self.__dictionary_reports.items(), key=lambda __t: __t[0]))

	#подсчитывает пройденное расстояние для разных режимов езды 
	def iter_reports(self):
		__distance = {'auto': 0, 'manual': 0}
		__value_old = {}
		__g = Geod(ellps='WGS84')
		__flag_control = 'manual'

		for __ts, __value in self.__dictionary_reports.items():
			if type(__value) == dict:
				if __value_old == {}:
					__value_old = __value
				else:
					if abs(__value['lat'] - __value_old['lat']) < 0.01 and abs(__value['lon'] - __value_old['lon']) < 0.01:
						_, _, __dist = __g.inv(__value_old['lon'], __value_old['lat'], __value['lon'], __value['lat'])        #преобразует из lon, lat в азимуты и расстояние между точками
						__distance[__flag_control] += __dist	
						__value_old = __value
			else:
				if __value: __flag_control = 'auto'
				else: __flag_control = 'manual'
		print(f"Автономно: {__distance['auto']}\nВ ручном режиме: {__distance['manual']}")

	

if __name__ == "__main__":
	url = input('Введите URL: ')
	#url = 'https://sdcimages.s3.yandex.net/test_task/data'
	car = Car(url)
	car.iter_reports()