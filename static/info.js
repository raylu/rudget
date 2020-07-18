'use strict';
(async () => {
	const response = await fetch('/transaction_info');
	const categories = await response.json();

	const categoryMeta = [];
	let total = 0;

	const infoEl = document.querySelector('#info');
	categories.forEach((categoryInfo) => {
		const [name, periodicity, transactions] = categoryInfo;

		const bar = document.createElement('div');
		bar.classList.add('bar');

		const transactionsEl = document.createElement('div');
		transactionsEl.classList.add('category_transactions');
		let categoryTotal = 0;
		transactions.forEach((t) => {
			const transactionEl = document.createElement('div');
			transactionEl.innerText = `${t.date} ${t.name} ${formatCurrency(t.amount/100)}`;
			transactionsEl.append(transactionEl);
			categoryTotal += t.amount;
		});

		const h2 = document.createElement('h2');
		h2.innerText = `${name} ${formatCurrency(categoryTotal/100)}`;
		h2.addEventListener('click', (evt) => {
			transactionsEl.classList.toggle('visible');
		});

		categoryMeta.push({'bar': bar, 'categoryTotal': categoryTotal});
		total += categoryTotal;

		infoEl.append(h2, `Periodicity: ${periodicity.toFixed(2)}`, bar, transactionsEl);
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
