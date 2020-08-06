import datetime
import operator
import unittest

from demo_transactions import FakeCategory, FakeTransaction, account, cat_games, cat_loans
import info

today = datetime.date.today()

def ft(days, amount, name, category):
	return FakeTransaction(today - datetime.timedelta(days), amount, name, account, category)

class InfoTest(unittest.TestCase):
	def test_low(self):
		t = [
			ft(10, 779, 'Steam Games', cat_games),
			ft(30, 2499, 'Steam Games', cat_games),
			ft(100, 499, 'Steam Games', cat_games),
		]
		t.sort(key=operator.attrgetter('date'))
		result = info.transaction_info(t, [account], 11)
		regularity = result['categories'][0][1]
		assert regularity < 0.25, f'regularity was {regularity}'

	def test_low2(self):
		cat = FakeCategory('Shops, Sporting Goods')
		t = [
			ft(2,  26424, 'SPORTS BASEMENT SUNNYVALE', cat),
			ft(2,   7358, 'SPORTS BASEMENT SUNNYVALE', cat),
			ft(30,  13372, 'Summit Bicycles', cat),
			ft(73,  24381, 'MAUI DIVING SCUBA STRIPE.CO', cat),
			ft(209,   1085, 'REI', cat),
			ft(209,   3417, 'REI', cat),
			ft(212,  27768, 'REI.COM', cat),
			ft(224,  27768, 'REI', cat),
			ft(226,   2000, 'REI', cat),
			ft(230,   5701, 'SPORTS BASEMENT SAN FRANCI', cat),
			ft(236,   1386, 'SPORTS BASEMENT SAN FRANCI', cat),
			ft(291,   1651, 'SPORTS BASEMENT SAN FRANCI', cat),
			ft(366,   2924, 'REI #83 SAN FRANCISCO SAN FRANCI', cat),
			ft(377,   2924, 'REI #83 SAN FRANCISCO SAN FRANCI', cat),
			ft(411,   1568, 'SPORTS BASEMENT SAN FRANCI', cat),
			ft(419,   1451, 'SPORTS BASEMENT SAN FRANCI', cat),
			ft(419,  22785, 'THE SPORTS BASEMENT', cat),
			ft(834,  43943, 'Sports Basement', cat),
			ft(849,   8680, 'Sports Basement', cat),
		]
		t.sort(key=operator.attrgetter('date'))
		result = info.transaction_info(t, [account], 11)
		regularity = result['categories'][0][1]
		assert regularity < 0.25, f'regularity was {regularity}'

	def test_high(self):
		t = [
				ft(5, 287000, 'CENLAR Mortgage', cat_loans),
				ft(35, 287000, 'CENLAR Mortgage', cat_loans),
				ft(66, 287000, 'CENLAR Mortgage', cat_loans),
				ft(96, 287000, 'CENLAR Mortgage', cat_loans),
				ft(127, 287000, 'CENLAR Mortgage', cat_loans),
		]
		t.sort(key=operator.attrgetter('date'))
		result = info.transaction_info(t, [account], 11)
		regularity = result['categories'][0][1]
		assert regularity > 0.5, f'regularity was {regularity}'

	def test_outlier(self):
		t = [
				ft(5, 287000, 'CENLAR Mortgage', cat_loans),
				ft(35, 287000, 'CENLAR Mortgage', cat_loans),
				ft(66, 287000, 'CENLAR Mortgage', cat_loans),
				ft(96, 287000, 'CENLAR Mortgage', cat_loans),
				ft(127, 287000, 'CENLAR Mortgage', cat_loans),
				ft(10, 1500, 'outlier', cat_loans),
		]
		t.sort(key=operator.attrgetter('date'))
		result = info.transaction_info(t, [account], 11)
		regularity = result['categories'][0][1]
		assert regularity > 0.5, f'regularity was {regularity}'
