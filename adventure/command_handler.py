class CommandHandler:

	def init_data(self, location_collection, item_collection):
		self.location_collection = location_collection
		self.item_collection = item_collection

	def get_command_function(self, command_function_name):
		return getattr(self, command_function_name, None)


	def handle_inventory(self, player):
		return player.inventory.get_contents_description()


	def handle_look(self, player):
		return "You are %s." % player.location.get_full_description()


	def handle_quit(self, player):
		player.playing = False
		return "Game has ended"


	def handle_score(self, player):
		return "Your current score is %s points" % player.score
