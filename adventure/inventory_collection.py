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

		inventory = Inventory(inventory_id=inventory_id, attributes=attributes, capacity=capacity)
		self.inventories[inventory_id] = inventory


	def get(self, inventory_id):
		return self.inventories.get(inventory_id)
