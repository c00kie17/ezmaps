import argparse
import json
from map import mapObj

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
	ezmap = mapObj(data)
	ezmap.load_child_roads()
	ezmap.get_boundies()
	ezmap.normalize()
	ezmap.create_img()
	ezmap.generate()

if __name__ == '__main__':
	main()