from enum import Enum

from adventure.element import DataElement


class Event(DataElement):

	def __init__(self, event_id, attributes, match, outcome):
		DataElement.__init__(self, data_id=event_id, attributes=attributes)
		self.match = match
		self.outcome = outcome


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
	OTHER = 0
	ITEM = 1
	LOCATION = 2


class ItemEventMatchPrerequisite:

	def __init__(self, kind, item, container):
		self.kind = kind
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

	def __init__(self, kind, location):
		self.kind = kind
		self.location = location


class EventOutcome:

	def __init__(self, text, actions):
		self.text = text
		self.actions = actions


class EventOutcomeActionKind(Enum):
	NONE = 0
	ITEM = 1


class ItemEventOutcomeAction:

	def __init__(self, kind, item, destination):
		self.kind = kind
		self.item = item
		self.destination = destination


class ItemEventOutcomeActionDestination:

	def __init__(self, kind, data_id):
		self.kind = kind
		self.data_id = data_id


class ItemEventOutcomeActionDestinationKind(Enum):
	DESTROY = 0
	CURRENT_LOCATION = 1
	CURRENT_INVENTORY = 2
	ABSOLUTE_CONTAINER = 3
	REPLACE = 4
