import json
import unittest

from adventure.command import Command
from adventure.element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, UsableItem
from adventure.item_parser import ItemParser
from adventure.location import Location

class TestItemParser(unittest.TestCase):

	def setUp(self):
		self.library_location = Location(80, 0x1, Labels("Library", "in the Library", ", a tall, bright room"))
		self.lighthouse_location = Location(81, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None)
		self.ash = Item(1109, 0x0, Labels("ash", "some ash", "some black ash"), 1, None)
		self.candle = Item(1110, 0x0, Labels("candle", "a candle", "a small candle"), 2, None)
		self.kindling = Item(1111, 0x0, Labels("kindling", "some kindling", "some kindling"), 2, None)
		self.elements = {
			80 : self.library_location,
			81 : self.lighthouse_location,
			1108 : self.box,
			1109 : self.ash,
			1110 : self.candle,
			1111 : self.kindling,
		}

		self.command = Command(17, 0x0, 0x0, [], [""],  {}, {})
		self.commands_by_id = {
			17 : self.command,
		}


	def test_init_single_item(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1105, \
					\"attributes\": \"2\", \
					\"container_ids\": [ \
						80 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"book\" \
						], \
						\"longname\": \"a book\", \
						\"description\": \"a book of fairytales in English\", \
						\"extended_descriptions\": [ \
							\". It is open on a particular page\" \
						] \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(1, len(book_list))
		book = book_list[0]
		self.assertEqual(0x2, book.attributes)
		self.assertEqual(1, len(book.containers))
		self.assertTrue(self.library_location in book.containers)
		self.assertEqual(2, book.size)
		self.assertEqual("book", book.shortname)
		self.assertEqual("a book", book.longname)
		self.assertEqual("a book of fairytales in English", book.description)
		self.assertEqual([". It is open on a particular page"], book.extended_descriptions)
		self.assertEqual("The Pied Piper of Hamelin", book.writing)
		self.assertFalse(isinstance(book, ContainerItem))
		self.assertTrue(book in self.library_location.items)
		self.assertEqual(0, len(related_commands))


	def test_init_different_items_with_different_names(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1105, \
					\"attributes\": \"2\", \
					\"container_ids\": [ \
						80 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"book\" \
						], \
						\"longname\": \"a book\", \
						\"description\": \"a book of fairytales in English. It is open on a particular page\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				}, \
				{ \
					\"data_id\": 1106, \
					\"attributes\": \"101A\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"lamp\" \
						], \
						\"longname\": \"a lamp\", \
						\"description\": \"a small lamp\" \
					}, \
					\"switch_info\": { \
						\"element_id\": 1106, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(2, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(1, len(book_list))
		book = book_list[0]
		lamp_list = collection.item_lists_by_name["lamp"]
		self.assertEqual(1, len(lamp_list))
		lamp = lamp_list[0]
		self.assertIsNot(book, lamp)
		self.assertEqual(0, len(related_commands))


	def test_init_different_items_with_same_name(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1105, \
					\"attributes\": \"2\", \
					\"container_ids\": [ \
						80 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"book\" \
						], \
						\"longname\": \"a book\", \
						\"description\": \"a book of fairytales in English. It is open on a particular page\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				}, \
				{ \
					\"data_id\": 1106, \
					\"attributes\": \"2\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"book\" \
						], \
						\"longname\": \"a book\", \
						\"description\": \"a recipe book. It is open on a particular page\" \
					}, \
					\"writing\": \"How to cook stew\" \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(2, len(book_list))
		fairytale_book = book_list[0]
		recipe_book = book_list[1]
		self.assertIsNot(recipe_book, fairytale_book)


	def test_init_aliased_item(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1042, \
					\"attributes\": \"2002\", \
					\"container_ids\": [ \
						27 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"kohlrabi\", \
							\"cabbage\" \
						], \
						\"longname\": \"some kohlrabi\", \
						\"description\": \"some kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(2, len(collection.item_lists_by_name))
		kohlrabi_list = collection.item_lists_by_name["kohlrabi"]
		self.assertEqual(1, len(kohlrabi_list))
		kohlrabi = kohlrabi_list[0]
		cabbage_list = collection.item_lists_by_name["cabbage"]
		self.assertEqual(1, len(cabbage_list))
		cabbage = cabbage_list[0]
		self.assertIs(kohlrabi, cabbage)
		self.assertEqual(0, len(related_commands))



	def test_init_item_without_container(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1106, \
					\"attributes\": \"101A\", \
					\"container_ids\": [ \
						100000 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"lamp\" \
						], \
						\"longname\": \"a lamp\", \
						\"description\": \"a small lamp\" \
					}, \
					\"switch_info\": { \
						\"element_id\": 1106, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lamp_list = collection.item_lists_by_name["lamp"]
		self.assertEqual(1, len(lamp_list))
		lamp = lamp_list[0]
		self.assertFalse(lamp.containers)
		self.assertEqual(0, len(related_commands))


	def test_init_item_with_multiple_containers(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1076, \
					\"attributes\": \"22802\", \
					\"container_ids\": [ \
						80,\
						81 \
					], \
					\"size\": 1, \
					\"labels\": { \
						\"shortnames\": [ \
							\"water\" \
						], \
						\"longname\": \"water\", \
						\"description\": \"River Amethyst water. It is cold and clear\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		water_list = collection.item_lists_by_name["water"]
		self.assertEqual(1, len(water_list))
		water = water_list[0]
		self.assertEqual(2, len(water.containers))
		self.assertTrue(self.library_location in water.containers)
		self.assertTrue(self.lighthouse_location in water.containers)
		self.assertEqual(0, len(related_commands))


	def test_init_container_item(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1002, \
					\"attributes\": \"3\", \
					\"container_ids\": [ \
						119 \
					], \
					\"size\": 5, \
					\"labels\": { \
						\"shortnames\": [ \
							\"basket\" \
						], \
						\"longname\": \"a basket\", \
						\"description\": \"a large basket\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		basket_list = collection.item_lists_by_name["basket"]
		self.assertEqual(1, len(basket_list))
		basket = basket_list[0]
		self.assertTrue(isinstance(basket, ContainerItem))
		self.assertEqual(0, len(related_commands))


	def test_init_sentient_item(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1002, \
					\"attributes\": \"80003\", \
					\"container_ids\": [ \
						119 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"cat\" \
						], \
						\"longname\": \"a cat\", \
						\"description\": \"a black cat\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		cat_list = collection.item_lists_by_name["cat"]
		self.assertEqual(1, len(cat_list))
		cat = cat_list[0]
		self.assertTrue(isinstance(cat, SentientItem))
		self.assertEqual(0, len(related_commands))


	def test_init_item_with_item_container(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1105, \
					\"attributes\": \"2\", \
					\"container_ids\": [ \
						1108 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"book\" \
						], \
						\"longname\": \"a book\", \
						\"description\": \"a book of fairytales in English. It is open on a particular page\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		book = book_list[0]
		self.assertEqual(1, len(book.containers))
		self.assertTrue(self.box in book.containers)
		self.assertTrue(book in self.box.items)
		self.assertEqual(0, len(related_commands))


	def test_init_switchable_switching_self(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1201, \
					\"attributes\": \"8\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"lamp\" \
						], \
						\"longname\": \"a lamp\", \
						\"description\": \"a small lamp\" \
					}, \
					\"switch_info\": { \
						\"element_id\": 1201, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					}, \
					\"list_template\": \"$0 (currently $1)\"\
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lamp_list = collection.item_lists_by_name["lamp"]
		self.assertEqual(1, len(lamp_list))
		lamp = lamp_list[0]
		self.assertTrue(isinstance(lamp, SwitchableItem))
		self.assertEqual(lamp, lamp.switched_element)
		self.assertEqual(0x10, lamp.switched_attribute)
		self.assertEqual(2, len(lamp.state_to_text))
		self.assertEqual("off", lamp.state_to_text[False])
		self.assertEqual("on", lamp.state_to_text[True])
		self.assertEqual(0, len(related_commands))
		self.assertEqual("{0} (currently {1})", lamp.list_template)


	def test_init_switchable_switching_other_item(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1202, \
					\"attributes\": \"8\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"button\" \
						], \
						\"longname\": \"a button\", \
						\"description\": \"a red button\" \
					}, \
					\"switch_info\": { \
						\"element_id\": 1108, \
						\"attribute\": \"20\", \
						\"off\": \"up\", \
						\"on\": \"down\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		button_list = collection.item_lists_by_name["button"]
		self.assertEqual(1, len(button_list))
		button = button_list[0]
		self.assertTrue(isinstance(button, SwitchableItem))
		self.assertEqual(self.box, button.switched_element)
		self.assertEqual(0x20, button.switched_attribute)
		self.assertEqual(0, len(related_commands))


	def test_init_switchable_switching_other_location(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1203, \
					\"attributes\": \"8\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"lever\" \
						], \
						\"longname\": \"a lever\", \
						\"description\": \"a mysterious lever\" \
					}, \
					\"switch_info\": { \
						\"element_id\": 80, \
						\"attribute\": \"40\", \
						\"off\": \"down\", \
						\"on\": \"up\" \
					} \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lever_list = collection.item_lists_by_name["lever"]
		self.assertEqual(1, len(lever_list))
		lever = lever_list[0]
		self.assertTrue(isinstance(lever, SwitchableItem))
		self.assertEqual(self.library_location, lever.switched_element)
		self.assertEqual(0x40, lever.switched_attribute)
		self.assertEqual(0, len(related_commands))


	def test_init_transformable_simple(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1205, \
					\"attributes\": \"100000\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"paper\" \
						], \
						\"longname\": \"some paper\", \
						\"description\": \"some old paper\" \
					}, \
					\"transformations\": [ \
						{ \
							\"command_id\": 6, \
							\"replacement_id\": 1109 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		paper_list = collection.item_lists_by_name["paper"]
		self.assertEqual(1, len(paper_list))
		paper = paper_list[0]
		self.assertEqual(1, len(paper.transformations))
		transformation_6 = paper.transformations[6]
		self.assertIs(self.ash, transformation_6.replacement)
		self.assertIsNone(transformation_6.tool)
		self.assertIsNone(transformation_6.material)
		self.assertEqual(0, len(related_commands))


	def test_init_transformable_with_tool_with_material(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1205, \
					\"attributes\": \"100000\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 2, \
					\"labels\": { \
						\"shortnames\": [ \
							\"paper\" \
						], \
						\"longname\": \"some paper\", \
						\"description\": \"some old paper\" \
					}, \
					\"transformations\": [ \
						{ \
							\"command_id\": 6, \
							\"replacement_id\": 1109, \
							\"tool_id\": 1110, \
							\"material_id\": 1111 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		paper_list = collection.item_lists_by_name["paper"]
		self.assertEqual(1, len(paper_list))
		paper = paper_list[0]
		self.assertEqual(1, len(paper.transformations))
		transformation_6 = paper.transformations[6]
		self.assertIs(self.ash, transformation_6.replacement)
		self.assertIs(self.candle, transformation_6.tool)
		self.assertIs(self.kindling, transformation_6.material)
		self.assertEqual(0, len(related_commands))


	def test_init_wearable(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1204, \
					\"attributes\": \"400\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"suit\" \
						], \
						\"longname\": \"a suit\", \
						\"description\": \"a space-suit\" \
					}, \
					\"using_info\": \"20\", \
					\"list_template\": \"$0 (lugging)\", \
					\"list_template_using\": \"$0 (wearing)\" \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		suit_list = collection.item_lists_by_name["suit"]
		self.assertEqual(1, len(suit_list))
		suit = suit_list[0]
		self.assertTrue(isinstance(suit, UsableItem))
		self.assertEqual(0x20, suit.attribute_activated)
		self.assertEqual(0, len(related_commands))
		self.assertEqual("{0} (lugging)", suit.list_template)
		self.assertEqual("{0} (wearing)", suit.list_template_using)


	def test_init_sailable(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1205, \
					\"attributes\": \"10000\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"raft\" \
						], \
						\"longname\": \"a raft\", \
						\"description\": \"a rickety raft\" \
					}, \
					\"using_info\": \"40000\" \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		raft_list = collection.item_lists_by_name["raft"]
		self.assertEqual(1, len(raft_list))
		raft = raft_list[0]
		self.assertTrue(isinstance(raft, UsableItem))
		self.assertEqual(0x40000, raft.attribute_activated)
		self.assertEqual(0, len(related_commands))


	def test_init_item_with_related_command(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1076, \
					\"attributes\": \"22802\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 1, \
					\"labels\": { \
						\"shortnames\": [ \
							\"water\" \
						], \
						\"longname\": \"water\", \
						\"description\": \"River Amethyst water. It is cold and clear\" \
					}, \
					\"related_command_id\": 17 \
				} \
			]"
		)

		collection, related_commands = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		water_list = collection.item_lists_by_name["water"]
		self.assertEqual(1, len(water_list))
		water = water_list[0]
		self.assertEqual(1, len(related_commands))
		self.assertEqual(self.command, related_commands["water"])


if __name__ == "__main__":
	unittest.main()
