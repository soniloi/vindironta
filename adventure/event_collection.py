from adventure.event import Event, EventMatch, EventMatchArgument, EventMatchArgumentKind
from adventure.event import EventOutcome, EventOutcomeActionKind, ItemEventOutcomeAction
from adventure.event import ItemEventOutcomeActionDestination, ItemEventOutcomeActionDestinationKind

class EventCollection:

	def __init__(self, event_inputs, commands_by_id, items_by_id):
		self.events = self.parse_events(event_inputs, commands_by_id, items_by_id)


	def parse_events(self, event_inputs, commands_by_id, items_by_id):
		events = {}

		for event_input in event_inputs:
			event, match = self.parse_event(event_input, commands_by_id, items_by_id)
			match_argument_values = [argument.value for argument in match.arguments]
			match_key = (tuple([match.command] + match_argument_values))
			events[match_key] = event

		return events


	def parse_event(self, event_input, commands_by_id, items_by_id):
		event_id = event_input["data_id"]
		attributes = int(event_input["attributes"], 16)
		match = self.parse_event_match(event_input["match"], commands_by_id, items_by_id)
		outcome = self.parse_event_outcome(event_input["outcome"])

		event = Event(event_id, attributes, match, outcome)
		return event, match


	def parse_event_match(self, event_match_input, commands_by_id, items_by_id):
		command = self.get_event_match_command(event_match_input["command_id"], commands_by_id)
		arguments  = self.parse_event_match_arguments(event_match_input["arguments"], items_by_id)
		return EventMatch(command, arguments)


	def get_event_match_command(self, command_id, commands_by_id):
		return commands_by_id.get(command_id)


	def parse_event_match_arguments(self, event_match_argument_inputs, items_by_id):
		event_match_arguments = []

		for event_match_argument_input in event_match_argument_inputs:
			arg_kind_key = event_match_argument_input["kind"].upper()
			arg_kind = EventMatchArgumentKind[arg_kind_key]

			arg_value = event_match_argument_input["value"]
			if arg_kind == EventMatchArgumentKind.ITEM:
				arg_value = items_by_id.get(arg_value)

			argument = EventMatchArgument(kind=arg_kind, value=arg_value)
			event_match_arguments.append(argument)

		return event_match_arguments


	def parse_event_outcome(self, event_outcome_input):
		text = event_outcome_input["text"]
		actions = self.parse_event_outcome_actions(event_outcome_input.get("actions"))
		return EventOutcome(text, actions)


	def parse_event_outcome_actions(self, event_outcome_action_inputs):
		if not event_outcome_action_inputs:
			return []

		actions  = []

		for event_outcome_action_input in event_outcome_action_inputs:
			kind_key = event_outcome_action_input["kind"].upper()
			kind = EventOutcomeActionKind[kind_key]

			# TODO: handle other kinds
			if kind == EventOutcomeActionKind.ITEM:
				item_id = event_outcome_action_input["item_id"]
				destination = self.parse_item_event_outcome_action_destination(event_outcome_action_input["destination"])

				action = ItemEventOutcomeAction(kind=kind, item_id=item_id, destination=destination)
				actions.append(action)

		return actions


	def parse_item_event_outcome_action_destination(self, item_event_outcome_action_destination_input):
		kind_key = item_event_outcome_action_destination_input["kind"].upper()
		kind = ItemEventOutcomeActionDestinationKind[kind_key]
		data_id = item_event_outcome_action_destination_input.get("data_id")
		return ItemEventOutcomeActionDestination(kind, data_id)


	def get(self, event_key):
		return self.events.get(event_key)
