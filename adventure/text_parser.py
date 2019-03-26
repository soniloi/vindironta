from adventure.text_collection import TextCollection
from adventure.token_translator import TokenTranslator

class TextParser:

	INPUT_SUBSTITUTION_PATTERN = "\$[0-9]+"

	def parse(self, text_inputs):
		texts = self.parse_texts(text_inputs)
		return TextCollection(texts)


	def parse_texts(self, text_inputs):
		texts = {}

		for key, raw_value in text_inputs.items():
			value = TokenTranslator.translate_substitution_tokens(raw_value)
			texts[key] = value

		return texts
