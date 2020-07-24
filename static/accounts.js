'use strict';
(() => {
	document.querySelectorAll('h2.account_name').forEach((h2) => {
		h2.addEventListener('click', accountNameClick);
		h2.addEventListener('keydown', accountNameKey);
		h2.addEventListener('blur', accountNameBlur);
	});

	function accountNameClick(evt) {
		if (evt.target.contentEditable == 'false') {
			evt.target.contentEditable = 'true';
			evt.target.classList.add('editing');
			if (evt.target.innerText == '(unnamed)') {
				evt.target.innerText = '';
			}
			evt.target.focus();
		}
	}

	async function accountNameKey(evt) {
		if (evt.key == 'Enter') {
			evt.preventDefault();
			await updateName(evt.target);
		}
	}

	async function accountNameBlur(evt) {
		if (evt.target.classList.contains('editing')) {
			await updateName(evt.target);
		}
	}

	async function updateName(el) {
		el.contentEditable = 'false';
		el.classList.remove('editing');
		let text = el.innerText.trim();
		if (text == '') {
			text = '(unnamed)';
		}
		el.innerText = text;

		await fetch('/accounts/update', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			redirect: 'error',
			body: JSON.stringify({'plaid_item_id': el.dataset['id'], 'name': text}),
		});
	}
})();
