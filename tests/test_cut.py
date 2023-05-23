import unittest
import cut
from cut import Length, Cutted_Length, Cutted_Stock


class Test_Single_Lengths(unittest.TestCase):

	def test_stock_of_same_length_is_not_cutted(self):
		lengths = [Length(100)]
		stock = [100]
		cutted_lengths, cutted_stock = cut.cut(lengths,stock)
		self.assertListEqual(
			cutted_lengths,
			[Cutted_Length(Length(100),[100])]
		)
		self.assertListEqual(
			cutted_stock,
			[Cutted_Stock(100,[100])]
		)
	
	def test_stock_of_twice_length_is_cutted_in_half(self):
		lengths = [Length(100)]
		stock = [200]
		cutted_lengths, cutted_stock = cut.cut(lengths,stock)
		self.assertListEqual(
			cutted_lengths,
			[Cutted_Length(Length(100,0),[100])]
		)
		self.assertListEqual(
			cutted_stock,
			[Cutted_Stock(200,[100,100])]
		)


class Test_Two_Lengths(unittest.TestCase):
	
	def test_matching_ends(self):
		lengths = [Length(150), Length(150)]
		stock = [150,150]
		cutted_lengths, cutted_stock = cut.cut(lengths,stock)
		self.assertListEqual(
			cutted_lengths,
			[Cutted_Length(Length(150),[150]), 
    		Cutted_Length(Length(150),[150])]
		)
		self.assertListEqual(
			cutted_stock,
			[
				Cutted_Stock(150,[150]),
				Cutted_Stock(150,[150])
			]
		)
	
	def test_not_matching_ends(self):
		lengths = [Length(200), Length(100)]
		stock = [150,150]
		cutted_lengths, cutted_stock = cut.cut(lengths,stock)
		self.assertListEqual(
			cutted_lengths,
			[Cutted_Length(Length(200),[150,50]), 
    		Cutted_Length(Length(100),[100])]
		)
		self.assertListEqual(
			cutted_stock,
			[
				Cutted_Stock(150,[150]),
				Cutted_Stock(150,[50,100])
			]
		)


if __name__=='__main__': unittest.main()