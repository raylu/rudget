'use strict';
(async () => {
	let url = '/transaction_info';
	if (window.demo) {
		url += '_demo';
	}
	const response = await fetch(url);
	const categories = await response.json();

	const categoryMeta = [];
	let total = 0;

	const infoEl = document.querySelector('#info');
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
			for (const text of [t.date, t.account, t.name, formatCurrency(t.amount/100)]) {
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
		categoryAmount.innerText = formatCurrency(categoryTotal/100);
		categoryLabel.append(categoryName, categoryPeriodicity, categoryAmount);
		categoryLabel.addEventListener('click', (evt) => {
			transactionsEl.classList.toggle('visible');
		});

		categoryMeta.push({'bar': bar, 'categoryTotal': categoryTotal});
		total += categoryTotal;

		infoEl.append(categoryLabel, bar, transactionsEl);
	});

	let accumulator = 0;
	categoryMeta.forEach((meta) => {
		const {bar, categoryTotal} = meta;
		const accumulatorEl = document.createElement('div');
		accumulatorEl.classList.add('accumulated');
		accumulatorEl.style.width = `${accumulator / total * 600}px`;
		const catTotalEl = document.createElement('div');
		catTotalEl.classList.add('category_total');
		catTotalEl.style.width = `${categoryTotal / total * 600}px`;
		bar.append(accumulatorEl, catTotalEl);

		accumulator += categoryTotal;
	});

	function formatCurrency(num) {
		return num.toLocaleString(undefined, {'style': 'currency', 'currency': 'USD'});
	}
})();
