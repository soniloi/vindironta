from adventure.resolver import Resolver

class PuzzleResolver(Resolver):

	ITEM_ID_BEAN = 1003
	ITEM_ID_PLANT = 1058
	ITEM_ID_POTION = 1059

	def handle_pour(self, command, player, item, destination, source):
		template = ""

		if item.data_id == PuzzleResolver.ITEM_ID_POTION:

			if destination.data_id == PuzzleResolver.ITEM_ID_BEAN:
				plant = self.data.get_item_by_id(PuzzleResolver.ITEM_ID_PLANT)
				self.replace_item_at_location(player, destination, plant)
				template = self.get_response("event_potion_bean")

			elif destination.data_id == PuzzleResolver.ITEM_ID_PLANT:
				bean = self.data.get_item_by_id(PuzzleResolver.ITEM_ID_BEAN)
				self.replace_item_at_location(player, destination, bean)
				template = self.get_response("event_potion_plant")

		return True, template, [item, destination, source]


	def replace_item_at_location(self, player, previous, replacement):
		player.drop_item(replacement)
		previous.destroy()


	def handle_say(self, command, player, word):
		return True, "", [word]
