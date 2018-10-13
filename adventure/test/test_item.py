import unittest

from adventure.item import Item, ContainerItem

class TestItem(unittest.TestCase):

	def setUp(self):
		self.book = Item(1105, 0x2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.desk = Item(1106, 0x20000, "desk", "a desk", "a large mahogany desk", 6, None)
		self.basket = ContainerItem(1107, 0x3, "basket", "a basket", "a large basket", 6, None)


	def test_get_list_name_simple(self):
		self.assertEqual("\n\ta book", self.book.get_list_name())


	def test_get_list_name_simple_indented(self):
		self.assertEqual("\n\t\t\ta book", self.book.get_list_name(3))


	def test_get_non_silent_list_name_simple_silent_item(self):
		self.assertEqual("", self.desk.get_non_silent_list_name())


	def test_get_non_silent_list_name_simple_non_silent_item(self):
		self.assertEqual("\n\ta book", self.book.get_non_silent_list_name())


	def test_get_list_name_container_empty(self):
		self.assertEqual("\n\ta basket (---)", self.basket.get_list_name())


	def test_get_list_name_container_nonempty(self):
		self.basket.insert(self.book)

		self.assertEqual("\n\ta basket +\n\t\ta book", self.basket.get_list_name())


if __name__ == "__main__":
	unittest.main()
