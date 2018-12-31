from adventure.event import EventMatchPrerequisiteKind, ItemEventMatchPrerequisiteContainerKind
from adventure.event import EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.item import Item
from adventure.item_container import ItemContainer
from adventure.resolver import Resolver

class EventResolver(Resolver):

	def resolve_event(self, command, player, *args):
		event = self.get_event(command, player, args)

		if not event:
			return False, "", list(args)

		outcome = event.outcome
		self.handle_outcome_actions(player, outcome.actions)

		return True, event.outcome.text, list(args)


	def get_event(self, command, player, args):
		event_key = self.create_event_key(command, args)
		event = self.data.get_event(event_key)

		if not event or not self.event_matches(event.match, player):
			return None

		return event


	def create_event_key(self, command, args):
		event_args = self.create_event_args(args)
		# TODO: remove the list-size workaround in favour of something more robust...
		return tuple([command] + list(event_args)[:2])


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
		if prerequisite.kind == EventMatchPrerequisiteKind.ITEM:
			item = prerequisite.item
			container_requirements = prerequisite.container
			container_kind = container_requirements.kind

			if container_kind == ItemEventMatchPrerequisiteContainerKind.ANY:
				return True

			if container_kind == ItemEventMatchPrerequisiteContainerKind.CURRENT_LOCATION:
				return player.get_location().contains(item)

		elif prerequisite.kind == EventMatchPrerequisiteKind.LOCATION:
			return prerequisite.location == player.get_location()

		return False


	def handle_outcome_actions(self, player, actions):
		for action in actions:
			if action.kind == EventOutcomeActionKind.ITEM:
				self.handle_item_outcome_action(player, action)


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
			container = self.data.get_element_by_id(destination.data_id)
			container.insert(item)

		elif destination.kind == ItemEventOutcomeActionDestinationKind.REPLACE:
			replacement =  self.data.get_item_by_id(destination.data_id)
			container = item.get_first_container()
			item.destroy()
			container.insert(replacement)
