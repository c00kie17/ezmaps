import sys

def print_iter(message):
	sys.stdout.write('\r')
	sys.stdout.write(message)
	sys.stdout.flush()

def exit_error(message):
	print('\033[1m\033[91m'+message+'\033[0m')
	sys.exit()

def print_warning(message):
	print('\033[93m'+message+'\033[0m')

def print_option(message):
	print('\033[94m'+message+'\033[0m')
