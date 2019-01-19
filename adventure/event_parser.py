from adventure.event import Event, EventMatch, EventMatchArgument, EventMatchArgumentKind
from adventure.event import EventMatchPrerequisiteKind, ItemEventMatchPrerequisite, ItemEventMatchPrerequisiteContainer, ItemEventMatchPrerequisiteContainerKind
from adventure.event import LocationEventMatchPrerequisite, EventEventMatchPrerequisite
from adventure.event import EventOutcome, EventOutcomeActionKind, PlayerEventOutcomeAction, ItemEventOutcomeAction, LocationEventOutcomeAction
from adventure.event import ItemEventOutcomeActionDestination, ItemEventOutcomeActionDestinationKind
from adventure.event_collection import EventCollection

class EventParser:

	def parse(self, event_inputs, commands_by_id, items_by_id, locations_by_id):
		events = self.parse_events(event_inputs, commands_by_id, items_by_id, locations_by_id)
		return EventCollection(events)


	def parse_events(self, event_inputs, commands_by_id, items_by_id, locations_by_id):
		events = {}

		for event_input in event_inputs:
			event, match = self.parse_event(event_input, commands_by_id, items_by_id, locations_by_id)
			match_argument_values = [argument.value for argument in match.arguments]
			match_key = (tuple([match.command] + match_argument_values))

			if not match_key in events:
				events[match_key] = []
			events[match_key].append(event)

		return events


	def parse_event(self, event_input, commands_by_id, items_by_id, locations_by_id):
		event_id = event_input["data_id"]
		attributes = int(event_input["attributes"], 16)
		match = self.parse_event_match(event_input["match"], commands_by_id, items_by_id, locations_by_id)
		outcome = self.parse_event_outcome(event_input["outcome"], items_by_id, locations_by_id)

		event = Event(event_id, attributes, match, outcome)
		return event, match


	def parse_event_match(self, event_match_input, commands_by_id, items_by_id, locations_by_id):
		command = self.get_event_match_command(event_match_input["command_id"], commands_by_id)
		arguments  = self.parse_event_match_arguments(event_match_input["arguments"], items_by_id)
		prerequisites = self.parse_event_match_prerequisites(event_match_input.get("prerequisites"), items_by_id, locations_by_id)
		return EventMatch(command, arguments, prerequisites)


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


	def parse_event_match_prerequisites(self, prerequisite_inputs, items_by_id, locations_by_id):
		if not prerequisite_inputs:
			return []

		prerequisites = []
		for prerequisite_input in prerequisite_inputs:
			prerequisite_kind_key = prerequisite_input["kind"].upper()
			prerequisite_kind = EventMatchPrerequisiteKind[prerequisite_kind_key]
			invert = prerequisite_input.get("invert", False)

			if prerequisite_kind == EventMatchPrerequisiteKind.ITEM:
				data_id = prerequisite_input["data_id"]
				item = items_by_id.get(data_id)
				container = self.parse_item_event_match_prerequisite_container(prerequisite_input["container"])
				prerequisites.append(ItemEventMatchPrerequisite(kind=prerequisite_kind, invert=invert, item=item, container=container))

			elif prerequisite_kind == EventMatchPrerequisiteKind.LOCATION:
				data_id = prerequisite_input["data_id"]
				location = locations_by_id.get(data_id)
				prerequisites.append(LocationEventMatchPrerequisite(kind=prerequisite_kind, invert=invert, location=location))

			elif prerequisite_kind == EventMatchPrerequisiteKind.EVENT:
				data_id = prerequisite_input["data_id"]
				prerequisites.append(EventEventMatchPrerequisite(kind=prerequisite_kind, invert=invert, event_id=data_id))

		return prerequisites


	def parse_item_event_match_prerequisite_container(self, container_input):
		container_kind_key = container_input["kind"].upper()
		container_kind = ItemEventMatchPrerequisiteContainerKind[container_kind_key]
		container_id = container_input.get("container_id")
		return ItemEventMatchPrerequisiteContainer(kind=container_kind, container_id=container_id)


	def parse_event_outcome(self, event_outcome_input, items_by_id, locations_by_id):
		text = event_outcome_input["text"]
		actions = self.parse_event_outcome_actions(event_outcome_input.get("actions"), items_by_id, locations_by_id)
		return EventOutcome(text, actions)


	def parse_event_outcome_actions(self, event_outcome_action_inputs, items_by_id, locations_by_id):
		if not event_outcome_action_inputs:
			return []

		actions  = []

		for event_outcome_action_input in event_outcome_action_inputs:
			kind_key = event_outcome_action_input["kind"].upper()
			kind = EventOutcomeActionKind[kind_key]

			if kind == EventOutcomeActionKind.PLAYER:
				attribute = int(event_outcome_action_input["attribute"], 16)
				on = event_outcome_action_input["on"]

				action = PlayerEventOutcomeAction(kind=kind, attribute=attribute, on=on)
				actions.append(action)

			elif kind == EventOutcomeActionKind.ITEM:
				item_id = event_outcome_action_input["item_id"]
				item = items_by_id[item_id]
				destination = self.parse_item_event_outcome_action_destination(event_outcome_action_input["destination"])

				action = ItemEventOutcomeAction(kind=kind, item=item, destination=destination)
				actions.append(action)

			elif kind == EventOutcomeActionKind.LOCATION:
				location_id = event_outcome_action_input["location_id"]
				location = locations_by_id[location_id]
				attribute = int(event_outcome_action_input["attribute"], 16)
				on = event_outcome_action_input["on"]

				action = LocationEventOutcomeAction(kind=kind, location=location, attribute=attribute, on=on)
				actions.append(action)


		return actions


	def parse_item_event_outcome_action_destination(self, item_event_outcome_action_destination_input):
		kind_key = item_event_outcome_action_destination_input["kind"].upper()
		kind = ItemEventOutcomeActionDestinationKind[kind_key]
		data_id = item_event_outcome_action_destination_input.get("data_id")
		return ItemEventOutcomeActionDestination(kind, data_id)
