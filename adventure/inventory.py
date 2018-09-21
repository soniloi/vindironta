from adventure.item_container import ItemContainer

class Inventory(ItemContainer):

	def __init__(self):
		ItemContainer.__init__(self)


	def get_contents_description(self):
		result = "You are not holding anything."
		if self.items:
			result = "You are holding the following items:"
			for item in self.items.values():
				result += "\n\t" + item.longname
		return result
