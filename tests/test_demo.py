import unittest

import demo_transactions
import info

class DemoTest(unittest.TestCase):
	def test_demo(self):
		fake_transactions, fake_accounts = demo_transactions.data()
		info.transaction_info(fake_transactions, fake_accounts, 30)
