from adventure.event import Event, EventMatch, EventMatchArgument, EventMatchArgumentType, EventOutcome

class EventCollection:

	def __init__(self, event_inputs, commands, items_by_id):
		self.events = self.parse_events(event_inputs, commands, items_by_id)


	def parse_events(self, event_inputs, commands, items_by_id):
		events = {}

		for event_input in event_inputs:
			event = self.parse_event(event_input, commands, items_by_id)
			events[event.data_id] = event

		return events


	def parse_event(self, event_input, commands, items_by_id):
		event_id = event_input["data_id"]
		attributes = int(event_input["attributes"], 16)
		match = self.parse_event_match(event_input["match"], commands, items_by_id)
		outcome = self.parse_event_outcome(event_input["outcome"])

		event = Event(event_id, attributes, match, outcome)
		return event


	def parse_event_match(self, event_match_input, commands, items_by_id):
		command = self.get_event_match_command(event_match_input["command_id"], commands)
		arguments  = self.parse_event_match_arguments(event_match_input["arguments"], items_by_id)
		return EventMatch(command, arguments)


	def get_event_match_command(self, command_id, commands):
		return commands.get(command_id)


	def parse_event_match_arguments(self, event_match_argument_inputs, items_by_id):
		event_match_arguments = []

		for event_match_argument_input in event_match_argument_inputs:
			arg_type_key = event_match_argument_input["type"].upper()
			arg_type = EventMatchArgumentType[arg_type_key]

			arg_value = event_match_argument_input["value"]
			if arg_type == EventMatchArgumentType.ITEM:
				arg_value = items_by_id.get(arg_value)

			argument = EventMatchArgument(type=arg_type, value=arg_value)
			event_match_arguments.append(argument)

		return event_match_arguments


	def parse_event_outcome(self, event_outcome_input):
		text = event_outcome_input["text"]
		return EventOutcome(text)


	def get(self, event_id):
		return self.events.get(event_id)
