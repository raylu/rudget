#!/usr/bin/env python3

import db
import plaid

def main():
	category_ids = {}
	for category in plaid.get_categories():
		category_id = int(category['category_id'])
		hierarchy = category['hierarchy']
		*parents, name = hierarchy
		category = db.Category(category_id=category_id, name=name, full_name=', '.join(hierarchy))
		if len(parents) > 0:
			category.parent = category_ids[tuple(parents)]
		db.session.add(category)
		category_ids[tuple(hierarchy)] = category_id
	db.session.commit()

if __name__ == '__main__':
	main()
