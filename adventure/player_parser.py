from adventure.player import Player

class PlayerParser:

	def parse(self, player_inputs, locations, default_inventory_template, inventory_templates):
		player_count = len(player_inputs)
		assert player_count == 1, ("Only exactly one player supported, {0} given.").format(player_count)

		player_input = next(iter(player_inputs))
		return self.parse_player(player_input, locations, default_inventory_template, inventory_templates)


	def parse_player(self, player_input, locations, default_inventory_template, inventory_templates):
		player_id = player_input["data_id"]
		attributes = int(player_input["attributes"], 16)
		location_id = player_input["location_id"]
		location = locations[location_id]

		return Player(
			player_id=player_id,
			attributes=attributes,
			initial_location=location,
			default_inventory_template=default_inventory_template,
			inventory_templates=inventory_templates,
		)
