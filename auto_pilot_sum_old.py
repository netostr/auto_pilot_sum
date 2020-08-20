import requests
from collections import OrderedDict
import time
from pyproj import Geod
import folium
import json

#url = input('Введите URL: ')
url = 'https://sdcimages.s3.yandex.net/test_task/data'
r = requests.get(url)
l = r.text.split('\n')
d = {}
for text in l:	
	if text != '':
		data = json.loads(text)
		key = data["ts"]
		if "control_switch_on" in data:														#exemple {"control_switch_on":false,"ts":1546824945154817766}		
			value = data["control_switch_on"]
		else:																				#exemple {"geo":{"lat":36.104064590834020976,"lon":-115.16390984327611591},"ts":1546825180350798251}
			value = list(data["geo"].values())
		d[key] = value
			   
#отсортирует по возрастанию ключей словаря
e = OrderedDict(sorted(d.items(), key=lambda t: t[0]))



for i in range(1,12):
	distance = 0
	value_old = []
	g = Geod(ellps='WGS84')
	a = 0
	for key, val in e.items():
		t = time.ctime(key//1000000000)
		if type(val) == list:
			value = [round(x,i) for x in val]
			if value_old == []:
				value_old = value
				map = folium.Map(location=value, zoom_start =20)
				#print(key, value, t, value[0]-value_old[0], value[1]-value_old[1])
			else:
				if abs(value[0] - value_old[0]) < 0.01 or abs(value[1] - value_old[1]) < 0.01:
					a += 1
					if a % 100 == 0:
						folium.Marker(location=value, icon=folium.Icon(color = 'gray')).add_to(map)
					az12,az21,dist = g.inv(value_old[1],value_old[0],value[1],value[0])
					distance += dist	
					value_old = value
			
			
				#print(key, value, t, value[0]-value_old[0], value[1]-value_old[1], dist)
	map.save("map1.html")
	print(i,distance)
	

