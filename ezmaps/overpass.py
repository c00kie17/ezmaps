import requests
import json
from time import sleep
from ezmaps.util import print_iter,print_warning
import sys

queryPrepend = '[out:json][timeout:500];'
overpassUrl = "http://overpass-api.de/api/interpreter"

class Overpass():

	def __init__(self):
		pass

	def request_overpass_stream(self,query,desc):
		code = None
		while code != 200:
			response = requests.get(overpassUrl, params={'data': queryPrepend+query},stream=True)
			if response.status_code != 200:
				if response.status_code == 429:
					print_warning('Retrying request in 60 seconds')
					sleep(60)
					continue
				else:
					return None
			code = response.status_code
			resp = b''
			count = 0
			for data in response.iter_content(chunk_size=2048):
				resp += data
				count += 2048
				print_iter('Downloading '+str(desc)+': '+str(round(count/1000000,2)) +'MB')
		sys.stdout.write('\n')
		return json.loads(resp)

	def request_overpass(self,query):
		code = None
		while code != 200:
			response = requests.get(overpassUrl, params={'data':queryPrepend+query})
			if response.status_code != 200:
				if response.status_code == 429:
					print_warning('Retrying request in 60 seconds')
					sleep(60)
					continue
				else:
					return None
			code = response.status_code
		return response.json()

overpassManager = Overpass()
