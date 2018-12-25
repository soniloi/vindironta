from adventure.file_reader import FileReader

class InputCollection:

	def __init__(self, input_inputs):
		self.inputs = input_inputs


	def matches(self, internal_key, input_key):
		return input_key in self.inputs.get(internal_key)
