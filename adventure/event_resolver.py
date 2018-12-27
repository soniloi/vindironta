from adventure.resolver import Resolver
from adventure.item import Item
class EventResolver(Resolver):

	def resolve_event(self, command, player, *args):
		event_key = tuple([command] + list(args))
		event = self.data.get_event(event_key)

		if not event:
			return False, "", list(args)

		return True, event.outcome.text, list(args)
