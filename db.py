import sqlalchemy
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Date, ForeignKey, Integer, String, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

engine = create_engine('postgres://rudget@/rudget')
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

Base = declarative_base()

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

class User(Base):
	__tablename__ = 'users'

	user_id = Column(Integer, primary_key=True)
	email = Column(String)
	password = Column(String)

	#items = relationship('PlaidItem')

	@classmethod
	def register(cls, email, password):
		user = User(email=email.casefold(), password=pwd_context.hash(password))
		session.add(user)
		return user

	@classmethod
	def login(cls, email, password):
		user = User.query.filter(email=email.casefold()).one()
		if pwd_context.verify(password, user.password):
			return user

class PlaidItem(Base):
	__tablename__ = 'plaid_items'

	plaid_item_id = Column(Integer, primary_key=True)
	plaid_user_id = Column(Integer, ForeignKey('users.user_id'))
	item_id = Column(String)
	access_token = Column(String)

	#accounts = relationship('PlaidAccount')

class PlaidAccount(Base):
	__tablename__ = 'plaid_accounts'

	plaid_account_id = Column(Integer, primary_key=True)
	plaid_item_id = Column(Integer, ForeignKey('plaid_items.plaid_item_id'))

	#transactions = relationship('PlaidTransactions')

class PlaidTransaction(Base):
	__tablename__ = 'plaid_transactions'

	plaid_transaction_id = Column(Integer, primary_key=True)
	plaid_account_id = Column(Integer, ForeignKey('plaid_accounts.plaid_account_id'))
	transaction_id = Column(String)
	date = Column(Date)
	name = Column(Unicode)
	amount = Column(Integer)
	category = Column(Integer)

class Category(Base):
	__tablename__ = 'categories'

	category_id = Column(Integer, primary_key=True)
	parent = Column(Integer, ForeignKey('categories.category_id'))
	name = Column(Unicode)

if __name__ == '__main__':
	Base.metadata.create_all(engine)
