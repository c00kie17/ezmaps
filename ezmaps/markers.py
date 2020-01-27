from ezmaps.overpass import overpassManager
from PIL import Image,ImageDraw,ImageOps
import os
from ezmaps.util import *


def add_markers(value,icon,size,ezmap,details,path):
	icon = load_icon(os.path.join(path,'icons/'+icon),size,ezmap,details['size'])
	if icon:
		cords = get_locations(value,ezmap)
		cords = normalize(cords,ezmap)
		draw(cords,icon,ezmap)
	else:
		return

def load_icon(path,size,ezmap,output_size):
	try:
		icon = Image.open(path)
	except FileNotFoundError:
		return None
	else:
		imgWidth,imgHeight = ezmap.img.size
		if isinstance(output_size,list):
			width = int(((size*100/output_size[0])*imgWidth)/100)
			height = int(((size*100/output_size[1])*imgHeight)/100)
		elif isinstance(output_size,int):
			width = size
			height = size
		icon = icon.resize((width,height), Image.ANTIALIAS)
		return icon

def get_locations(value,ezmap):
	if isinstance(value, list):
		return [value]
	elif isinstance(value, str):
		query = 'area["name"="'+ezmap.map['tags']['name']+'"]->.searchArea;(node["amenity"="'+value+'"](area.searchArea);way["amenity"="'+value+'"](area.searchArea);relation["amenity"="'+value+'"](area.searchArea););out body;>;out skel qt;'
		response = overpassManager.request_overpass(query)
		nodeArray = []
		for element in response['elements']:
			if element['type'] == 'node':
				nodeArray.append([element['lat'],element['lon']])
		return nodeArray

def normalize(cords,ezmap):
	for cord in cords:
		cord[0] = abs(int(cord[0]*ezmap.scaleValue) - ezmap.boundry['minlat'])
		cord[1] = abs(int(cord[1]*ezmap.scaleValue) - ezmap.boundry['minlon'])
	return cords

def draw(cords,icon,ezmap):
	for cord in cords:
		myicon = ImageOps.mirror(icon)
		myicon = myicon.rotate(180, Image.NEAREST, expand=1)
		try:
			ezmap.img.paste(myicon,(cord[1],cord[0]),myicon)
		except ValueError:
			exit_error('invalid icon file')


