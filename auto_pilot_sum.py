import requests
from collections import OrderedDict
from pyproj import Geod
import json

class Car():

	#получает файл сообщений, преобразует в список
	def __init__(self, url):
		_req = requests.get(url)
		self._list_reports = _req.text.split('\n')
		self._get_dict_reports()


	#преобразует полученный список сообщений в словарь и сортирует по ts
	def _get_dict_reports(self):
		self._dictionary_reports = {}			   
		for _text in self._list_reports:	
			if _text != '':
				_data = json.loads(_text)
				_key = _data["ts"]
				if "control_switch_on" in _data:														#exemple {"control_switch_on":false,"ts":1546824945154817766}		
					_value = _data["control_switch_on"]
				else:																				#exemple {"geo":{"lat":36.104064590834020976,"lon":-115.16390984327611591},"ts":1546825180350798251}
					_value = _data["geo"]
				self._dictionary_reports[_key] = _value

		#отсортирует по возрастанию ключей словаря
		self._dictionary_reports = OrderedDict(sorted(self._dictionary_reports.items(), key=lambda _t: _t[0]))

	#подсчитывает пройденное расстояние для разных режимов езды 
	def iter_reports(self):
		_distance = {'auto': 0, 'manual': 0}
		_value_old = {}
		_g = Geod(ellps='WGS84')
		_flag_control = 'manual'

		for _ts, _value in self._dictionary_reports.items():
			if type(_value) == dict:
				if _value_old == {}:
					_value_old = _value
				else:
					if abs(_value['lat'] - _value_old['lat']) < 0.01 and abs(_value['lon'] - _value_old['lon']) < 0.01:
						_, _, _dist = _g.inv(_value_old['lon'], _value_old['lat'], _value['lon'], _value['lat'])        #преобразует из lon, lat в азимуты и расстояние между точками
						_distance[_flag_control] += _dist	
						_value_old = _value
			else:
				_flag_control = 'auto' if _value else 'manual'
		print(f"Автономно: {_distance['auto']} м\nВ ручном режиме: {_distance['manual']} м")

	

if __name__ == "__main__":
	url = input('Введите URL: ')
	#url = 'https://sdcimages.s3.yandex.net/test_task/data'
	car = Car(url)
	car.iter_reports()
