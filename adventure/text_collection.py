import re

from adventure.file_reader import FileReader

class TextCollection:

	INPUT_SUBSTITUTION_PATTERN = "\$[0-9]+"

	def __init__(self, reader):
		self.texts = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_text(line)
			line = reader.read_line()


	def create_text(self, line):
		tokens = line.split("\t")
		text_key = tokens[0]
		text_value = self.translate_substitution_tokens(tokens[1])
		self.texts[text_key] = text_value


	def translate_substitution_tokens(self, text):
		return re.sub(TextCollection.INPUT_SUBSTITUTION_PATTERN, self.replace_token, text)


	def replace_token(self, match):
		match_token = match.group(0)
		return "{" + match_token[1:] + "}"


	def get(self, text_key):
		if text_key in self.texts:
			return self.texts[text_key]
		return ""
