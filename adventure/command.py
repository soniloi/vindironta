
class Command:

	def __init__(self, command_id, attributes, function, primary):
		self.command_id = command_id
		self.attributes = attributes
		self.function = function
		self.primary = primary

	def execute(self):
		return self.function()
