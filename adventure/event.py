from adventure.element import DataElement

class Event(DataElement):

	def __init__(self, event_id, attributes, requirements, outcome):
		DataElement.__init__(self, data_id=event_id, attributes=attributes)
		self.requirements = requirements
		self.outcome = outcome


class EventRequirement:

	def __init__(self, command_id, arguments):
		self.command_id = command_id
		self.arguments = arguments


class EventOutcome:

	def __init__(self, text):
		self.text = text
