import unittest

from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.location import Location
from adventure.player import Player

class TestPlayer(unittest.TestCase):

	def setUp(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		default_labels = Labels("Main Inventory", "in the main inventory", ", where items live usually.")
		self.default_inventory = Inventory(0, 0x1, default_labels, 13)
		non_default_labels = Labels("Special Inventory", "in the special inventory", ", where items live sometimes.")
		self.mine_inventory = Inventory(1, 0x0, non_default_labels, 8, [9,10,11])


	def test_init(self):
		player = Player(self.mine_location, self.default_inventory, [self.mine_inventory])

		self.assertIsNot(self.default_inventory, player.default_inventory)
		self.assertEqual(self.default_inventory.data_id, player.default_inventory.data_id)
		self.assertEqual(self.default_inventory.attributes, player.default_inventory.attributes)
		self.assertEqual(self.default_inventory.capacity, player.default_inventory.capacity)

		self.assertEqual(3, len(player.inventories_by_location))
		non_default_inventory = player.inventories_by_location[9]
		self.assertIs(non_default_inventory, player.inventories_by_location[10])
		self.assertIs(non_default_inventory, player.inventories_by_location[11])
		self.assertIsNot(self.mine_inventory, non_default_inventory)
		self.assertEqual(self.mine_inventory.data_id, non_default_inventory.data_id)
		self.assertEqual(self.mine_inventory.attributes, non_default_inventory.attributes)
		self.assertEqual(self.mine_inventory.capacity, non_default_inventory.capacity)


	def test_get_inventory_default(self):
		player = Player(self.lighthouse_location, self.default_inventory)

		player_inventory = player.get_inventory()
		self.assertEqual(self.default_inventory.data_id, player_inventory.data_id)
		self.assertEqual(self.default_inventory.attributes, player_inventory.attributes)
		self.assertEqual(self.default_inventory.capacity, player_inventory.capacity)


	def test_get_inventory_non_default(self):
		player = Player(self.mine_location, self.default_inventory, [self.mine_inventory])

		player_inventory = player.get_inventory()
		self.assertEqual(self.mine_inventory.data_id, player_inventory.data_id)
		self.assertEqual(self.mine_inventory.attributes, player_inventory.attributes)
		self.assertEqual(self.mine_inventory.capacity, player_inventory.capacity)


if __name__ == "__main__":
	unittest.main()
