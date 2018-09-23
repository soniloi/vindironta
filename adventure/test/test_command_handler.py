import unittest
from unittest.mock import patch

from adventure.command_handler import CommandHandler
from adventure import item_collection
from adventure.item import Item
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.handler = CommandHandler()
		with patch(item_collection.__name__ + ".ItemCollection") as item_collection_mock:
			self.item_collection_mock_instance = item_collection_mock.return_value
			self.item_collection_mock_instance.get.side_effect = self.item_side_effect
			self.handler.init_data(None, self.item_collection_mock_instance)

		self.location = Location(11, 0, "Mines", "in the mines", ". There are dark passages everywhere")
		self.player = Player(self.location)
		self.book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.lamp = Item(1043, 0x101A, "lamp", "a lamp", "a small hand-held lamp", 2, None)
		self.kohlrabi = Item(1042, 0x2002, "kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar", 3, None)

		self.item_map = {
			"book" : self.book,
			"kohlrabi" : self.kohlrabi,
			"lamp" : self.lamp,
		}


	def item_side_effect(self, *args):
		item_id = args[0]
		if item_id in self.item_map:
			return self.item_map[item_id]
		return None


	def test_handle_drop_unknown(self):
		response = self.handler.handle_drop(self.player, "biscuit")

		self.assertEqual("I do not know who or what that is.", response)


	def test_handle_drop_known_not_in_inventory(self):
		response = self.handler.handle_drop(self.player, "book")

		self.assertEqual("You do not have the book.", response)
		self.assertFalse(self.player.is_carrying(self.book))


	def test_handle_drop_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_drop(self.player, "lamp")

		self.assertEqual("Dropped.", response)
		self.assertFalse(self.player.is_carrying(self.lamp))


	def test_handle_inventory(self):
		response = self.handler.handle_inventory(self.player, "")

		self.assertEqual("You are not holding anything.", response)


	def test_handle_look(self):
		response = self.handler.handle_look(self.player, "")

		self.assertEqual("You are in the mines. There are dark passages everywhere.", response)


	def test_handle_quit(self):
		response = self.handler.handle_quit(self.player, "")

		self.assertEqual("Game has ended", response)
		self.assertFalse(self.player.playing)


	def test_handle_score(self):
		response = self.handler.handle_score(self.player, "")

		self.assertEqual("Your current score is 0 points", response)


	def test_handle_take_unknown(self):
		response = self.handler.handle_take(self.player, "biscuit")

		self.assertEqual("I do not know who or what that is.", response)


	def test_handle_take_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_take(self.player, "lamp")

		self.assertEqual("You already have the lamp.", response)
		self.assertTrue(self.player.is_carrying(self.lamp))


	def test_handle_take_known_absent(self):
		response = self.handler.handle_take(self.player, "kohlrabi")

		self.assertEqual("I see no kohlrabi here.", response)


	def test_handle_take_known_at_location(self):
		self.location.insert(self.book)

		response = self.handler.handle_take(self.player, "book")

		self.assertEqual("Taken.", response)
		self.assertTrue(self.player.is_carrying(self.book))


if __name__ == "__main__":
	unittest.main()
