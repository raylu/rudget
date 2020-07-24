import dataclasses
import datetime
import operator

@dataclasses.dataclass(eq=False, frozen=True)
class FakeCategory:
	full_name: str

@dataclasses.dataclass(eq=False, frozen=True)
class FakeAccount:
	name: str
	subtype: str

@dataclasses.dataclass(eq=False, frozen=True)
class FakeTransaction:
	date: datetime.date
	amount: int
	name: str
	account: FakeAccount
	category: FakeCategory

def transactions():
	today = datetime.date.today()
	account = FakeAccount('Personal', 'checking')
	cat_loans = FakeCategory('Service, Financial, Loans and Mortgages')
	cat_games = FakeCategory('Shops, Computers and Electronics, Video Games')
	cat_dept = FakeCategory('Shops, Department Stores')
	cat_venmo = FakeCategory('Transfer, Third Party, Venmo')
	cat_gas = FakeCategory('Travel, Gas Stations')
	cat_digital = FakeCategory('Shops, Digital Purchase')
	cat_cable = FakeCategory('Service, Cable')
	cat_groceries = FakeCategory('Shops, Supermarkets and Groceries')
	cat_entertainment = FakeCategory('Service, Entertainment')

	def ft(days, amount, name, category):
		return FakeTransaction(today - datetime.timedelta(days), amount, name, account, category)

	transactions = [
		ft(5, 287000, 'CENLAR Mortgage', cat_loans),
		ft(35, 287000, 'CENLAR Mortgage', cat_loans),
		ft(66, 287000, 'CENLAR Mortgage', cat_loans),
		ft(96, 287000, 'CENLAR Mortgage', cat_loans),
		ft(127, 287000, 'CENLAR Mortgage', cat_loans),
		ft(10, 779, 'Steam Games ', cat_games),
		ft(55, 1499, 'Steam Games ', cat_games),
		ft(100, 499, 'Steam Games ', cat_games),
		ft(2, 4679, 'Walmart', cat_dept),
		ft(40, 2311, 'Walmart', cat_dept),
		ft(43, 1851, 'Walmart', cat_dept),
		ft(7, 2000, 'Venmo', cat_venmo),
		ft(70, 4300, 'Venmo', cat_venmo),
		ft(90, 1000, 'Venmo', cat_venmo),
		ft(20, 3758, 'ExxonMobil', cat_gas),
		ft(50, 3815, 'Shell', cat_gas),
		ft(94, 1200, 'Shell', cat_gas),
		ft(102, 3169, 'ExxonMobil', cat_gas),
		ft(12, 1742, 'Amazon', cat_digital),
		ft(20, 511, 'Amazon', cat_digital),
		ft(23, 1200, 'DOMAINS INTERNET', cat_digital),
		ft(32, 1506, 'Etsy.com - Glitterfree', cat_digital),
		ft(52, 3594, 'Amazon', cat_digital),
		ft(10, 7498, 'Comcast', cat_cable),
		ft(40, 7498, 'Comcast', cat_cable),
		ft(71, 7498, 'Comcast', cat_cable),
		ft(102, 7498, 'Comcast', cat_cable),
		ft(132, 7498, 'Comcast', cat_cable),
		ft(23, 1089, 'NOB HILL #606', cat_groceries),
		ft(15, 8604, 'Whole Foods', cat_groceries),
		ft(8, 1034, 'Safeway', cat_groceries),
		ft(7, 3521, 'Safeway', cat_groceries),
		ft(61, 7248, 'GROCERY WEEE!', cat_groceries),
		ft(41, 1100, 'Safeway', cat_groceries),
		ft(41, 6116, 'Safeway', cat_groceries),
		ft(40, 7255, 'UNCLE FRESH INC', cat_groceries),
		ft(33, 6453, 'UNCLE FRESH INC', cat_groceries),
		ft(86, 8779, 'UNCLE FRESH INC', cat_groceries),
		ft(76, 6720, 'GROCERY WEEE!/ONROOT', cat_groceries),
		ft(72, 7259, 'UNCLE FRESH INC', cat_groceries),
		ft(28, 10082, '99 RANCH #1772', cat_groceries),
		ft(1, 5623, 'Nintendo', cat_entertainment),
	]
	transactions.sort(key=operator.attrgetter('date'))
	return transactions
