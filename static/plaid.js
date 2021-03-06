'use strict';
/* global Plaid */
(() => {
	async function plaidSuccess(public_token, metadata) {
		await fetch('/plaid_access_token', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			redirect: 'error',
			body: JSON.stringify({'public_token': public_token}),
		});
	}

	const plaid = Plaid.create({
		clientName: 'rudget',
		countryCodes: ['US'],
		env: window.environment,
		key: window.plaidPublicKey,
		product: ['transactions'],
		onSuccess: plaidSuccess,
		onExit: function(err, metadata) {
			if (err != null)
				console.error(err);
		},
	});

	document.querySelector('#plaid_link').addEventListener('click', (evt) => {
		evt.preventDefault();
		plaid.open();
	});
})();
