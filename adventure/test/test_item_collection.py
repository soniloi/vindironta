import unittest
from unittest.mock import Mock

from adventure.data_element import Labels
from adventure.item import ContainerItem, SentientItem, SwitchableItem, WearableItem
from adventure.item_collection import ItemCollection
from adventure.location import Location

class TestItemCollection(unittest.TestCase):

	def setUp(self):
		self.location = Location(80, 1, Labels("Library", "in the Library", ", a tall, bright room"))
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None)
		self.elements = {
			80 : self.location,
			1108 : self.box,
		}


	def test_init_single_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1105\t0x2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("book" in collection.items)
		book = collection.items["book"]
		self.assertEqual(0x2, book.attributes)
		self.assertEqual(self.location, book.container)
		self.assertEqual(2, book.size)
		self.assertEqual("book", book.shortname)
		self.assertEqual("a book", book.longname)
		self.assertEqual("a book of fairytales in English. It is open on a particular page", book.description)
		self.assertEqual("The Pied Piper of Hamelin", book.writing)
		self.assertFalse(isinstance(book, ContainerItem))
		self.assertEqual(book, self.location.get_by_id(book.data_id))


	def test_init_different_items(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1105\t0x2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin\t\t",
			"1106\t0x101A\t81\t3\tlamp\ta lamp\ta small lamp\t\t1106,10,off,on\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(2, len(collection.items))
		book = collection.items["book"]
		lamp = collection.items["lamp"]
		self.assertIsNot(book, lamp)


	def test_init_aliased_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1042\t2002\t27\t3\tkohlrabi,cabbage\tsome kohlrabi\tsome kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\t\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(2, len(collection.items))
		kohlrabi = collection.items["kohlrabi"]
		cabbage = collection.items["cabbage"]
		self.assertIs(kohlrabi, cabbage)


	def test_init_item_without_container(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1076\t22802\t1007\t1\twater\twater\tRiver Amethyst water. It is cold and clear\t\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("water" in collection.items)
		water = collection.items["water"]
		self.assertIsNone(water.container)


	def test_init_container_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1002\t3\t119\t5\tbasket\ta basket\ta large basket\t\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("basket" in collection.items)
		basket = collection.items["basket"]
		self.assertTrue(isinstance(basket, ContainerItem))


	def test_init_sentient_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1002\t80003\t119\t3\tcat\ta cat\ta black cat\t\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("cat" in collection.items)
		cat = collection.items["cat"]
		self.assertTrue(isinstance(cat, SentientItem))


	def test_init_item_with_item_container(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1105\t0x2\t1108\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin\t\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		book = collection.items["book"]
		self.assertEqual(self.box, book.container)
		self.assertEqual(book, self.box.get_by_id(book.data_id))


	def test_init_switchable_switching_self(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1201\t0x8\t81\t3\tlamp\ta lamp\ta small lamp\t\t1201,10,off,on\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		lamp = collection.items["lamp"]
		self.assertTrue(isinstance(lamp, SwitchableItem))
		self.assertEqual(lamp, lamp.switched_element)
		self.assertEqual(0x10, lamp.switched_attribute)
		self.assertEqual(2, len(lamp.state_to_text))
		self.assertEqual("off", lamp.state_to_text[False])
		self.assertEqual("on", lamp.state_to_text[True])


	def test_init_switchable_switching_other_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1202\t0x8\t81\t3\tbutton\ta button\ta red button\t\t1108,20,up,down\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		button = collection.items["button"]
		self.assertTrue(isinstance(button, SwitchableItem))
		self.assertEqual(self.box, button.switched_element)
		self.assertEqual(0x20, button.switched_attribute)


	def test_init_switchable_switching_other_location(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1203\t0x8\t81\t3\tlever\ta lever\ta mysterious lever\t\t80,40,down,up\t",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		lever = collection.items["lever"]
		self.assertTrue(isinstance(lever, SwitchableItem))
		self.assertEqual(self.location, lever.switched_element)
		self.assertEqual(0x40, lever.switched_attribute)


	def test_init_wearable(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1204\t0x400\t81\t3\tsuit\ta suit\ta space-suit\t\t\t20",
			"---",
		]

		collection = ItemCollection(reader_mock, self.elements)

		self.assertEqual(1, len(collection.items))
		suit = collection.items["suit"]
		self.assertTrue(isinstance(suit, WearableItem))
		self.assertEqual(0x20, suit.attribute_activated)


if __name__ == "__main__":
	unittest.main()
