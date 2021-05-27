from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Date, ForeignKey, Integer, String, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

engine = create_engine('postgresql://rudget@/rudget', echo=False)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

Base = declarative_base()
Base.query = session.query_property()

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

class User(Base):
	__tablename__ = 'users'

	user_id = Column(Integer, primary_key=True)
	email = Column(String, nullable=False, unique=True)
	password = Column(String, nullable=False)

	@classmethod
	def register(cls, email, password):
		user = User(email=email.casefold(), password=pwd_context.hash(password))
		session.add(user)
		return user

	@classmethod
	def login(cls, email, password):
		user = User.query.filter(User.email == email.casefold()).one()
		if pwd_context.verify(password, user.password):
			return user

class PlaidItem(Base):
	__tablename__ = 'plaid_items'

	plaid_item_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	item_id = Column(String, nullable=False, unique=True)
	access_token = Column(String, nullable=False, unique=True)
	name = Column(String, nullable=True)

	user = relationship(User)
	accounts = relationship('PlaidAccount')

class PlaidAccount(Base):
	__tablename__ = 'plaid_accounts'

	plaid_account_id = Column(Integer, primary_key=True)
	plaid_item_id = Column(Integer, ForeignKey('plaid_items.plaid_item_id'), nullable=False)
	account_id = Column(String, nullable=False, unique=True)
	name = Column(String, nullable=False)
	mask = Column(String, nullable=True)
	subtype = Column(String, nullable=False)

	item = relationship(PlaidItem)

class PlaidTransaction(Base):
	__tablename__ = 'plaid_transactions'

	plaid_transaction_id = Column(Integer, primary_key=True)
	plaid_account_id = Column(Integer, ForeignKey('plaid_accounts.plaid_account_id'), nullable=False)
	transaction_id = Column(String, nullable=False, unique=True)
	date = Column(Date, nullable=False)
	name = Column(Unicode, nullable=False)
	amount = Column(Integer, nullable=False)
	category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)

	account = relationship(PlaidAccount)
	category = relationship('Category')

class Category(Base):
	__tablename__ = 'categories'

	category_id = Column(Integer, primary_key=True)
	parent = Column(Integer, ForeignKey('categories.category_id'), nullable=True)
	name = Column(Unicode, nullable=False)
	full_name = Column(Unicode, nullable=False)

if __name__ == '__main__':
	Base.metadata.create_all(engine)
