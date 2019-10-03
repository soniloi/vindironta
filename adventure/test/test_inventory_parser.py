import json
import unittest

from adventure.inventory_parser import InventoryParser
from adventure.validation import Severity

class TestInventoryParser(unittest.TestCase):

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

		collection, validation = InventoryParser().parse(inventory_inputs)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(0 in collection.inventories)
		inventory = collection.inventories[0]
		self.assertEqual("Main Inventory", inventory.shortname)
		self.assertEqual("in the main unventory", inventory.longname)
		self.assertEqual(", where items live usually.", inventory.description)
		self.assertEqual([], inventory.extended_descriptions)
		self.assertEqual(13, inventory.capacity)
		self.assertFalse(inventory.location_ids)
		self.assertFalse(validation)


	def test_init_non_default(self):
		inventory_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1, \
					\"attributes\": \"0\", \
					\"labels\": { \
						\"shortname\": \"Special Inventory\", \
						\"longname\": \"in the special unventory\", \
						\"description\": \", where items live sometimes.\", \
						\"extended_descriptions\": [ \
							\". This is unusual\" \
						] \
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

		collection, validation = InventoryParser().parse(inventory_inputs)

		self.assertEqual(1, len(collection.inventories))
		self.assertTrue(1 in collection.inventories)
		inventory = collection.inventories[1]
		self.assertEqual("Special Inventory", inventory.shortname)
		self.assertEqual("in the special unventory", inventory.longname)
		self.assertEqual(", where items live sometimes.", inventory.description)
		self.assertEqual([". This is unusual"], inventory.extended_descriptions)
		self.assertEqual(17, inventory.capacity)
		self.assertEqual(3, len(inventory.location_ids))
		self.assertTrue(4 in inventory.location_ids)
		self.assertTrue(5 in inventory.location_ids)
		self.assertTrue(19 in inventory.location_ids)
		self.assertFalse(validation)


	def test_init_duplicate_ids(self):
		inventory_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 43, \
					\"attributes\": \"1\", \
					\"labels\": { \
						\"shortname\": \"Main Inventory\", \
						\"longname\": \"in the main unventory\", \
						\"description\": \", where items live usually.\" \
					}, \
					\"capacity\": 13 \
				}, \
				{ \
					\"data_id\": 43, \
					\"attributes\": \"0\", \
					\"labels\": { \
						\"shortname\": \"Special Inventory\", \
						\"longname\": \"in the special unventory\", \
						\"description\": \", where items live sometimes.\", \
						\"extended_descriptions\": [ \
							\". This is unusual\" \
						] \
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

		collection, validation = InventoryParser().parse(inventory_inputs)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Multiple inventories found with id {0}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((43,), validation_line.args)


if __name__ == "__main__":
	unittest.main()
