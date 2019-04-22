import json
import unittest

from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.location import Location
from adventure.player_parser import PlayerParser

class TestPlayerParser(unittest.TestCase):

	def setUp(self):
		self.setup_locations()
		self.setup_inventories()


	def setup_locations(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.cave_location = Location(9, 0x0, Labels("Cave", "in a cave", ". It is dark"))

		self.location_map = {
			12 : self.lighthouse_location,
			9 : self.cave_location,
		}


	def setup_inventories(self):
		default_labels = Labels("Main Inventory", "in the main inventory", ", where items live usually.")
		self.default_inventory = Inventory(0, 0x1, default_labels, 13)
		non_default_labels = Labels("Special Inventory", "in the special inventory", ", where items live sometimes.")
		self.non_default_inventory = Inventory(1, 0x0, non_default_labels, 8, [9,11])


	def test_parse_none(self):
		player_inputs = json.loads(
			"[]"
		)

		with self.assertRaises(AssertionError) as assertion_error:
			PlayerParser().parse(player_inputs, self.location_map, self.default_inventory, [self.default_inventory, self.non_default_inventory])

		self.assertEqual("Only exactly one player supported, 0 given.", assertion_error.exception.args[0])


	def test_parse_single(self):
		player_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9000, \
					\"attributes\": \"3\", \
					\"location_id\": 12, \
					\"reincarnation_location_id\": 9 \
				} \
			]"
		)

		player = PlayerParser().parse(player_inputs, self.location_map, self.default_inventory, [self.default_inventory, self.non_default_inventory])

		self.assertEqual(9000, player.data_id)
		self.assertEqual(3, player.attributes)
		self.assertEqual(self.lighthouse_location, player.location)
		self.assertEqual(self.cave_location, player.reincarnation_location)

		default_inventory = player.default_inventory
		self.assertEqual(self.default_inventory.data_id, default_inventory.data_id)
		self.assertEqual(self.default_inventory.attributes, default_inventory.attributes)
		self.assertEqual(self.default_inventory.capacity, default_inventory.capacity)

		self.assertEqual(2, len(player.inventories_by_location_id))
		inventory_9 = player.inventories_by_location_id[9]
		inventory_11 = player.inventories_by_location_id[11]
		self.assertIs(inventory_9, inventory_11)
		self.assertEqual(self.non_default_inventory.data_id, inventory_9.data_id)
		self.assertEqual(self.non_default_inventory.attributes, inventory_9.attributes)
		self.assertEqual(self.non_default_inventory.capacity, inventory_9.capacity)


	def test_parse_multiple(self):
		player_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 9000, \
					\"attributes\": \"3\", \
					\"location_id\": 12, \
					\"reincarnation_location_id\": 9 \
				}, \
				{ \
					\"data_id\": 9001, \
					\"attributes\": \"5\", \
					\"location_id\": 17, \
					\"reincarnation_location_id\": 17 \
				} \
			]"
		)

		with self.assertRaises(AssertionError) as assertion_error:
			PlayerParser().parse(player_inputs, self.location_map, self.default_inventory, [self.default_inventory, self.non_default_inventory])

		self.assertEqual("Only exactly one player supported, 2 given.", assertion_error.exception.args[0])


if __name__ == "__main__":
	unittest.main()
