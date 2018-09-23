from adventure.file_reader import FileReader

class TextCollection:

	SUBSTITUTION_TOKEN = "$$"

	def __init__(self, reader):
		self.texts = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_text(line)
			line = reader.read_line()


	def create_text(self, line):
		tokens = line.split("\t")
		text_key = tokens[0]
		# TODO: support additional args
		text_value = tokens[1].replace(TextCollection.SUBSTITUTION_TOKEN, "{0}")
		self.texts[text_key] = text_value


	def get(self, text_key):
		if text_key in self.texts:
			return self.texts[text_key]
		return ""
