from adventure.event import Event, EventMatch, EventMatchArgument, EventMatchArgumentType, EventOutcome

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
		match = self.parse_event_match(event_input["match"])
		outcome = self.parse_event_outcome(event_input["outcome"])

		event = Event(event_id, attributes, match, outcome)
		return event


	def parse_event_match(self, event_match_input):
		command_id = event_match_input["command_id"]
		arguments  = self.parse_event_match_arguments(event_match_input["arguments"])
		return EventMatch(command_id, arguments)


	def parse_event_match_arguments(self, event_match_argument_inputs):
		event_match_arguments = []

		for event_match_argument_input in event_match_argument_inputs:
			arg_type_key = event_match_argument_input["type"].upper()
			arg_type = EventMatchArgumentType[arg_type_key]
			arg_value = event_match_argument_input["value"]

			argument = EventMatchArgument(type=arg_type, value=arg_value)
			event_match_arguments.append(argument)

		return event_match_arguments


	def parse_event_outcome(self, event_outcome_input):
		text = event_outcome_input["text"]
		return EventOutcome(text)


	def get(self, event_id):
		return self.events.get(event_id)
