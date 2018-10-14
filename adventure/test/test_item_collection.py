import unittest
from unittest.mock import Mock

from adventure.item import ContainerItem
from adventure.item_collection import ItemCollection
from adventure.location import Location

class TestItemCollection(unittest.TestCase):

	def setUp(self):
		self.location = Location(80, 1, "Library", "in the Library", ", a tall, bright room")
		self.box = ContainerItem(1108, 0x3, "box", "a box", "a small box", 3, None)
		self.containers = {
			80 : self.location,
			1108 : self.box,
		}


	def test_init_single_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1105\t0x2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

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
			"1105\t0x2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
			"1106\t0x101A\t81\t3\tlamp\ta lamp\ta small lamp\t0",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

		self.assertEqual(2, len(collection.items))
		book = collection.items["book"]
		lamp = collection.items["lamp"]
		self.assertIsNot(book, lamp)


	def test_init_aliased_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1042\t2002\t27\t3\tkohlrabi,cabbage\tsome kohlrabi\tsome kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\t0",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

		self.assertEqual(2, len(collection.items))
		kohlrabi = collection.items["kohlrabi"]
		cabbage = collection.items["cabbage"]
		self.assertIs(kohlrabi, cabbage)


	def test_init_item_without_container(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1076\t22802\t1007\t1\twater\twater\tRiver Amethyst water. It is cold and clear\t0",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("water" in collection.items)
		water = collection.items["water"]
		self.assertIsNone(water.container)


	def test_init_container_item(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1002\t3\t119\t5\tbasket\ta\tbasket\ta\tlarge basket\t0",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

		self.assertEqual(1, len(collection.items))
		self.assertTrue("basket" in collection.items)
		basket = collection.items["basket"]
		self.assertTrue(isinstance(basket, ContainerItem))


	def test_init_item_with_item_container(self):
		reader_mock = Mock()
		reader_mock.read_line.side_effect = [
			"1105\t0x2\t1108\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
			"---",
		]

		collection = ItemCollection(reader_mock, self.containers)

		book = collection.items["book"]
		self.assertEqual(self.box, book.container)
		self.assertEqual(book, self.box.get_by_id(book.data_id))


if __name__ == "__main__":
	unittest.main()
