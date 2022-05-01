from time import sleep
from csv import DictReader
from os import get_terminal_size, system


def progress_bar(progress, total, err=None):
	"""this programm is for general loading stuff.. it can show
	the progress of loading for user"""

	#vypočítavanie
	ter_size = (get_terminal_size().columns - 10) / 100
	percent = 100 * ((progress) / float(total))
	bar = '█' * int(percent * ter_size) + '-' * (int(ter_size * 100) - int(percent * ter_size))

	#clean up
	printi = ' ' * int(len(bar) + 10)
	print(printi, end='\r')

	print('\x1b[1;33;33m' + f"|{bar}| {percent:.2f}%" + '\x1b[0m', end="\r")

	if progress == total:
		print('\33[92m' + f"\r|{bar}| {percent:.2f}%" + '\33[0m', end="\n")

	if err is not None:
		#na konci je \n aby sa error správa správne vypísala do konzoly
		print('\x1b[1;30;41m' + f"\r|{bar}| {percent:.2f}%" + '\x1b[0m', end="\n\a")
		sleep(0.5)
		raise err

def CSVr(csvfile, debug):
	"""Na čítanie z .csv filov"""

	with open(csvfile, 'r') as csvf:
		csv_diktionary = DictReader(csvf)

		if debug['csv']: print(debug['gtext'] + debug['text'] + f' CSV↓ \r')
		pos = [{}]*3
		posCount1 = 0
		posCount2 = 0
		for row1 in csv_diktionary:
			if row1['ar'] == '1':
				posCount1 += 1
				pos[1][posCount1] = {
					'X': float(row1['X']),# * 10,
					'Y': float(row1['Y']),# * 10,
					'Z': float(row1['Z'])# * 10
				}
				if debug['csv']: print(debug['gtext'] + f' {row1}')

			elif row1['ar'] == '2':
				posCount2 += 1
				pos[2][posCount2] = {
					'X': float(row1['X']),# * 10,
					'Y': float(row1['Y']),# * 10,
					'Z': float(row1['Z'])# * 10
				}
				if debug['csv']: print(debug['gtext'] + f' {row1}')
			elif debug['csv']:
				print(debug['Error'] + f' {row1}')

	if debug['csv']:
		for poss in pos:
			for key, value in poss.items():
				print(key, '\t : ', value, end='\n')

	return pos[1],pos[2]

if __name__ == "__main__":

	#test loading baru pre commandlinu
	CSVr('.\\positions.csv', {
	'0':            bool(1),  # celkový debug
	'csv':          bool(1),  # čítanie CSV súboru
	'math':         bool(0),  # matematika
	'mathEX':       bool(1),  # matematika
	'ini':          bool(1),  # inicializačný
	'fromser':      bool(1),  # z sériového portu
	'auto-program': bool(1),  # proste automatický mód
	'zasielanie':   bool(1),  # kontrola zasielania
	'text':         '\x1b[1;33;33m' + 'debug:' + '\x1b[0m',  # samotný text "debug:"
	'space':        '\x1b[1;33;33m' + 'I ' + '\x1b[0m',  # žltý medzerník
	'gtext':        '\33[92m' + 'I ' + '\33[0m',  # zelený medzerník
	'Error':        '\x1b[1;30;41m' + '\tE ' + '\x1b[0m'  # VEĽKÉ červené "E "
})
	import math
	numbers = [x * 5 for x in range(2000, 3000)]
	results = []
	progress_bar(0, len(numbers))
	for i, x in enumerate(numbers):
		#v appende je iba paiload
		results.append(math.factorial(x))
		progress_bar(i + 1, len(numbers))
	sleep(0.5)

	numbers = [x * 5 for x in range(2000, 3000)]
	results = []
	progress_bar(0, len(numbers))
	for i, x in enumerate(numbers):
		results.append(math.factorial(x))
		if i == 99:
			#ak chcem vzpísať error i musí byť bez +1
			# ak chceš vypísať správne kde sa vyskitol error
			progress_bar(i, len(numbers), 2)
		progress_bar(i + 1, len(numbers))

	#system('cls')