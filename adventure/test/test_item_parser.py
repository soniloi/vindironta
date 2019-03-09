import json
import unittest

from adventure.element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, ReplaceableItem, WearableItem
from adventure.item_parser import ItemParser
from adventure.location import Location

class TestItemParser(unittest.TestCase):

	def setUp(self):
		self.library_location = Location(80, 0x1, Labels("Library", "in the Library", ", a tall, bright room"))
		self.lighthouse_location = Location(81, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None)
		self.ash = Item(1109, 0x0, Labels("ash", "some ash", "some black ash"), 1, None)
		self.elements = {
			80 : self.library_location,
			81 : self.lighthouse_location,
			1108 : self.box,
			1109 : self.ash,
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
						\"description\": \"a book of fairytales in English. It is open on a particular page\" \
					}, \
					\"writing\": \"The Pied Piper of Hamelin\" \
				} \
			]"
		)

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		self.assertTrue("book" in collection.items_by_name)
		book = collection.items_by_name["book"]
		self.assertEqual(0x2, book.attributes)
		self.assertEqual(1, len(book.containers))
		self.assertTrue(self.library_location in book.containers)
		self.assertEqual(2, book.size)
		self.assertEqual("book", book.shortname)
		self.assertEqual("a book", book.longname)
		self.assertEqual("a book of fairytales in English. It is open on a particular page", book.description)
		self.assertEqual("The Pied Piper of Hamelin", book.writing)
		self.assertFalse(isinstance(book, ContainerItem))
		self.assertEqual(book, self.library_location.get_by_id(book.data_id))


	def test_init_different_items(self):
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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(2, len(collection.items_by_name))
		book = collection.items_by_name["book"]
		lamp = collection.items_by_name["lamp"]
		self.assertIsNot(book, lamp)


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
						\"longname\": \"some kolhrabi\", \
						\"description\": \"some kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\" \
					} \
				} \
			]"
		)

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(2, len(collection.items_by_name))
		kohlrabi = collection.items_by_name["kohlrabi"]
		cabbage = collection.items_by_name["cabbage"]
		self.assertIs(kohlrabi, cabbage)



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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		lamp = collection.items_by_name["lamp"]
		self.assertFalse(lamp.containers)


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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		self.assertTrue("water" in collection.items_by_name)
		water = collection.items_by_name["water"]
		self.assertEqual(2, len(water.containers))
		self.assertTrue(self.library_location in water.containers)
		self.assertTrue(self.lighthouse_location in water.containers)


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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		self.assertTrue("basket" in collection.items_by_name)
		basket = collection.items_by_name["basket"]
		self.assertTrue(isinstance(basket, ContainerItem))


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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		self.assertTrue("cat" in collection.items_by_name)
		cat = collection.items_by_name["cat"]
		self.assertTrue(isinstance(cat, SentientItem))


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

		collection = ItemParser().parse(item_inputs, self.elements)

		book = collection.items_by_name["book"]
		self.assertEqual(1, len(book.containers))
		self.assertTrue(self.box in book.containers)
		self.assertEqual(book, self.box.get_by_id(book.data_id))


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
					} \
				} \
			]"
		)

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		lamp = collection.items_by_name["lamp"]
		self.assertTrue(isinstance(lamp, SwitchableItem))
		self.assertEqual(lamp, lamp.switched_element)
		self.assertEqual(0x10, lamp.switched_attribute)
		self.assertEqual(2, len(lamp.state_to_text))
		self.assertEqual("off", lamp.state_to_text[False])
		self.assertEqual("on", lamp.state_to_text[True])


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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		button = collection.items_by_name["button"]
		self.assertTrue(isinstance(button, SwitchableItem))
		self.assertEqual(self.box, button.switched_element)
		self.assertEqual(0x20, button.switched_attribute)


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

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		lever = collection.items_by_name["lever"]
		self.assertTrue(isinstance(lever, SwitchableItem))
		self.assertEqual(self.library_location, lever.switched_element)
		self.assertEqual(0x40, lever.switched_attribute)


	def test_init_replaceable(self):
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
					\"replacements\": [ \
						{ \
							\"command_id\": 6, \
							\"replacement_id\": 1109 \
						} \
					] \
				} \
			]"
		)

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		paper = collection.items_by_name["paper"]
		self.assertTrue(isinstance(paper, ReplaceableItem))
		self.assertEqual(1, len(paper.replacements))
		self.assertEqual(self.ash, paper.replacements[6])


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
					\"wearing_info\": \"20\" \
				} \
			]"
		)

		collection = ItemParser().parse(item_inputs, self.elements)

		self.assertEqual(1, len(collection.items_by_name))
		suit = collection.items_by_name["suit"]
		self.assertTrue(isinstance(suit, WearableItem))
		self.assertEqual(0x20, suit.attribute_activated)


if __name__ == "__main__":
	unittest.main()
