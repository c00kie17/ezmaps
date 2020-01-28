import sys
import json
import os
from PIL import Image,ImageDraw,ImageOps
from ezmaps.overpass import overpassManager
import operator
from functools import reduce
from json.decoder import JSONDecodeError
from ezmaps.util import *
import pickle

highwayKeys = ['motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','service','residential']

class mapObj():

	def __init__(self,data,filename):
		self.filename = filename
		self.scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
		self.data = data
		self.scaleValue = 1000000
		self.maxScale = 10000
		if isinstance(self.data['details']['size'],int):
			self.maxScale = self.data['details']['size']
		print('Loaded Locations')

	def get_place(self):
		query = 'area["name:en"="'+self.data['details']['place'].title()+'"]["admin_level"='+str(self.data['details']['level'])+'];out geom;'
		query += 'area["name"="'+self.data['details']['place'].title()+'"]["admin_level"='+str(self.data['details']['level'])+'];out geom;'
		children = overpassManager.request_overpass(query)
		options = self.get_options(children)
		if len(options) > 1:
			count = 1
			for option in options:
				print_option(str(count)+'. '+option['tags']['name']+','+option['tags']['wikipedia'])
				count += 1
			answer = input('Please enter the number for your option: ')
			if answer.isnumeric() and (int(answer)) < len(options):
				self.map = options[int(answer)-1]
			else:
				exit_error('Invalid input: '+str(answer))
		else:
			self.map = options[0]

	def get_options(self,results):
		options = []
		codes = []
		if results:
			results = results['elements']
			options = []
			for result in results:
				childTags = result['tags']
				if all(x in childTags.keys() for x in ['name', 'wikipedia', 'wikidata']):
					if childTags['wikidata'] not in codes:
						options.append(result)
						codes.append(childTags['wikidata'])
		else:
			exit_error('No place '+self.data['details']['place'].title()+' found')

		if len(options) > 0:
			return options
		else:
			exit_error('No place '+self.data['details']['place'].title()+' found')


	def fetch_bounds(self):
		query ='area('+str(self.map['id'])+');(rel(area)[name="'+self.map['tags']['name']+'"];);(._;>;);out geom;'
		bounds = overpassManager.request_overpass(query)
		self.bounds = self.get_element(bounds,['type'],'way')


	def get_element(self,obj,key,value):
		elementArray = []
		for element in obj['elements']:
			try:
				if reduce(operator.getitem,key,element) == value:
					elementArray.append(element)
			except KeyError:
				pass
		return elementArray

	def get_data(self,name):
		query = 'area[name="'+name+'"][type="boundary"];out geom;'
		data = overpassManager.request_overpass(query)
		try:
			data = data['elements'][0]
		except (KeyError,IndexError,TypeError):
			exit_error(name+' doesnt exist')
		return data

	def load_child_roads(self):
		detail = self.data['details']['detail']
		if detail*2 > len(highwayKeys) or detail == 0:
			exit_error('detialed value not valid')
		query = 'area('+str(self.map['id'])+')->.searchArea;('
		for i in range(0,(self.data['details']['detail']*2)):
			query += 'way["highway"='+highwayKeys[i]+'](area.searchArea);'
		query += ');(._;>;);out geom;'
		roads = overpassManager.request_overpass_stream(query,'roads')
		self.roads = self.get_element(roads,["type"],"way")
		self.roads = [road['geometry']for road in self.roads] + [road['geometry'] for road in self.bounds]

	def get_map_boundies(self):
		allLat = [item['lat'] for sublist in self.roads for item in sublist]
		allLon = [item['lon'] for sublist in self.roads for item in sublist]
		self.boundry = {
			"minlat":min(allLat),
			"maxlat":max(allLat),
			"minlon":min(allLon),
			"maxlon":max(allLon)
		}

	def save_state(self,path):
		state = {
			"data":self.data,
			"map":self.map,
			"roads":self.roads,
			"bounds":self.bounds
		}
		with open(os.path.join(path,self.filename+'.pickle'), 'wb') as handle:
			pickle.dump(state,handle,protocol=pickle.HIGHEST_PROTOCOL)

	def load_state(self,path):
		with open(path, 'rb') as handle:
			state = pickle.load(handle)
			if self.data['details']['place'] == state['data']['details']['place'] and self.data['details']['level'] == state['data']['details']['level']:
				self.map = state['map']
				self.roads = state['roads']
				self.bounds = state['bounds']
			else:
				exit_error('Config and State do not match')

	def set_scale(self):
		done = True
		while done:
			temp = {}
			for key,value in self.boundry.items():
				temp[key] = int(value*self.scaleValue)
			height = temp['maxlat'] - temp['minlat']
			width = temp['maxlon'] - temp['minlon']
			if width > self.maxScale or height > self.maxScale:
				self.scaleValue = self.scaleValue/10
			else:
				self.boundry = temp
				done = False

	def normalize(self):
		for roadList in self.roads:
			for road in roadList:
				road['lat'] = abs(int(road['lat']*self.scaleValue) - self.boundry['minlat'])
				road['lon'] = abs(int(road['lon']*self.scaleValue) - self.boundry['minlon'])

		self.normBoundry = {}
		self.normBoundry['maxlat'] = (self.boundry['maxlat'] - self.boundry['minlat']) + 10
		self.normBoundry['maxlon'] = (self.boundry['maxlon'] - self.boundry['minlon']) + 10
		self.normBoundry['minlat'] = 0
		self.normBoundry['minlon'] = 0

	def create_img(self):
		width = self.normBoundry['maxlon']
		height = self.normBoundry['maxlat']
		if self.data['details']['background'] == -1:
			self.img = Image.new('RGB', (width,height), (255, 255, 255))
			self.convert_transparent()
		elif self:
			self.img = Image.new('RGB', (width,height), tuple(self.data['details']['background']))

	def convert_transparent(self):
		self.img = self.img.convert("RGBA")
		datas = self.img.getdata()
		newData = []
		for item in datas:
		    if item[0] == 255 and item[1] == 255 and item[2] == 255:
		        newData.append((255, 255, 255, 0))
		    else:
		        newData.append(item)
		self.img.putdata(newData)

	def save_image(self,path):
		if isinstance(self.data['details']['size'],list):
			self.img = self.img.resize((self.data['details']['size'][0],self.data['details']['size'][1]), Image.ANTIALIAS)
		self.img = ImageOps.mirror(self.img)
		self.img = self.img.rotate(180, Image.NEAREST, expand=1)
		self.img.save(os.path.join(path,self.filename+'.png'),"PNG")

	def generate(self):
		draw = ImageDraw.Draw(self.img)
		for roadList in self.roads:
			xy = [(val['lon'],val['lat']) for val in roadList]
			draw.polygon(xy, outline=tuple(self.data['details']['color']) )
		del draw
