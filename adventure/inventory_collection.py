from adventure.element import Labels
from adventure.inventory import Inventory


class InventoryCollection:

	INDEX_ID = 0
	INDEX_ATTRIBUTES = 1
	INDEX_SHORTNAME = 2
	INDEX_LONGNAME = 3
	INDEX_DESCRIPTION = 4
	INDEX_CAPACITY = 5
	INDEX_LOCATIONS = 6

	def __init__(self, inventory_inputs):
		self.inventories = self.parse_inventories(inventory_inputs)


	def parse_inventories(self, inventory_inputs):
		inventories = {}

		for inventory_input in inventory_inputs:
			inventory = self.parse_inventory(inventory_input)
			inventories[inventory.data_id] = inventory

		return inventories


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
		return Labels(label_input["shortname"], label_input["longname"], label_input["description"])


	def parse_location_ids(self, location_ids_input):
		if not location_ids_input:
			return []
		return location_ids_input


	def get(self, inventory_id):
		return self.inventories.get(inventory_id)


	def get_all(self):
		return self.inventories.values()
