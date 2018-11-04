from adventure.inventory import Inventory


class InventoryCollection:

	def __init__(self, reader):
		self.inventories = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_inventory(line)
			line = reader.read_line()


	def create_inventory(self, line):
		tokens = line.split("\t")

		inventory_id = int(tokens[0])
		attributes = int(tokens[1], 16)
		capacity = int(tokens[2])
		location_ids = self.parse_location_ids(tokens[3])

		inventory = Inventory(
			inventory_id=inventory_id,
			attributes=attributes,
			capacity=capacity,
			location_ids=location_ids
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
