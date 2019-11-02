from copy import copy

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
		essential_drop_location_id = player_input["essential_drop_location_id"]
		reincarnation_location_id = player_input["reincarnation_location_id"]
		collectible_location_id = player_input["collectible_location_id"]
		location = locations[location_id]
		essential_drop_location = locations[essential_drop_location_id]
		reincarnation_location = locations[reincarnation_location_id]
		collectible_location = locations[collectible_location_id]
		default_inventory, inventories_by_location_id = self.create_player_inventories(default_inventory_template, inventory_templates)

		return Player(
			player_id=player_id,
			attributes=attributes,
			initial_location=location,
			essential_drop_location=essential_drop_location,
			reincarnation_location=reincarnation_location,
			collectible_location=collectible_location,
			default_inventory=default_inventory,
			inventories_by_location_id=inventories_by_location_id,
		)


	def create_player_inventories(self, default_inventory_template, inventory_templates):
		default_inventory = copy(default_inventory_template)

		inventories_by_location_id = {}
		for inventory_template in inventory_templates:
			self.add_non_default_inventory(inventories_by_location_id, inventory_template)

		return default_inventory, inventories_by_location_id


	def add_non_default_inventory(self, inventories_by_location_id, inventory_template):
		if not inventory_template.is_default():
			non_default_inventory = copy(inventory_template)
			for location_id in inventory_template.location_ids:
				inventories_by_location_id[location_id] = non_default_inventory
