import unittest

from adventure.data_element import Labels
from adventure.inventory import Inventory
from adventure.location import Location
from adventure.player import Player

class TestPlayer(unittest.TestCase):

	def setUp(self):
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.default_inventory = Inventory(0, 0x1, 13)
		self.non_default_inventory = Inventory(1, 0x0, 8, [9,10,11])
		self.inventories_by_location = {
			9 : self.non_default_inventory,
			10 : self.non_default_inventory,
			11 : self.non_default_inventory,
		}


	def test_get_inventory_default(self):
		player = Player(self.lighthouse_location, self.default_inventory)

		self.assertEqual(self.default_inventory, player.get_inventory())


	def test_get_inventory_non_default(self):
		player = Player(self.mine_location, self.default_inventory, self.inventories_by_location)

		self.assertEqual(self.non_default_inventory, player.get_inventory())


if __name__ == "__main__":
	unittest.main()
