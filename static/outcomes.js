'use strict';
(async () => {
	const datePicker = document.querySelector('#date select');
	datePicker.addEventListener('change', query);

	async function query() {
		const spendingTotal = document.querySelector('#spending #spending_total');
		const transactionWrapper = document.querySelector('#regularity #transactions');
		const itemsWrapper = document.querySelector('#accounts #items');
		spendingTotal.innerHTML = '';
		transactionWrapper.innerHTML = '';
		itemsWrapper.innerHTML = '';

		let url = '/transaction_info';
		if (window.demo) {
			url += '_demo';
		}
		url += '?days=' + datePicker.value;
		const response = await fetch(url);
		const {categories, items} = await response.json();

		const total = renderCategories(categories, transactionWrapper);
		spendingTotal.innerText = formatCurrency(total);
		renderAccounts(items, itemsWrapper);
	}

	function renderCategories(categories, transactionWrapper) {
		const categoryMeta = [];
		let total = 0;

		categories.forEach((categoryInfo) => {
			const [name, periodicity, transactions] = categoryInfo;

			const bar = document.createElement('div');
			bar.classList.add('bar');

			const transactionsEl = document.createElement('section');
			transactionsEl.classList.add('category_transactions');
			let categoryTotal = 0;
			transactions.forEach((t) => {
				const transactionEl = document.createElement('div');
				transactionEl.classList.add('transaction');
				for (const text of [t.date, t.account, t.name, formatCurrency(t.amount)]) {
					const textEl = document.createElement('div');
					textEl.innerText = text;
					transactionEl.append(textEl);
				}
				transactionsEl.append(transactionEl);
				categoryTotal += t.amount;
			});

			const categoryLabel = document.createElement('div');
			categoryLabel.classList.add('line');
			categoryLabel.classList.add('category_label');
			const categoryName = document.createElement('div');
			const categoryPeriodicity = document.createElement('div');
			const categoryAmount = document.createElement('div');
			categoryName.innerText = name;
			categoryPeriodicity.innerText = periodicity.toFixed(2);
			categoryAmount.innerText = formatCurrency(categoryTotal);
			categoryLabel.append(categoryName, categoryPeriodicity, categoryAmount);
			categoryLabel.addEventListener('click', (evt) => {
				transactionsEl.classList.toggle('visible');
			});

			categoryMeta.push({'bar': bar, 'categoryTotal': categoryTotal});
			total += categoryTotal;

			transactionWrapper.append(categoryLabel, bar, transactionsEl);
		});

		let accumulator = 0;
		categoryMeta.forEach((meta) => {
			const {bar, categoryTotal} = meta;
			const catTotalEl = document.createElement('div');
			catTotalEl.classList.add('category_total');
			catTotalEl.style.marginLeft = `${accumulator / total * 100}%`;
			catTotalEl.style.width = `${categoryTotal / total * 100}%`;
			bar.append(catTotalEl);

			accumulator += categoryTotal;
		});

		return total;
	}

	function renderAccounts(items, itemsWrapper) {
		items.forEach((item) => {
			const itemName = document.createElement('div');
			itemName.classList.add('item');
			itemName.innerText = item['name'];
			itemsWrapper.append(itemName);

			item['accounts'].forEach((account) => {
				const accountName = document.createElement('div');
				const total = document.createElement('div');
				accountName.classList.add('account');
				total.classList.add('total');
				accountName.innerText = account['name'];
				if (account['total'] === null)
					total.innerText = '(skipped)';
				else
					total.innerText = formatCurrency(account['total']);
				itemsWrapper.append(accountName, total);
			});
		});
	}

	function formatCurrency(num) {
		return (num / 100).toLocaleString(undefined, {'style': 'currency', 'currency': 'USD'});
	}

	await query();
})();
