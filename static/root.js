'use strict';
(() => {
	const modal = document.querySelector('div.modal');

	function activateModal(evt) {
		evt.preventDefault();
		modal.style.display = 'flex';
	}

	document.querySelectorAll('nav a.button.modal').forEach((button) => {
		button.addEventListener('click', activateModal);
	});

	modal.addEventListener('click', (evt) => {
		if (evt.target === modal)
			modal.style.display = 'none';
	});
})();
