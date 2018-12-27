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

	def __init__(self, text):
		self.text = text
