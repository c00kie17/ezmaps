import sys
import json
import os
from PIL import Image,ImageDraw,ImageOps
from ezmaps.overpass import overpassManager
import operator
from functools import reduce
from json.decoder import JSONDecodeError
from ezmaps.util import *

highwayKeys = ['motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','service','residential']

class mapObj():

	def __init__(self,data,filename):
		self.filename = filename
		self.scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))
		self.data = data
		self.scaleValue = 1000000
		self.get_place()
		self.bounds = self.fetch_bounds()
		print('Loaded Locations')

	def get_place(self):
		query = 'area[name='+self.data['details']['place'].title()+']["admin_level"='+str(self.data['details']['level'])+'];out geom;'
		codes = []
		children = overpassManager.request_overpass(query)['elements']
		options = []
		count = 0
		if len(children) > 1:
			for child in children:
				childTags = child['tags']
				if all(x in childTags.keys() for x in ['place', 'name', 'wikipedia', 'wikidata']):
					if childTags['wikidata'] not in codes:
						print_option(str(count+1)+'.'+childTags['place'].capitalize()+':'+childTags['name']+','+childTags['wikipedia'].replace('en:',''))
						codes.append(childTags['wikidata'])
						options.append(child)
						count += 1
			value = input("Enter Digit for your Option: ")
			if value.isnumeric() or (value > len(children)):
				self.map = options[int(value)-1]
			else:
				exit_error('Wrong Input Entered')
		else:
			try:
				self.map = children[0]
			except IndexError:
				exit_error('No place '+self.data['details']['place'].title()+' found')
	#FIX
	def fetch_bounds(self):
		query ='area('+str(self.map['id'])+');(rel(area)[name="'+self.map['tags']['name']+'"];);(._;>;);out geom;'
		bounds = overpassManager.request_overpass(query)
		try:
			return self.get_element(bounds,['type'],'way')
		except TypeError:
			#FIX
			print('bounds error')
			print(bounds)
		sys.exit()

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

	def set_scale(self):
		done = True
		while done:
			temp = {}
			for key,value in self.boundry.items():
				temp[key] = int(value*self.scaleValue)
			height = temp['maxlat'] - temp['minlat']
			width = temp['maxlon'] - temp['minlon']
			if width > 10000 or height > 10000:
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
		if self.data['details']['background'] == 1:
			self.img = Image.new('RGB', (width,height), (255, 255, 255))
		elif self.data['details']['background'] == -1:
			self.img = Image.new('RGB', (width,height), (255, 255, 255))
			self.convert_transparent()
		else:
			self.img = Image.new('RGB', (width,height), (0, 0, 0))

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

	def save_image(self):
		self.img = self.img.resize((self.data['details']['size'][0],self.data['details']['size'][1]), Image.ANTIALIAS)
		self.img = ImageOps.mirror(self.img)
		self.img = self.img.rotate(180, Image.NEAREST, expand=1)
		self.img.save(os.path.join(os.getcwd(),self.filename+'.png'),"PNG")

	def generate(self):
		draw = ImageDraw.Draw(self.img)
		for roadList in self.roads:
			for i in range(1,len(roadList)):
				draw.line((roadList[i]['lon'],roadList[i]['lat'],roadList[i-1]['lon'],roadList[i-1]['lat']), fill=tuple(i for i in self.data['details']['color']) )
		del draw
