class InventoryCollection:

	DEFAULT_ID = 0

	def __init__(self, inventories):
		self.inventories = inventories


	def get(self, inventory_id):
		return self.inventories.get(inventory_id)


	def get_default(self):
		return self.get(InventoryCollection.DEFAULT_ID)


	def get_all(self):
		return self.inventories.values()
