class TextCollection:

	def __init__(self, texts):
		self.texts = texts


	def get(self, text_key):
		return self.texts.get(text_key, "")
