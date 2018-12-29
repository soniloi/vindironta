from adventure.event import EventOutcomeActionKind, ItemEventOutcomeActionDestinationKind
from adventure.item import Item
from adventure.resolver import Resolver

class EventResolver(Resolver):

	def resolve_event(self, command, player, *args):
		event = self.get_event(command, args)

		if not event:
			return False, "", list(args)

		outcome = event.outcome
		self.handle_outcome_actions(player, outcome.actions)

		return True, event.outcome.text, list(args)


	def handle_outcome_actions(self, player, actions):
		for action in actions:
			if action.kind == EventOutcomeActionKind.ITEM:
				self.handle_item_outcome_action(player, action)


	def handle_item_outcome_action(self, player, action):
		item = self.data.get_item_by_id(action.item_id)
		destination = action.destination

		if destination.kind == ItemEventOutcomeActionDestinationKind.DESTROY:
			item.destroy()

		elif destination.kind == ItemEventOutcomeActionDestinationKind.CURRENT_LOCATION:
			player.drop_item(item)

		elif destination.kind == ItemEventOutcomeActionDestinationKind.CURRENT_INVENTORY:
			player.take_item(item)


	def get_event(self, command, args):
		event_key = self.create_event_key(command, args)
		return self.data.get_event(event_key)


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
