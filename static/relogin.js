'use strict';
/* global Plaid */
(() => {
	async function relogin(plaidItemId) {
		const response = await fetch('/plaid_link_token', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			redirect: 'error',
			body: JSON.stringify({'plaid_item_id': plaidItemId}),
		});
		const linkToken = await response.json();
		const plaid = Plaid.create({
			env: window.environment,
			token: linkToken,
			onSuccess: function() {
				document.querySelector(`button[data-id="${plaidItemId}"]`).disabled = true;
			},
			onExit: function(err, metadata) {
				if (err != null)
					console.error(err);
			},
		});
		plaid.open();
	}

	for (const button of document.querySelectorAll('button.plaid_link')) {
		button.addEventListener('click', (evt) => {
			evt.preventDefault();
			const plaidItemId = button.dataset['id'];
			relogin(plaidItemId);
		});
	}
})();
