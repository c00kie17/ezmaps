import argparse
import json
from map import mapObj
from markers import add_markers
from tqdm import tqdm

#get CLI working
#check all maps

def get_args():
	parser = argparse.ArgumentParser(description='Generating Maps')
	parser.add_argument('-c','--config',metavar='CONF', help='config file you need to generatea map with', required=True)
	return parser.parse_args()

def load_file(config):
	data = open(config,'r').read()
	data = json.loads(data)
	return data

def main():
	args = get_args()
	data = load_file(args.config)
	ezmap = mapObj(data,args.config.split('/')[-1].replace('.json',''))
	ezmap.load_child_roads()
	ezmap.get_map_boundies()
	print('Loaded Map')
	ezmap.set_scale()
	ezmap.normalize()
	ezmap.create_img()
	ezmap.generate()
	print('Generated Map')
	pbar = tqdm(total = len(data['markers']),desc='markers')
	for markers in data['markers']:
		for location in markers['locations']:
			add_markers(location,markers['icon'],markers['size'],ezmap,data['details'])
		pbar.update(1)
	pbar.close()
	print('Generated Markers')
	ezmap.save_image()

if __name__ == '__main__':
	main()