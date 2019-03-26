import re

class TokenTranslator:

	INPUT_SUBSTITUTION_PATTERN = "\$[0-9]+"

	def translate_substitution_tokens(text):
		return re.sub(TokenTranslator.INPUT_SUBSTITUTION_PATTERN, TokenTranslator.replace_token, text)


	def replace_token(match):
		match_token = match.group(0)
		return "{" + match_token[1:] + "}"
