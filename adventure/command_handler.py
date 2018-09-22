class CommandHandler:

	def init_data(self, location_collection, item_collection):
		self.location_collection = location_collection
		self.item_collection = item_collection

	def get_command_function(self, command_function_name):
		return getattr(self, command_function_name, None)


	def handle_inventory(self, player, arg):
		return player.inventory.get_contents_description()


	def handle_look(self, player, arg):
		return "You are %s." % player.location.get_full_description()


	def handle_quit(self, player, arg):
		player.playing = False
		return "Game has ended"


	def handle_score(self, player, arg):
		return "Your current score is %s points" % player.score


	def handle_take(self, player, arg):
		#TODO: handle None arg

		result = ""

		item = self.item_collection.get(arg)
		if not item:
			result = "I do not know who or what that is."

		else:
			current_container = item.container
			if current_container == player.inventory:
				# TODO: enhance when implementing container items
				result = "You already have the %s." % item.shortname
			elif current_container != player.location:
				result = "I see no %s here." % item.shortname
			else:
				current_container.remove_item(item)
				player.inventory.insert_item(item)
				item.container = player.inventory
				result = "Taken."

		return result
