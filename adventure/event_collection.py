from adventure.event import Event, EventRequirement, EventOutcome

class EventCollection:

	def __init__(self, event_inputs):
		self.events = self.parse_events(event_inputs)


	def parse_events(self, event_inputs):
		events = {}

		for event_input in event_inputs:
			event = self.parse_event(event_input)
			events[event.data_id] = event

		return events


	def parse_event(self, event_input):
		event_id = event_input["data_id"]
		attributes = int(event_input["attributes"], 16)
		requirements = self.parse_event_requirements(event_input["requirements"])
		outcome = self.parse_event_outcome(event_input["outcome"])

		event = Event(event_id, attributes, requirements, outcome)
		return event


	def parse_event_requirements(self, event_requirement_input):
		command_id = event_requirement_input["command_id"]
		arguments  = event_requirement_input["arguments"]
		return EventRequirement(command_id, arguments)


	def parse_event_outcome(self, event_outcome_input):
		text = event_outcome_input["text"]
		return EventOutcome(text)


	def get(self, event_id):
		return self.events.get(event_id)
