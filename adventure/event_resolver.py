from adventure.event import EventMatchPrerequisiteKind, ItemEventMatchPrerequisiteContainerKind
from adventure.event import EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.item import Item
from adventure.item_container import ItemContainer
from adventure.resolver import Resolver

class EventResolver(Resolver):

	def resolve_event(self, command, player, *args):
		content_args = list(args)
		next_args = list(args)

		event = self.get_event(command, player, args)

		if not event:
			return True, [], content_args, []

		outcome = event.outcome
		self.handle_outcome_actions(player, outcome.actions)
		self.update_player_outcomes(player, event)

		return True, [event.outcome.text_key], content_args, next_args


	def get_event(self, command, player, args):
		event_key = self.create_event_key(command, args)
		events = self.data.get_events(event_key)

		if events:
			for event in events:
				if self.event_matches(event.match, player):
					return event

		return None


	def create_event_key(self, command, args):
		event_args = self.create_event_args(args)
		return tuple([command] + list(event_args))


	def create_event_args(self, args):
		event_args = []

		for arg in args:
			if isinstance(arg, Item):
				event_args.append(arg.get_original())
			else:
				event_args.append(arg)

		return event_args


	def event_matches(self, match, player):
		for prerequisite in match.prerequisites:

			if not self.event_meets_prerequisites(prerequisite, player):
				return False

		return True


	def event_meets_prerequisites(self, prerequisite, player):
		condition_met = False

		if prerequisite.kind == EventMatchPrerequisiteKind.ITEM:
			item = prerequisite.item
			container_requirements = prerequisite.container
			container_kind = container_requirements.kind

			if container_kind == ItemEventMatchPrerequisiteContainerKind.ANY:
				condition_met = True

			if container_kind == ItemEventMatchPrerequisiteContainerKind.CURRENT_LOCATION:
				condition_met = player.get_location().contains(item)

		elif prerequisite.kind == EventMatchPrerequisiteKind.LOCATION:
			condition_met = prerequisite.location == player.get_location()

		elif prerequisite.kind == EventMatchPrerequisiteKind.EVENT:
			condition_met = player.has_completed_event(prerequisite.event_id)

		return condition_met ^ prerequisite.invert


	def handle_outcome_actions(self, player, actions):
		for action in actions:
			if action.kind == EventOutcomeActionKind.PLAYER:
				self.handle_player_outcome_action(player, action)
			elif action.kind == EventOutcomeActionKind.ITEM:
				self.handle_item_outcome_action(player, action)
			elif action.kind == EventOutcomeActionKind.LOCATION:
				self.handle_location_outcome_action(player, action)
			elif action.kind == EventOutcomeActionKind.LINK:
				self.handle_link_outcome_action(player, action)
			elif action.kind == EventOutcomeActionKind.DESCRIPTION:
				self.handle_description_outcome_action(player, action)


	def handle_player_outcome_action(self, player, action):
		if action.on:
			player.set_attribute(action.attribute)
		else:
			player.unset_attribute(action.attribute)


	def handle_item_outcome_action(self, player, action):
		item = action.item
		destination = action.destination

		if destination.kind == ItemEventOutcomeActionDestinationKind.DESTROY:
			item.destroy()

		elif destination.kind == ItemEventOutcomeActionDestinationKind.CURRENT_LOCATION:
			player.drop_item(item)

		elif destination.kind == ItemEventOutcomeActionDestinationKind.CURRENT_INVENTORY:
			player.take_item(item)

		elif destination.kind == ItemEventOutcomeActionDestinationKind.ABSOLUTE_CONTAINER:
			if not item.is_copyable():
				item.remove_from_containers()

			# TODO: handle case where container is ContainerItem and already contains something
			container = destination.named_data_element
			container.insert(item)

		elif destination.kind == ItemEventOutcomeActionDestinationKind.REPLACE:
			container = item.get_first_container()
			item.destroy()
			container.insert(destination.named_data_element)


	def handle_location_outcome_action(self, player, action):
		location = action.location
		if action.on:
			location.set_attribute(action.attribute)
		else:
			location.unset_attribute(action.attribute)


	def handle_link_outcome_action(self, player, action):
		source = action.source
		destination = action.destination
		direction = action.direction

		if destination:
			source.directions[direction] = destination
		else:
			source.directions.pop(direction, None)


	def handle_description_outcome_action(self, player, action):
		action.named_data_element.extended_description_index = action.extended_description_index


	def update_player_outcomes(self, player, event):
		player.complete_event(event.data_id)

		if event.is_end_game():
			player.set_playing(False)

		if event.is_puzzle():
			player.solve_puzzle(event.data_id)
