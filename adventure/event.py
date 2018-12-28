from collections import namedtuple
from enum import Enum

from adventure.element import DataElement


class Event(DataElement):

	def __init__(self, event_id, attributes, match, outcome):
		DataElement.__init__(self, data_id=event_id, attributes=attributes)
		self.match = match
		self.outcome = outcome


class EventMatch:

	def __init__(self, command, arguments):
		self.command = command
		self.arguments = arguments


EventMatchArgument = namedtuple("EventMatchArgument", "type value")


class EventMatchArgumentType(Enum):
	TEXT = 0
	ITEM = 1


class EventOutcome:

	def __init__(self, text, actions):
		self.text = text
		self.actions = actions


class EventOutcomeActionKind(Enum):
	NONE = 0
	ITEM = 1


class ItemEventOutcomeAction:

	def __init__(self, kind, item_id, destination):
		self.kind = kind
		self.item_id = item_id
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
