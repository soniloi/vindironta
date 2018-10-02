import unittest

from adventure.item import Item
from adventure.inventory import Inventory

class TestInventory(unittest.TestCase):

	def setUp(self):
		self.inventory = Inventory(3)
		self.book = Item(1105, 0x2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.lamp = Item(1043, 0x101A, "lamp", "a lamp", "a small lamp", 2, None)
		self.coin = Item(1000, 0x2, "coin", "a coin", "a silver coin", 1, None)
		self.medal = Item(1001, 0x2, "medal", "a medal", "a gold medal", 1, None)


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


if __name__ == "__main__":
	unittest.main()
