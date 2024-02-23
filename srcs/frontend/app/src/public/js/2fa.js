import { fetchTemplate, loadProfileCss, changeUrlHistory } from "./pageUtils.js";


function inputsEvents(inputs) {
	inputs.forEach((input, index) => {
        input.addEventListener('input', () => {
            if (input.value) {
                const nextInput = inputs[index + 1];
                if (nextInput) {
                    nextInput.focus();
                }
            }
        });
		input.addEventListener('keydown', (event) => {
            if (event.key === 'Backspace' && input.value === '') {
				for (let i = index; i < inputs.length - 1; i++) {
                    inputs[i].value = inputs[i + 1].value;
                    inputs[i + 1].value = '';
                }
				const previousInput = inputs[index - 1];
                if (previousInput && !inputs[index].value) {
                    previousInput.focus();
                }
            }
        });
		input.addEventListener('keypress', function (event) {
			if (!/\d/.test(event.key)) {
				event.preventDefault();
			}
		});
    });
}

function enterValidate(inputs) {
	document.addEventListener('keydown', (event) => {
		if (event.key === 'Enter') {
			const allFilled = inputs.every(input => input.value !== '');
			if (allFilled) {
				console.log('All filled');
			}
		}
	});
}

function addEventListeners() {
	const inputs = Array.from(document.querySelectorAll('input'));
	inputsEvents(inputs);
	enterValidate(inputs);
}

export async function get2FAPage() {
	// if (!sessionStorage.getItem("2fa_token")) {
	// 	window.location.replace("/login");
	// 	return;
	// }
    const template = await fetchTemplate("/public/html/2fa.html");
	document.getElementById("main").innerHTML = template;
	loadProfileCss("/public/css/2fa.css");
	addEventListeners();
	changeUrlHistory("/2fa");
}