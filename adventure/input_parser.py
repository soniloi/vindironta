from adventure.input_collection import InputCollection

class InputParser:

	def parse(self, input_inputs):
		inputs = self.parse_inputs(input_inputs)
		return InputCollection(inputs)


	def parse_inputs(self, input_inputs):
		inputs = {}

		for internal_key, values in input_inputs.items():
			for value in values:
				inputs[value] = internal_key

		return inputs
