import json
import unittest

from adventure.command import Command
from adventure.element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, UsableItem
from adventure.item_parser import ItemParser
from adventure.location import Location
from adventure.validation import Severity

class TestItemParser(unittest.TestCase):

	def setUp(self):
		self.library_location = Location(80, 0x1, Labels("Library", "in the Library", ", a tall, bright room"))
		self.lighthouse_location = Location(81, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None)
		self.ash = Item(1109, 0x2, Labels("ash", "some ash", "some black ash"), 1, None)
		self.candle = Item(1110, 0x2, Labels("candle", "a candle", "a small candle"), 2, None)
		self.kindling = Item(1111, 0x2, Labels("kindling", "some kindling", "some kindling"), 2, None)
		self.desk = Item(1112, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None)
		self.elements = {
			80 : self.library_location,
			81 : self.lighthouse_location,
			1108 : self.box,
			1109 : self.ash,
			1110 : self.candle,
			1111 : self.kindling,
			1112 : self.desk,
		}

		self.burn_command = Command(6, 0x0, 0x0, [], ["smash"],  {})
		self.non_switching_command = Command(17, 0x0, 0x0, [], ["throw"],  {})
		self.switching_command = Command(19, 0x200, 0x0, [], ["switch"],  {})
		self.commands_by_id = {
			6 : self.burn_command,
			17 : self.non_switching_command,
			19 : self.switching_command,
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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

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
		self.assertFalse(validation)


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
					\"attributes\": \"102002\", \
					\"container_ids\": [ \
						81 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"bread\" \
						], \
						\"longname\": \"a loaf of bread\", \
						\"description\": \"a loaf of brown bread\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(2, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(1, len(book_list))
		book = book_list[0]
		bread_list = collection.item_lists_by_name["bread"]
		self.assertEqual(1, len(bread_list))
		bread = bread_list[0]
		self.assertIsNot(book, bread)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(2, len(book_list))
		fairytale_book = book_list[0]
		recipe_book = book_list[1]
		self.assertIsNot(recipe_book, fairytale_book)
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(2, len(collection.item_lists_by_name))
		kohlrabi_list = collection.item_lists_by_name["kohlrabi"]
		self.assertEqual(1, len(kohlrabi_list))
		kohlrabi = kohlrabi_list[0]
		cabbage_list = collection.item_lists_by_name["cabbage"]
		self.assertEqual(1, len(cabbage_list))
		cabbage = cabbage_list[0]
		self.assertIs(kohlrabi, cabbage)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


	def test_init_item_without_container(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1106, \
					\"attributes\": \"102002\", \
					\"container_ids\": [ \
						100000 \
					], \
					\"size\": 3, \
					\"labels\": { \
						\"shortnames\": [ \
							\"bread\" \
						], \
						\"longname\": \"a loaf of bread\", \
						\"description\": \"a loaf of brown bread\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		bread_list = collection.item_lists_by_name["bread"]
		self.assertEqual(1, len(bread_list))
		bread = bread_list[0]
		self.assertFalse(bread.containers)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		water_list = collection.item_lists_by_name["water"]
		self.assertEqual(1, len(water_list))
		water = water_list[0]
		self.assertEqual(2, len(water.containers))
		self.assertTrue(self.library_location in water.containers)
		self.assertTrue(self.lighthouse_location in water.containers)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		basket_list = collection.item_lists_by_name["basket"]
		self.assertEqual(1, len(basket_list))
		basket = basket_list[0]
		self.assertTrue(isinstance(basket, ContainerItem))
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		cat_list = collection.item_lists_by_name["cat"]
		self.assertEqual(1, len(cat_list))
		cat = cat_list[0]
		self.assertTrue(isinstance(cat, SentientItem))
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		book = book_list[0]
		self.assertEqual(1, len(book.containers))
		self.assertTrue(self.box in book.containers)
		self.assertTrue(book in self.box.items)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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
					\"list_template\": \"$0 (currently $1)\", \
					\"related_command_id\": 19, \
					\"switch_info\": { \
						\"element_id\": 1201, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

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
		self.assertEqual(1, len(related_commands))
		self.assertEqual("{0} (currently {1})", lamp.list_template)
		self.assertFalse(validation)


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
					\"list_template\": \"$0 (currently $1)\", \
					\"related_command_id\": 19, \
					\"switch_info\": { \
						\"element_id\": 1108, \
						\"attribute\": \"20\", \
						\"off\": \"up\", \
						\"on\": \"down\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		button_list = collection.item_lists_by_name["button"]
		self.assertEqual(1, len(button_list))
		button = button_list[0]
		self.assertTrue(isinstance(button, SwitchableItem))
		self.assertEqual(self.box, button.switched_element)
		self.assertEqual(0x20, button.switched_attribute)
		self.assertEqual(1, len(related_commands))
		self.assertEqual("{0} (currently {1})", button.list_template)
		self.assertFalse(validation)


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
					\"list_template\": \"$0 (currently $1)\", \
					\"related_command_id\": 19, \
					\"switch_info\": { \
						\"element_id\": 80, \
						\"attribute\": \"40\", \
						\"off\": \"down\", \
						\"on\": \"up\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lever_list = collection.item_lists_by_name["lever"]
		self.assertEqual(1, len(lever_list))
		lever = lever_list[0]
		self.assertTrue(isinstance(lever, SwitchableItem))
		self.assertEqual(self.library_location, lever.switched_element)
		self.assertEqual(0x40, lever.switched_attribute)
		self.assertEqual(1, len(related_commands))
		self.assertEqual("{0} (currently {1})", lever.list_template)
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

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
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

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
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		suit_list = collection.item_lists_by_name["suit"]
		self.assertEqual(1, len(suit_list))
		suit = suit_list[0]
		self.assertTrue(isinstance(suit, UsableItem))
		self.assertEqual(0x20, suit.attribute_activated)
		self.assertEqual(0, len(related_commands))
		self.assertEqual("{0} (lugging)", suit.list_template)
		self.assertEqual("{0} (wearing)", suit.list_template_using)
		self.assertFalse(validation)


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
					\"list_template_using\": \"(sailing) $0\", \
					\"using_info\": \"40000\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		raft_list = collection.item_lists_by_name["raft"]
		self.assertEqual(1, len(raft_list))
		raft = raft_list[0]
		self.assertTrue(isinstance(raft, UsableItem))
		self.assertEqual(0x40000, raft.attribute_activated)
		self.assertEqual("(sailing) {0}", raft.list_template_using)
		self.assertEqual(0, len(related_commands))
		self.assertFalse(validation)


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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		water_list = collection.item_lists_by_name["water"]
		self.assertEqual(1, len(water_list))
		water = water_list[0]
		self.assertEqual(1, len(related_commands))
		self.assertEqual(self.non_switching_command, related_commands["water"])
		self.assertFalse(validation)


	def test_init_different_items_with_duplicate_id(self):
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
					} \
				}, \
				{ \
					\"data_id\": 1105, \
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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Multiple items found with id {0}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1105,), validation_line.args)


	def test_init_no_shortnames(self):
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
						\"shortnames\": [], \
						\"longname\": \"a book\", \
						\"description\": \"a book of fairytales in English\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(0, len(collection.item_lists_by_name))
		self.assertEqual(1, len(collection.items_by_id))
		book = collection.items_by_id[1105]
		self.assertFalse(book.shortname)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No shortnames given for item with id {0}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1105,), validation_line.args)


	def test_init_empty_writing(self):
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
						\"description\": \"a book of fairytales in English\" \
					}, \
					\"writing\": \"\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(1, len(book_list))
		book = book_list[0]
		self.assertFalse(book.writing)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Writing given for item {0} \"{1}\" is empty. To have no writing on an item, omit the field entirely.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1105, "book"), validation_line.args)


	def test_init_switchable_no_switch_info(self):
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
					\"related_command_id\": 17, \
					\"list_template\": \"$0 (currently $1)\"\
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lamp_list = collection.item_lists_by_name["lamp"]
		self.assertEqual(1, len(lamp_list))
		lamp = lamp_list[0]
		self.assertFalse(isinstance(lamp, SwitchableItem))
		self.assertEqual(1, len(related_commands))

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No switch info found for switchable item {0} \"{1}\".", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1201, "lamp"), validation_line.args)


	def test_init_non_switchable_with_switch_info(self):
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
					\"switch_info\": { \
						\"element_id\": 1105, \
						\"attribute\": \"10\", \
						\"off\": \"close\", \
						\"on\": \"open\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		book_list = collection.item_lists_by_name["book"]
		self.assertEqual(1, len(book_list))
		book = book_list[0]
		self.assertFalse(isinstance(book, SwitchableItem))
		self.assertEqual(0, len(related_commands))

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Switch info given for non-switchable item {0} \"{1}\". This switch info will not be used.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1105, "book"), validation_line.args)


	def test_init_switchable_no_related_command_id(self):
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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		lamp_list = collection.item_lists_by_name["lamp"]
		self.assertEqual(1, len(lamp_list))
		lamp = lamp_list[0]
		self.assertTrue(isinstance(lamp, SwitchableItem))
		self.assertEqual(0, len(related_commands))

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Switchable item {0} \"{1}\" missing mandatory field \"related_command_id\".", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1201, "lamp"), validation_line.args)


	def test_init_invalid_related_command(self):
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
					\"related_command_id\": 77 \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(collection.item_lists_by_name))
		water_list = collection.item_lists_by_name["water"]
		self.assertEqual(1, len(water_list))
		water = water_list[0]
		self.assertEqual(0, len(related_commands))

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Related command id {0} given for switchable item {1} \"{2}\" does not reference a valid command.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((77, 1076, "water"), validation_line.args)


	def test_init_switchable_non_switching_related_command(self):
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
					\"related_command_id\": 17, \
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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Switchable item {0} \"{1}\" has been specified with related command {2} \"{3}\", but this is not a switching command.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1201, "lamp", 17, "throw"), validation_line.args)


	def test_init_switchable_invalid_switched_element(self):
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
					\"related_command_id\": 19, \
					\"switch_info\": { \
						\"element_id\": 9999, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					}, \
					\"list_template\": \"$0 (currently $1)\"\
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Switchable item {0} \"{1}\" has invalid switched element id {2}.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1201, "lamp", 9999), validation_line.args)


	def test_init_switchable_no_list_template(self):
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
					\"related_command_id\": 19, \
					\"switch_info\": { \
						\"element_id\": 1201, \
						\"attribute\": \"10\", \
						\"off\": \"off\", \
						\"on\": \"on\" \
					} \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No list template found for switchable item {0} \"{1}\". While not mandatory, this will lead to incomplete descriptions of this item when listed.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1201, "lamp"), validation_line.args)


	def test_init_wearable_no_list_template(self):
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
					\"list_template_using\": \"$0 (wearing)\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("No list template found for wearable item {0} \"{1}\". While not mandatory, this will lead to incomplete descriptions of this item when listed.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1204, "suit"), validation_line.args)


	def test_init_usable_no_list_template_using(self):
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

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Mandatory field \"list_template_using\" not found for usable item {0} \"{1}\".", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "raft"), validation_line.args)


	def test_init_non_usable_with_list_template_using(self):
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
					\"writing\": \"The Pied Piper of Hamelin\", \
					\"list_template_using\": \"$0 (using)\" \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("Invalid field \"list_template_using\" found for item {0} \"{1}\". This field is only valid for usable items and will be ignored here.", validation_line.template)
		self.assertEqual(Severity.WARN, validation_line.severity)
		self.assertEqual((1105, "book"), validation_line.args)


	def test_init_transformable_unknown_command_id(self):
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
							\"command_id\": 9999, \
							\"replacement_id\": 1109 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("For item {0} \"{1}\", replacement command id {2} does not reference any known command.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "paper", 9999), validation_line.args)


	def test_init_transformable_unknown_replacement_id(self):
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
							\"replacement_id\": 8888 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("For item {0} \"{1}\" with replacement command {2} \"{3}\", replacement id {4} does not reference any known item.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "paper", 6, "smash", 8888), validation_line.args)


	def test_init_transformable_replacement_non_item(self):
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
							\"replacement_id\": 81 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("For item {0} \"{1}\" with replacement command {2} \"{3}\", replacement element {4} \"{5}\" is not an item.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "paper", 6, "smash", 81, "Lighthouse"), validation_line.args)


	def test_init_transformable_replaced_mobile_replacement_non_mobile(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1205, \
					\"attributes\": \"100002\", \
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
							\"replacement_id\": 1112 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("For item {0} \"{1}\" with replacement command {2} \"{3}\", the replaced item is mobile but the replacement item {4} \"{5}\" is not.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "paper", 6, "smash", 1112, "desk"), validation_line.args)


	def test_init_transformable_mobile_replacement_larger(self):
		item_inputs = json.loads(
			"[ \
				{ \
					\"data_id\": 1205, \
					\"attributes\": \"100002\", \
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
							\"replacement_id\": 1108 \
						} \
					] \
				} \
			]"
		)

		collection, related_commands, validation = ItemParser().parse(item_inputs, self.elements, self.commands_by_id)

		self.assertEqual(1, len(validation))
		validation_line = validation[0]
		self.assertEqual("For item {0} \"{1}\" with replacement command {2} \"{3}\", the replaced item is mobile but the replacement item {4} \"{5}\" is larger than the item being replaced.", validation_line.template)
		self.assertEqual(Severity.ERROR, validation_line.severity)
		self.assertEqual((1205, "paper", 6, "smash", 1108, "box"), validation_line.args)


if __name__ == "__main__":
	unittest.main()
