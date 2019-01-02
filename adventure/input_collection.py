class InputCollection:

	def __init__(self, inputs):
		self.inputs = inputs


	def matches(self, internal_key, input_key):
		return self.inputs.get(input_key) == internal_key
