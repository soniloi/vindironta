from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.inventory_collection import InventoryCollection
from adventure.validation import Message, Severity

class InventoryParser:

	INDEX_ID = 0
	INDEX_ATTRIBUTES = 1
	INDEX_SHORTNAME = 2
	INDEX_LONGNAME = 3
	INDEX_DESCRIPTION = 4
	INDEX_CAPACITY = 5
	INDEX_LOCATIONS = 6

	def parse(self, inventory_inputs):
		inventories, validation = self.parse_inventories(inventory_inputs)
		return InventoryCollection(inventories), validation


	def parse_inventories(self, inventory_inputs):
		inventories = {}
		validation = []

		for inventory_input in inventory_inputs:
			inventory = self.parse_inventory(inventory_input)
			if inventory.data_id in inventories:
				validation.append(Message(Message.INVENTORY_SHARED_ID, (inventory.data_id,)))
			inventories[inventory.data_id] = inventory

		if len(inventories) < 1:
			validation.append(Message(Message.INVENTORY_NONE, ()))
		else:
			default_inventory_ids = [inventory.data_id for inventory in inventories.values() if inventory.is_default()]
			if len(default_inventory_ids) < 1:
				validation.append(Message(Message.INVENTORY_NO_DEFAULT, ()))
			elif len(default_inventory_ids) > 1:
				validation.append(Message(Message.INVENTORY_MULTIPLE_DEFAULT, (default_inventory_ids,)))

		return inventories, validation


	def parse_inventory(self, inventory_input):
		inventory_id = inventory_input["data_id"]
		attributes = int(inventory_input["attributes"], 16)
		labels = self.parse_labels(inventory_input["labels"])
		capacity = inventory_input["capacity"]
		location_ids = self.parse_location_ids(inventory_input.get("locations"))

		return Inventory(
			inventory_id=inventory_id,
			attributes=attributes,
			labels=labels,
			capacity=capacity,
			location_ids=location_ids,
		)


	def parse_labels(self, label_input):
		extended_descriptions = label_input.get("extended_descriptions", [])
		return Labels(label_input["shortname"], label_input["longname"], label_input["description"], extended_descriptions)


	def parse_location_ids(self, location_ids_input):
		if not location_ids_input:
			return []
		return location_ids_input
