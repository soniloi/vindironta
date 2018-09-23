from adventure.file_reader import FileReader

class TextCollection:

	def __init__(self, reader):
		self.texts = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_text(line)
			line = reader.read_line()


	def create_text(self, line):
		tokens = line.split("\t")
		self.texts[tokens[0]] = tokens[1]


	def get(self, text_key):
		if text_key in self.texts:
			return self.texts[text_key]
		return None
