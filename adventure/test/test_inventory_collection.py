import unittest
from unittest.mock import Mock

from adventure.inventory_collection import InventoryCollection

class TestInventoryCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_init_default(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"0\t0x1\tMain Inventory\tin the main inventory\t, where items live usually.\t13\t\t\t\t",
			"---",
		]

		collection = InventoryCollection(reader_mock)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(0 in collection.inventories)
		inventory = collection.inventories[0]
		self.assertEqual(13, inventory.capacity)
		self.assertFalse(inventory.location_ids)


	def test_init_non_default(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1\t0x1\tSpecial Inventory\tin the special inventory\t, where items live sometimes.\t17\t4,5,19\t\t\t",
			"---",
		]

		collection = InventoryCollection(reader_mock)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(1 in collection.inventories)
		inventory = collection.inventories[1]
		self.assertEqual(17, inventory.capacity)
		self.assertEqual(3, len(inventory.location_ids))
		self.assertTrue(4 in inventory.location_ids)
		self.assertTrue(5 in inventory.location_ids)
		self.assertTrue(19 in inventory.location_ids)


if __name__ == "__main__":
	unittest.main()
