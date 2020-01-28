import argparse
import json
from ezmaps.ezmap import mapObj
from ezmaps.markers import add_markers
from tqdm import tqdm

def get_args():
	parser = argparse.ArgumentParser(description='Generating Maps')
	parser.add_argument('-c','--config',metavar='CONF', help='config file you need to generate map with', required=True)
	parser.add_argument('-s','--save' ,help='If you want to save the state file', required=False, action='store_true')
	parser.add_argument('-l','--load',metavar='LOAD', help='specify a state file to load from', required=False, default=None)
	return parser.parse_args()

def load_file(config):
	data = open(config,'r').read()
	data = json.loads(data)
	return data

def main():
	args = get_args()
	data = load_file(args.config)
	ezmap = mapObj(data,args.config.split('/')[-1].replace('.json',''))
	if args.load:
		ezmap.load_state(args.load)
	else:
		ezmap.get_place()
		ezmap.fetch_bounds()
		ezmap.load_child_roads()
	ezmap.get_map_boundies()
	if args.save:
		ezmap.save_state("/".join(args.config.split('/')[:-1]))
	print('Loaded Map')
	ezmap.set_scale()
	ezmap.normalize()
	ezmap.create_img()
	ezmap.generate()
	print('Generated Map')
	if 'markers' in data.keys():
		pbar = tqdm(total = len(data['markers']),desc='markers')
		for markers in data['markers']:
			for location in markers['locations']:
				add_markers(location,markers['icon'],markers['size'],ezmap,data['details'],"/".join(args.config.split('/')[:-1]))
			pbar.update(1)
		pbar.close()
	print('Generated Markers')
	ezmap.save_image("/".join(args.config.split('/')[:-1]))

if __name__ == '__main__':
	main()