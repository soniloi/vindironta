from enum import Enum

from adventure.data_element import NamedDataElement
from adventure.item_container import ItemContainer

from collections import namedtuple

class Item(NamedDataElement):

	ATTRIBUTE_CONTAINER = 0x1
	ATTRIBUTE_MOBILE = 0x2
	ATTRIBUTE_OBSTRUCTION = 0x4
	ATTRIBUTE_SWITCHABLE = 0x8
	ATTRIBUTE_GIVES_LIGHT = 0x10
	ATTRIBUTE_GIVES_AIR = 0x20
	ATTRIBUTE_LIQUID = 0x100
	ATTRIBUTE_LIQUID_CONTAINER = 0x200
	ATTRIBUTE_WEARABLE= 0x400
	ATTRIBUTE_SILENT = 0x20000

	def __init__(self, item_id, attributes, labels, size, writing):
		NamedDataElement.__init__(self, data_id=item_id, attributes=attributes, labels=labels)
		self.size = size
		self.writing = writing
		self.container = None
		self.obstruction = bool(attributes & Item.ATTRIBUTE_OBSTRUCTION)


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


	def update_container(self, container):
		self.container = container


	def get_weight(self):
		return self.size


	def contains(self, item):
		return False


	def is_container(self):
		return self.has_attribute(Item.ATTRIBUTE_CONTAINER)


	def is_portable(self):
		return self.is_mobile() and not self.obstruction


	def is_mobile(self):
		return self.has_attribute(Item.ATTRIBUTE_MOBILE)


	def is_obstruction(self):
		return self.obstruction


	def is_wearable(self):
		return self.has_attribute(Item.ATTRIBUTE_WEARABLE)


	def gives_light(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_LIGHT)


	def gives_air(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_AIR)


	def is_liquid(self):
		return self.has_attribute(Item.ATTRIBUTE_LIQUID)


	def is_liquid_container(self):
		return self.has_attribute(Item.ATTRIBUTE_LIQUID_CONTAINER)


	def is_silent(self):
		return self.has_attribute(Item.ATTRIBUTE_SILENT)


	def get_outermost_container(self):
		container = self.container
		while isinstance(container, Item):
			container = container.container
		return container


class ContainerItem(Item, ItemContainer):

	def __init__(self, item_id, attributes, labels, size, writing):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)
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

			inner_item = self.get_contained_item()
			if item == inner_item:
				return True

			return inner_item.contains(item)

		return False


	def get_contained_item(self):
		return next(iter(self.items.values()))


	def can_accommodate(self, item):
		return self.size > item.size


SwitchInfo = namedtuple("SwitchInfo", "attribute off on")

class SwitchTransition(Enum):
	OFF = 0
	ON = 1
	TOGGLE = 2


class SwitchableItem(Item):

	def __init__(self, item_id, attributes, labels, size, writing, switch_info):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)
		ItemContainer.__init__(self)
		self.switched_element = None
		self.switched_attribute = switch_info.attribute
		self.state_to_text = {
			False : switch_info.off,
			True : switch_info.on,
		}
		self.text_to_transition = {
			switch_info.off : SwitchTransition.OFF,
			switch_info.on : SwitchTransition.ON,
		}


	def is_switchable(self):
		return True


	def get_list_name(self, indentation=1):
		result = Item.get_list_name(self, indentation)
		result += " (" + self.get_state_text() + ")"
		return result


	def get_full_description(self):
		return [Item.get_full_description(self), self.get_state_text()]


	def get_state_text(self):
		return self.state_to_text[self.is_on()]


	def is_on(self):
		return self.switched_element.has_attribute(self.switched_attribute)


	def switch_on(self):
		self.switched_element.set_attribute(self.switched_attribute)


	def switch_off(self):
		self.switched_element.unset_attribute(self.switched_attribute)


	def switch_toggle(self):
		self.switched_element.toggle_attribute(self.switched_attribute)


class WearableItem(Item):

	def __init__(self, item_id, attributes, labels, size, writing, attribute_activated):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)
		self.attribute_activated = attribute_activated
		self.being_worn = False


	def has_attribute(self, attribute):
		if self.being_worn:
			return bool((self.attributes | self.attribute_activated) & attribute)
		return Item.has_attribute(self, attribute)


	def get_weight(self):
		if self.being_worn:
			return 0
		return self.size


	def update_container(self, container):
		Item.update_container(self, container)
		self.being_worn = False
