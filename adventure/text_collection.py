import re

from adventure.file_reader import FileReader

class TextCollection:

	INPUT_SUBSTITUTION_PATTERN = "\$[0-9]+"

	def __init__(self, text_inputs):
		self.texts = self.parse_texts(text_inputs)


	def parse_texts(self, text_inputs):
		texts = {}

		for key, raw_value in text_inputs.items():
			value = self.translate_substitution_tokens(raw_value)
			texts[key] = value

		return texts


	def translate_substitution_tokens(self, text):
		return re.sub(TextCollection.INPUT_SUBSTITUTION_PATTERN, self.replace_token, text)


	def replace_token(self, match):
		match_token = match.group(0)
		return "{" + match_token[1:] + "}"


	def get(self, text_key):
		return self.texts.get(text_key, "")
