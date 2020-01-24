import requests
import sys
import json
import os
from time import sleep
import pandas as pd
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

highwayKeys = ['residential','motorway','primary','trunk','secondary','tertiary','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link','service']

class mapObj():

	def __init__(self,data):
		self.data =  data
		self.queryPrepend = '[out:json][timeout:500];'
		self.overpassUrl = "http://overpass-api.de/api/interpreter"
		self.country = self.get_data(data['country'])
		self.parent = self.country
		self.child = None
		self.scaleValue = 10000
		self.check_areas()
		self.child = self.get_data(self.child['tags']['name'])
		print('Finished Loading the Family')
		

	def check_child(self,child,chidType):
		query = 'area[name='+self.parent['tags']['name']+'];(node[place='+chidType+'](area););out;'
		data = self.request_overpass(query)
		for element in data['elements']:
			if child == element['tags']['name']:		
				return element	
		return None

	def get_data(self,name):
		query = 'area[name="'+name+'"][type="boundary"];out geom;'
		data = 	self.request_overpass(query)
		try:
			data = data['elements'][0]
		except (KeyError,IndexError):
			print('doesnt exist')
			sys.exit()
			#throw error	
		return data	

	def get_boundies(self):
		self.boundry = {
			"minlat":self.roads['lat'].min(),
			"maxlat":self.roads['lat'].max(),
			"minlon":self.roads['lon'].min(),
			"maxlon":self.roads['lon'].max()
		}

	def check_areas(self):
		state = self.check_state()
		city = self.check_city()
		if not state and not city:
			self.child = self.country

	def check_state(self):
		try:
			self.state = self.check_child(self.data['state'],'state')			
		except KeyError:
			return None

		if self.state:
			self.parent = self.state
			return True
		else:	
			print('no state')
			sys.exit()
	
	def check_city(self):
		try:
			self.city = self.check_child(self.data['city'],'city')	
		except KeyError:
			self.parent = self.country
			self.child = self.state
			return	None	
		if self.city:
			self.child = self.city
			return True		
		else:
			print('no city')
			sys.exit()
			#throw error message
		
	def save_roads(self,data):
		with open('temp.json', 'w') as f:
			json.dump(data, f)

	def load_roads(self):
		if os.path.isfile('./temp.json'): 
			f = open('./temp.json','r')
			return json.loads(f.read())
		else:
			return None	

	def load_child_roads(self):
		query = 'area[name='+self.child['tags']['name']+']->.searchArea;('
		for key in highwayKeys:
			query += 'way["highway"='+key+'](area.searchArea);'
		query += ');(._;>;);out geom;'
		roads = self.load_roads()
		if not roads:
			roads = self.request_overpass_stream(query)
		self.save_roads(roads)
		self.roads = self.parse_roads(roads)
		
	def normalize(self):
		for key,value in self.boundry.items():
			self.boundry[key] = int(value*self.scaleValue)
		self.roads = self.roads*self.scaleValue
		self.roads = self.roads.astype('int32')
		self.roads['lat'] = self.roads['lat'] - self.boundry['minlat']
		self.roads['lon'] = self.roads['lon'] - self.boundry['minlon']

		self.normBoundry = self.boundry	
		self.normBoundry['maxlat'] = (self.boundry['maxlat'] - self.boundry['minlat']) + 10
		self.normBoundry['maxlon'] = (self.boundry['maxlon'] - self.boundry['minlon']) + 10
		self.normBoundry['minlat'] = 0
		self.normBoundry['minlon'] = 0	

	def delete_temp(self):
		os.remove('./temp.json')		

	def parse_roads(self,roads):
		roadArray = []
		for geo in roads['elements']:
			if geo['type'] == "way":
				roadArray += geo['geometry']
		return pd.DataFrame(roadArray)		

	def create_img(self):
		width = self.normBoundry['maxlon']
		height = self.normBoundry['maxlat']
		if self.data['background'] == 0:
			self.img = np.zeros((height, width, 3), dtype=np.uint8)
		else:
			self.img = np.zeros((height, width, 3), dtype=np.uint8)
			self.img.fill(255)
			
	def save_image(self):
		im = Image.fromarray(self.img)
		im = im.resize((self.data['size'][0],self.data['size'][1]), Image.ANTIALIAS)
		im.save(os.path.join(os.getcwd(),'output.png'))

	def generate(self):
		for cord in self.roads.values.tolist():
			try:
				for i in range(0,3):
					self.img[cord[0]][cord[1]][i] = self.data['color'][i]
			except IndexError:
				pass			
		self.save_image()	

	def request_overpass_stream(self,query):
		code = None
		while code != 200:
			response = requests.get(self.overpassUrl, params={'data': self.queryPrepend+query},stream=True)
			if response.status_code != 200:
				print(response.status_code)
				print('Retrying request in 30 seconds')
				sleep(30)
				continue
			code = 	response.status_code
			resp = b''		
			count = 0
			for data in response.iter_content(chunk_size=2048):
				resp += data
				count += 2048
				sys.stdout.write('\r')
				sys.stdout.write('read '+str(round(count/1000000,2)) +'MB')
				sys.stdout.flush()
		return json.loads(resp)		

	def request_overpass(self,query):
		code = None
		while code != 200:
			response = requests.get(self.overpassUrl, params={'data': self.queryPrepend+query})
			if response.status_code != 200:
				print('Retrying request in 30 seconds')
				sleep(30)
				continue
			code = 	response.status_code		
		return response.json()	


