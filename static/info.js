'use strict';
(async () => {
	const response = await fetch('/transaction_info');
	const categories = await response.json();
	const infoEl = document.querySelector('#info');
	categories.forEach((categoryInfo) => {
		const [name, periodicity, transactions] = categoryInfo;

		const transactionsEl = document.createElement('div');
		transactionsEl.classList.add('category_transactions');
		let categoryTotal = 0;
		transactions.forEach((t) => {
			const transactionEl = document.createElement('div');
			transactionEl.innerText = `${t.date} ${t.name} $${(t.amount/100).toLocaleString()}`;
			transactionsEl.append(transactionEl);
			categoryTotal += t.amount;
		});

		const h2 = document.createElement('h2');
		h2.innerText = `${name} $${(categoryTotal/100).toLocaleString()}`;
		h2.addEventListener('click', (evt) => {
			transactionsEl.classList.toggle('visible');
		});

		infoEl.append(h2, `Periodicity: ${periodicity.toFixed(2)}`, transactionsEl);
	});
})();
