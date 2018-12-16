import unittest
from unittest.mock import Mock

from adventure.puzzle_resolver import PuzzleResolver
from adventure.data_element import Labels
from adventure.item import Item, ContainerItem

class TestPuzzleResolver(unittest.TestCase):

	def setUp(self):

		self.data = Mock()
		self.data.get_response.side_effect = self.responses_side_effect
		self.data.get_item_by_id.side_effect = self.items_by_id_side_effect

		self.bean = Item(1003, 0x2, Labels("bean", "a bean", "a small bean"), 2, None)
		self.bottle = ContainerItem(1108, 0x203, Labels("bottle", "a bottle", "a small bottle"), 3, None)
		self.plant = Item(1058, 0x2, Labels("plant", "a plant", "a green plant"), 2, None)
		self.potion = Item(1059, 0x902, Labels("potion", "some potion", "some mysterious potion"), 2, None)
		self.item_by_id_map = {
			1003 : self.bean,
			1058 : self.plant,
			1059 : self.potion,
		}

		self.response_map = {
			"event_potion_bean" : "The bean turns into a plant.",
			"event_potion_plant" : "The plant turns into a bean.",
		}

		self.command = Mock()
		self.player = Mock()

		self.resolver = PuzzleResolver()
		self.resolver.init_data(self.data)


	def items_by_id_side_effect(self, *args):
		return self.item_by_id_map.get(args[0])


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def test_handle_pour_potion_bean(self):
		success, template, content = self.resolver.handle_pour(self.command, self.player, self.potion, self.bean, self.bottle)

		self.assertTrue(success)
		self.assertEqual("The bean turns into a plant.", template)
		self.assertEqual([self.potion, self.bean, self.bottle], content)
		self.player.drop_item.assert_called_with(self.plant)


	def test_handle_pour_potion_plant(self):
		success, template, content = self.resolver.handle_pour(self.command, self.player, self.potion, self.plant, self.bottle)

		self.assertTrue(success)
		self.assertEqual("The plant turns into a bean.", template)
		self.assertEqual([self.potion, self.plant, self.bottle], content)
		self.player.drop_item.assert_called_with(self.bean)


if __name__ == "__main__":
	unittest.main()
