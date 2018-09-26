from adventure.item_container import ItemContainer

class Inventory(ItemContainer):

	def __init__(self):
		ItemContainer.__init__(self)


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += "\n\t" + item.longname
		return result
