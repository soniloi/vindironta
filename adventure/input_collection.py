from adventure.file_reader import FileReader

class InputCollection:

	def __init__(self, reader):
		self.inputs = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_text(line)
			line = reader.read_line()


	def create_text(self, line):
		tokens = line.split("\t")
		internal_key = tokens[0]
		input_values = self.get_input_values(tokens[1])
		self.inputs[internal_key] = input_values


	def get_input_values(self, token):
		return set(token.split(","))


	def matches(self, internal_key, input_key):
		return input_key in self.inputs.get(internal_key)
