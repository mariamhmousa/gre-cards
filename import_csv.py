import csv

def read_csv(path):
	with open(path, newline='', encoding='utf-8-sig') as csvfile:
		file_reader = csv.DictReader(csvfile)
		file_reader.fieldnames = [name.strip().lower() for name in (file_reader.fieldnames or [])]

		#check headers are correct
		required = {'word', 'definition'}
		if not required.issubset(file_reader.fieldnames or []):
			raise ValueError("CSV needs 'word' and 'definition' columns")
		
		result = []
		for row in file_reader:
			word = (row.get('word') or '').strip()
			definition = (row.get('definition') or '').strip()
			example = (row.get('example') or '').strip()

			if not word or not definition:
				continue
			word_tuple = (word, definition, example)
			result.append(word_tuple)
			
	return result