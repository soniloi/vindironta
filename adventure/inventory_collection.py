from adventure.data_element import Labels
from adventure.inventory import Inventory


class InventoryCollection:

	INDEX_ID = 0
	INDEX_ATTRIBUTES = 1
	INDEX_SHORTNAME = 2
	INDEX_LONGNAME = 3
	INDEX_DESCRIPTION = 4
	INDEX_CAPACITY = 5
	INDEX_LOCATIONS = 6

	def __init__(self, reader):
		self.inventories = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_inventory(line)
			line = reader.read_line()


	def create_inventory(self, line):
		tokens = line.split("\t")

		inventory_id = int(tokens[InventoryCollection.INDEX_ID])
		attributes = int(tokens[InventoryCollection.INDEX_ATTRIBUTES], 16)
		shortname = tokens[InventoryCollection.INDEX_SHORTNAME]
		longname = tokens[InventoryCollection.INDEX_LONGNAME]
		description = tokens[InventoryCollection.INDEX_DESCRIPTION]
		labels = Labels(shortname=shortname, longname=longname, description=description)
		capacity = int(tokens[InventoryCollection.INDEX_CAPACITY])
		location_ids = self.parse_location_ids(tokens[InventoryCollection.INDEX_LOCATIONS])

		inventory = Inventory(
			inventory_id=inventory_id,
			attributes=attributes,
			labels=labels,
			capacity=capacity,
			location_ids=location_ids,
		)
		self.inventories[inventory_id] = inventory


	def parse_location_ids(self, token):
		if not token:
			return []
		location_id_tokens = token.split(",")
		return list(map(int, location_id_tokens))


	def get(self, inventory_id):
		return self.inventories.get(inventory_id)


	def get_all(self):
		return self.inventories.values()
