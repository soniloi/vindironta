from collections import namedtuple
from enum import Enum

from adventure.element import Labels, NamedDataElement
from adventure.item_container import ItemContainer

class Item(NamedDataElement):

	ATTRIBUTE_CONTAINER = 0x1
	ATTRIBUTE_MOBILE = 0x2
	ATTRIBUTE_OBSTRUCTION = 0x4
	ATTRIBUTE_SWITCHABLE = 0x8
	ATTRIBUTE_GIVES_LIGHT = 0x10
	ATTRIBUTE_GIVES_AIR = 0x20
	ATTRIBUTE_LIQUID = 0x100
	ATTRIBUTE_LIQUID_CONTAINER = 0x200
	ATTRIBUTE_WEARABLE = 0x400
	ATTRIBUTE_COPYABLE = 0x800
	ATTRIBUTE_STRONG = 0x1000
	ATTRIBUTE_EDIBLE = 0x2000
	ATTRIBUTE_SILENT = 0x20000
	ATTRIBUTE_SENTIENT = 0x80000
	ATTRIBUTE_ALLOWS_BURNING = 0x200000

	# TODO: find a better place for this
	COMMAND_ID_BURN = 6
	COMMAND_ID_SMASH = 73


	def __init__(self, item_id, attributes, labels, size, writing, copied_from=None):
		NamedDataElement.__init__(self, data_id=item_id, attributes=attributes, labels=labels)
		self.size = size
		self.writing = writing
		self.containers = set()
		self.replacements = {}
		self.related_command = None
		self.obstruction = bool(attributes & Item.ATTRIBUTE_OBSTRUCTION)
		self.copied_from = copied_from
		self.copied_to = set()


	def __copy__(self):
		item_copy = type(self)(
			item_id=self.data_id,
			attributes=(self.attributes & ~Item.ATTRIBUTE_COPYABLE),
			labels=Labels(self.shortname, self.longname, self.description),
			size=self.size,
			writing=self.writing,
			copied_from=self,
		)
		self.copied_to.add(item_copy)

		for command_id, replacement in self.replacements.items():
			item_copy.replacements[command_id] = replacement
		item_copy.related_command = self.related_command

		return item_copy


	def get_original(self):
		if self.copied_from:
			return self.copied_from.get_original()
		return self


	def destroy(self):
		self.remove_from_containers()
		self.containers.clear()
		if self.copied_from:
			self.copied_from.copied_to.remove(self)


	def is_allow_copy(self, item):
		return item is self or item is self.copied_from


	def is_switchable(self):
		return False


	def get_full_description(self):
		return [self.description]


	def get_list_name(self, indentation=1):
		result = "\n"
		for i in range(0, indentation):
			result += "\t"
		return result + self.longname


	def get_non_silent_list_name(self, indentation=1):
		if not self.is_silent():
			return self.get_list_name(indentation)
		return ""


	def remove_from_containers(self):
		for container in self.containers:
			container.remove(self)


	def update_container(self, container):
		first_container = self.get_first_container()
		if first_container:
			self.containers.remove(first_container)
		self.containers.add(container)


	def add_container(self, container):
		self.containers.add(container)


	def get_weight(self):
		return self.size


	def contains(self, item):
		return False


	def get_allow_copy(self, item):
		return None


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


	def is_copyable(self):
		return self.has_attribute(Item.ATTRIBUTE_COPYABLE)


	def is_strong(self):
		return self.has_attribute(Item.ATTRIBUTE_STRONG)


	def gives_light(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_LIGHT)


	def gives_air(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_AIR)


	def is_liquid(self):
		return self.has_attribute(Item.ATTRIBUTE_LIQUID)


	def is_liquid_container(self):
		return self.has_attribute(Item.ATTRIBUTE_LIQUID_CONTAINER)


	def is_edible(self):
		return self.has_attribute(Item.ATTRIBUTE_EDIBLE)


	def is_silent(self):
		return self.has_attribute(Item.ATTRIBUTE_SILENT)


	def is_sentient(self):
		return self.has_attribute(Item.ATTRIBUTE_SENTIENT)


	def is_burnable(self):
		return Item.COMMAND_ID_BURN in self.replacements


	def allows_burning(self):
		return self.has_attribute(Item.ATTRIBUTE_ALLOWS_BURNING)


	def is_smashable(self):
		return Item.COMMAND_ID_SMASH in self.replacements


	def get_outermost_container(self):
		container = self.get_first_container()
		while isinstance(container, Item):
			container = container.get_first_container()
		return container


	def get_first_container(self):
		if len(self.containers) >= 1:
			return next(iter(self.containers))
		return None


	def get_sentient_owner(self):
		owner = self.get_first_container()
		if isinstance(owner, SentientItem):
			return owner
		elif not isinstance(owner, Item):
			return None
		return owner.get_sentient_owner()


class ContainerItem(Item, ItemContainer):

	def __init__(self, item_id, attributes, labels, size, writing, copied_from=None):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing, copied_from=copied_from)
		ItemContainer.__init__(self)


	def gives_air(self):
		if self.has_attribute(Item.ATTRIBUTE_GIVES_AIR):
			return True

		return ItemContainer.gives_air(self)


	def allows_burning(self):
		if self.has_attribute(Item.ATTRIBUTE_ALLOWS_BURNING):
			return True

		return ItemContainer.allows_burning(self)


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


	def get_allow_copy(self, item):
		if self.has_items():
			inner_item = self.get_contained_item()

			if inner_item.is_allow_copy(item):
				return inner_item
			return inner_item.get_allow_copy(item)

		return None


	def get_contained_item(self):
		return next(iter(self.items.values()))


	def can_accommodate(self, item):
		return self.size > item.size


class SentientItem(ItemContainer, Item):

	def __init__(self, item_id, attributes, labels, size, writing, copied_from=None):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing, copied_from=copied_from)
		ItemContainer.__init__(self)


	def gives_air(self):
		if self.has_attribute(Item.ATTRIBUTE_GIVES_AIR):
			return True

		return ItemContainer.gives_air(self)


	def get_list_name(self, indentation=1):

		result = Item.get_list_name(self, indentation)
		inner_indentation = indentation + 1

		if self.items:
			template = " +{0}"
			inner_item = next(iter(self.items.values()))
			contents = inner_item.get_list_name(inner_indentation)
			result += template.format(contents)

		return result


	def is_sentient(self):
		return True


SwitchInfo = namedtuple("SwitchInfo", "attribute off on")

class SwitchTransition(Enum):
	OFF = 0
	ON = 1
	TOGGLE = 2


class SwitchableItem(Item):

	def __init__(self, item_id, attributes, labels, size, writing, switch_info=None, copied_from=None):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing, copied_from=copied_from)
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
		return [self.description, self.get_state_text()]


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

	def __init__(self, item_id, attributes, labels, size, writing, attribute_activated, copied_from=None):
		Item.__init__(self, item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing, copied_from=copied_from)
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
