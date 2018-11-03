import unittest
from unittest.mock import Mock

from adventure.inventory_collection import InventoryCollection

class TestInventoryCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_init(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"0\t0x1\t13",
			"---",
		]

		collection = InventoryCollection(reader_mock)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(0 in collection.inventories)
		inventory = collection.inventories[0]
		self.assertEqual(13, inventory.capacity)


if __name__ == "__main__":
	unittest.main()
