import unittest

from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.location import Location
from adventure.player import Player

class TestPlayer(unittest.TestCase):

	def setUp(self):
		self.lighthouse_location = Location(12, 0x603, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.beach_location = Location(13, 0x603, Labels("Beach", "on a beach", " of black sand"))
		self.cave_location = Location(9, 0x402, Labels("Cave", "in a cave", ". It is dark"))
		self.inventory = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 13)
		self.player = Player(1, 0x3, self.lighthouse_location, self.beach_location, self.inventory)


	def test_reincarnate(self):
		self.player.set_alive(False)
		self.player.previous_location = self.cave_location

		self.player.reincarnate()

		self.assertTrue(self.player.is_alive())
		self.assertIs(self.beach_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


if __name__ == "__main__":
	unittest.main()
