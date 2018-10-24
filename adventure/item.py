from adventure.data_element import DataElement
from adventure.item_container import ItemContainer

class Item(DataElement):

	ATTRIBUTE_CONTAINER = 0x1
	ATTRIBUTE_MOBILE = 0x2
	ATTRIBUTE_OBSTRUCTION = 0x4
	ATTRIBUTE_SWITCHABLE = 0x8
	ATTRIBUTE_GIVES_LIGHT = 0x10
	ATTRIBUTE_SILENT = 0x20000

	def __init__(self, item_id, attributes, shortname, longname, description, size, writing):
		super().__init__(data_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.size = size
		self.writing = writing
		self.container = None
		self.obstruction = self.has_attribute(Item.ATTRIBUTE_OBSTRUCTION)


	def is_switchable(self):
		return False


	def get_full_description(self):
		return self.description


	def get_list_name(self, indentation=1):
		result = "\n"
		for i in range(0, indentation):
			result += "\t"
		return result + self.longname


	def get_non_silent_list_name(self, indentation=1):
		if not self.is_silent():
			return self.get_list_name(indentation)
		return ""


	def contains(self, item):
		return False


	def is_portable(self):
		return self.is_mobile() and not self.obstruction


	def is_mobile(self):
		return self.has_attribute(Item.ATTRIBUTE_MOBILE)


	def is_obstruction(self):
		return self.obstruction


	def gives_light(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_LIGHT)


	def is_silent(self):
		return self.has_attribute(Item.ATTRIBUTE_SILENT)


class ContainerItem(Item, ItemContainer):

	def __init__(self, item_id, attributes, shortname, longname, description, size, writing):
		Item.__init__(self, item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing)
		ItemContainer.__init__(self)


	def get_list_name(self, indentation=1):

		result = Item.get_list_name(self, indentation)
		inner_indentation = indentation + 1
		result += " "

		template = "(---)"
		contents = ""
		if self.items:
			template = "+{0}"
			inner_item = next(iter(self.items.values()))
			contents = inner_item.get_list_name(inner_indentation)

		result += template.format(contents)

		return result


	def contains(self, item):

		if self.has_items():

			inner_item = next(iter(self.items.values()))
			if item == inner_item:
				return True

			return inner_item.contains(item)

		return False


class SwitchableItem(Item):

	def __init__(self, item_id, attributes, shortname, longname, description, size, writing, switching_info):
		Item.__init__(self, item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing)
		ItemContainer.__init__(self)
		self.switched_element = None
		self.switched_attribute = switching_info[1]
		self.state_to_text = {
			False : switching_info[2],
			True : switching_info[3],
		}


	def is_switchable(self):
		return True


	def get_list_name(self, indentation=1):
		result = Item.get_list_name(self, indentation)
		result += " (" + self.state_to_text[self.is_on()] + ")"
		return result


	def is_on(self):
		return self.switched_element.has_attribute(self.switched_attribute)


	def switch_on(self):
		self.switched_element.set_attribute(self.switched_attribute)


	def switch_off(self):
		self.switched_element.unset_attribute(self.switched_attribute)
