from enum import Enum

from adventure.element import DataElement


class Event(DataElement):

	ATTRIBUTE_END_GAME = 0x1
	ATTRIBUTE_PUZZLE = 0x4

	def __init__(self, event_id, attributes, match, outcome):
		DataElement.__init__(self, data_id=event_id, attributes=attributes)
		self.match = match
		self.outcome = outcome


	def is_end_game(self):
		return self.has_attribute(Event.ATTRIBUTE_END_GAME)


	def is_puzzle(self):
		return self.has_attribute(Event.ATTRIBUTE_PUZZLE)


class EventMatch:

	def __init__(self, command, arguments, prerequisites):
		self.command = command
		self.arguments = arguments
		self.prerequisites = prerequisites


class EventMatchArgument:

	def __init__(self, kind, value):
		self.kind = kind
		self.value = value


class EventMatchArgumentKind(Enum):
	TEXT = 0
	ITEM = 1


class EventMatchPrerequisiteKind(Enum):
	EVENT = 0
	ITEM = 1
	LOCATION = 2


class EventMatchPrerequisite:

	def __init__(self, kind, invert):
		self.kind = kind
		self.invert = invert


class ItemEventMatchPrerequisite(EventMatchPrerequisite):

	def __init__(self, kind, invert, item, container):
		EventMatchPrerequisite.__init__(self, kind=kind, invert=invert)
		self.item = item
		self.container = container


class ItemEventMatchPrerequisiteContainer:

	def __init__(self, kind, container_id):
		self.kind = kind
		self.container_id = container_id


class ItemEventMatchPrerequisiteContainerKind(Enum):
	ANY = 0
	CURRENT_LOCATION = 1
	CURRENT_INVENTORY = 2
	ABSOLUTE_CONTAINER = 3



class LocationEventMatchPrerequisite:

	def __init__(self, kind, invert, location):
		EventMatchPrerequisite.__init__(self, kind=kind, invert=invert)
		self.location = location


class EventEventMatchPrerequisite:

	def __init__(self, kind, invert, event_id):
		EventMatchPrerequisite.__init__(self, kind=kind, invert=invert)
		self.event_id = event_id


class EventOutcome:

	def __init__(self, text_key, actions):
		self.text_key = text_key
		self.actions = actions


class EventOutcomeActionKind(Enum):
	PLAYER = 0
	ITEM = 1
	LOCATION = 2
	LINK = 3
	DESCRIPTION = 4


class PlayerEventOutcomeAction:

	def __init__(self, kind, attribute, on):
		self.kind = kind
		self.attribute = attribute
		self.on = on


class ItemEventOutcomeAction:

	def __init__(self, kind, item, destination):
		self.kind = kind
		self.item = item
		self.destination = destination


class ItemEventOutcomeActionDestination:

	def __init__(self, kind, named_data_element):
		self.kind = kind
		self.named_data_element = named_data_element


class ItemEventOutcomeActionDestinationKind(Enum):
	DESTROY = 0
	CURRENT_LOCATION = 1
	CURRENT_INVENTORY = 2
	ABSOLUTE_CONTAINER = 3
	REPLACE = 4


class LocationEventOutcomeAction:

	def __init__(self, kind, location, attribute, on):
		self.kind = kind
		self.location = location
		self.attribute = attribute
		self.on = on


class LinkEventOutcomeAction:

	def __init__(self, kind, source, direction, destination):
		self.kind = kind
		self.source = source
		self.direction = direction
		self.destination = destination


class DescriptionEventOutcomeAction:

	def __init__(self, kind, named_data_element, extended_description_index):
		self.kind = kind
		self.named_data_element = named_data_element
		self.extended_description_index = extended_description_index
