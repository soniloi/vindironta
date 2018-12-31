class CommandCollection:

	def __init__(self, commands_by_name, commands_by_id, command_list):
		self.commands_by_name = commands_by_name
		self.commands_by_id = commands_by_id
		self.command_list = command_list


	def get_by_name(self, name):
		return self.commands_by_name.get(name)


	def get_by_id(self, command_id):
		return self.commands_by_id.get(command_id)


	def list_commands(self):
		return self.command_list
