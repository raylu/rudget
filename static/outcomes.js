'use strict';
/* global d3 c3 */
(async () => {
	const datePicker = document.querySelector('#date select');
	datePicker.addEventListener('change', query);

	const regularityGroups = document.querySelectorAll('#regularity #transactions > div');
	const regularityHeaders = document.querySelectorAll('#regularity #regularity_groups > div.group_header');
	regularityHeaders.forEach((header, i) => {
		header.addEventListener('click', (evt) => {
			regularityHeaders.forEach((rg) => {
				rg.classList.remove('active');
			});
			regularityGroups.forEach((rg) => {
				rg.classList.remove('active');
			});
			header.classList.add('active');
			regularityGroups[i].classList.add('active');
		});
	});

	const chart = c3.generate({
		'bindto': '#chart',
		'data': {
			'type': 'bar',
			'x': 'x',
			'xFormat': '%Y-%m',
			'columns': [],
			colors: {
				low: '#5555ff',
				medium: '#8888ee',
				high: '#aaaadd',
			},
		},
		'axis': {
			'x': {
				'type': 'timeseries',
				'tick': {'format': '%Y-%m'},
			},
			'y': {
				'tick': {'format': d3.format('$,')},
			},
		},
	});

	async function query() {
		const spendingTotal = document.querySelector('#spending #spending_total');
		const itemsWrapper = document.querySelector('#accounts #items');
		spendingTotal.innerHTML = '';
		itemsWrapper.innerHTML = '';
		regularityHeaders.forEach((rh) => {
			rh.querySelector('div.group_total').innerText = '';
			rh.querySelector('span.group_transactions').innerText = '';
		});
		regularityGroups.forEach((rg) => {
			rg.innerHTML = '';
		});
		chart.unload({'ids': ['x', 'low', 'medium', 'high']});

		let url = '/transaction_info';
		if (window.demo) {
			url += '_demo';
		}
		url += '?days=' + datePicker.value;
		const response = await fetch(url);
		const {categories, items, months} = await response.json();

		renderChart(months);
		const total = renderCategories(categories);
		spendingTotal.innerText = formatCurrency(total);
		renderAccounts(items, itemsWrapper);
	}

	function renderChart(months) {
		const sorted = Object.keys(months).sort();
		const columns = [['low'], ['medium'], ['high']];
		for (const month of sorted) {
			const monthData = months[month];
			columns.forEach((col, i) => {
				col.push(monthData[i]);
			});
		}
		columns.push(['x'].concat(sorted));
		chart.load({'columns': columns});
		chart.groups([['low', 'medium', 'high']]);
	}

	function renderCategories(categories) {
		const categoryMeta = [];
		const groupTotals = [0, 0, 0];
		const groupTransactions = [0, 0, 0];
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

			let group;
			if (periodicity >= 0.5)
				group = 2;
			else if (periodicity >= 0.25)
				group = 1;
			else
				group = 0;
			regularityGroups[group].append(categoryLabel, bar, transactionsEl);
			groupTotals[group] += categoryTotal;
			groupTransactions[group] += transactions.length;
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

		regularityHeaders.forEach((header, i) => {
			header.querySelector('div.group_total').innerText = formatCurrency(groupTotals[i]);
			header.querySelector('span.group_transactions').innerText = groupTransactions[i];
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
				const mask = document.createElement('div');
				const subtype = document.createElement('div');
				accountName.classList.add('account');
				total.classList.add('total');
				mask.classList.add('mask');
				subtype.classList.add('subtype');
				accountName.innerText = account['name'];
				if (account['total'] === null)
					total.innerText = '(skipped)';
				else
					total.innerText = formatCurrency(account['total']);
				mask.innerText = `(${account['mask']})`;
				subtype.innerText = account['subtype'];
				itemsWrapper.append(accountName, total, mask, subtype);
			});
		});
	}

	function formatCurrency(num) {
		return (num / 100).toLocaleString(undefined, {'style': 'currency', 'currency': 'USD'});
	}

	await query();
})();
