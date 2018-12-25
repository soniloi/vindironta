import json
import unittest

from adventure.inventory_collection import InventoryCollection

class TestInventoryCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_init_default(self):
		inventory_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 0, \
					\"attributes\": \"1\", \
					\"labels\": { \
						\"shortname\": \"Main Inventory\", \
						\"longname\": \"in the main unventory\", \
						\"description\": \", where items live usually.\" \
					}, \
					\"capacity\": 13 \
				} \
			]"
		)

		collection = InventoryCollection(inventory_inputs)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(0 in collection.inventories)
		inventory = collection.inventories[0]
		self.assertEqual(13, inventory.capacity)
		self.assertFalse(inventory.location_ids)


	def test_init_non_default(self):
		inventory_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1, \
					\"attributes\": \"0\", \
					\"labels\": { \
						\"shortname\": \"Special Inventory\", \
						\"longname\": \"in the special unventory\", \
						\"description\": \", where items live sometimes.\" \
					}, \
					\"capacity\": 17, \
					\"locations\": [ \
						4, \
						5, \
						19 \
					] \
				} \
			]"
		)

		collection = InventoryCollection(inventory_inputs)

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
