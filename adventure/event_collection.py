from adventure.event import Event, EventRequirement, EventRequirementArgument, EventRequirementArgumentType, EventOutcome

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
		arguments  = self.parse_event_requirement_arguments(event_requirement_input["arguments"])
		return EventRequirement(command_id, arguments)


	def parse_event_requirement_arguments(self, event_requirement_argument_inputs):
		event_requirement_arguments = []

		for event_requirement_argument_input in event_requirement_argument_inputs:
			arg_type_key = event_requirement_argument_input["type"].upper()
			arg_type = EventRequirementArgumentType[arg_type_key]
			arg_value = event_requirement_argument_input["value"]

			argument = EventRequirementArgument(type=arg_type, value=arg_value)
			event_requirement_arguments.append(argument)

		return event_requirement_arguments


	def parse_event_outcome(self, event_outcome_input):
		text = event_outcome_input["text"]
		return EventOutcome(text)


	def get(self, event_id):
		return self.events.get(event_id)
