import unittest

from adventure.item import Item
from adventure.inventory import Inventory
from adventure.location import Location

class TestInventory(unittest.TestCase):

	def setUp(self):
		self.inventory = Inventory(3)
		self.book = Item(1105, 0x2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.lamp = Item(1043, 0x101A, "lamp", "a lamp", "a small lamp", 2, None)
		self.coin = Item(1000, 0x2, "coin", "a coin", "a silver coin", 1, None)
		self.medal = Item(1001, 0x2, "medal", "a medal", "a gold medal", 1, None)
		self.drop_location = Location(12, 0x1, "Lighthouse", "at a lighthouse", " by the sea.")


	def test_can_accommodate_below_capacity(self):
		self.assertTrue(self.inventory.can_accommodate(self.book))


	def test_can_accommodate_to_capacity(self):
		self.inventory.insert(self.book)

		self.assertTrue(self.inventory.can_accommodate(self.coin))


	def test_can_accommodate_at_capacity(self):
		self.inventory.insert(self.book)
		self.inventory.insert(self.medal)

		self.assertFalse(self.inventory.can_accommodate(self.coin))


	def test_can_accommodate_above_capacity(self):
		self.inventory.insert(self.book)

		self.assertFalse(self.inventory.can_accommodate(self.lamp))


	def test_drop_all_items_none(self):
		self.inventory.drop_all_items(self.drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertFalse(self.drop_location.has_items())


	def test_drop_all_items_single(self):
		self.inventory.insert(self.book)

		self.inventory.drop_all_items(self.drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertTrue(self.drop_location.contains(self.book))


	def test_drop_all_items_multiple(self):
		self.drop_location.insert(self.coin)
		self.drop_location.insert(self.medal)
		self.inventory.insert(self.book)
		self.inventory.insert(self.lamp)

		self.inventory.drop_all_items(self.drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertTrue(self.drop_location.contains(self.coin))
		self.assertTrue(self.drop_location.contains(self.medal))
		self.assertTrue(self.drop_location.contains(self.book))
		self.assertTrue(self.drop_location.contains(self.lamp))


if __name__ == "__main__":
	unittest.main()
