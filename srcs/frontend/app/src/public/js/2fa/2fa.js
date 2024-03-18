import { api_url, router } from "../main.js";
import { fetchTemplate, loadProfileCss, changeUrlHistory, postData, delProfileCss, addEventListenerDOMElem, addEventListenerByIdPreventDouble } from "../pageUtils.js";

let keydownHandler = null;

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

function enterValidate(inputs, button) {
    keydownHandler = (event) => {
        if (event.key === 'Enter') {
            const allFilled = inputs.every(input => input.value !== '');
            if (allFilled) {
                button.click();
            }
        }
    };
    document.addEventListener('keydown', keydownHandler);
}

function removeEnterValidate() {
    if (keydownHandler) {
        document.removeEventListener('keydown', keydownHandler);
        keydownHandler = null;
    }
}

async function buttonValidate(inputs, button) {
	addEventListenerDOMElem(button ,'click', async () => {
		let combinedValue = inputs.map(input => input.value).join('');
		const data = {
			"token": sessionStorage.getItem("2fa_token"),
			"code": combinedValue,
		}
		let errmsg = document.getElementById("2fa-err")
		const response = await postData(api_url + "mail/2fa/", data)
		if (response.ok) {
			errmsg.textContent = "";
			sessionStorage.removeItem("2fa_token");
			removeEnterValidate();
			setTimeout(() => {
				router("/home");
			}, 1000);
		} else {
			handle2FAValidationErrors(response, errmsg);
		}
	});
}

async function handle2FAValidationErrors(response, errmsg) {
	let data = null;
	try {
		data = await response.json();
	} catch (error) {
		return ;
	}
	if (data && 'non_field_errors' in data) {
		if (data['non_field_errors'][0] === "2FA code expired.") {
			console.log("2FA code expired.");
			sessionStorage.removeItem("2fa_token");
			removeEnterValidate();
			router("/login");
		} else if (data['non_field_errors'][0] === "Invalid 2FA code.") {
			console.log("Invalid 2FA code.");
			errmsg.textContent = "Invalid 2FA code. Try again...";
		} else if (data['non_field_errors'][0] === "Invalid 2FA token.") {
			console.log("Invalid token.");
			sessionStorage.removeItem("2fa_token");
			removeEnterValidate();
			router("/login");
		}
	} else if (data) {
		console.log(data);
	}
}

async function addEventListeners() {
	const inputs = Array.from(document.querySelectorAll('input'));
	const button = document.getElementById("verify-btn");
	inputsEvents(inputs);
	await buttonValidate(inputs, button);
	enterValidate(inputs, button);
}

export async function get2FAPage() {
	if (!sessionStorage.getItem("2fa_token")) {
		window.location.replace("/login");
		return;
	}
	removeEnterValidate();
	loadProfileCss("/public/css/2fa.css");
    const template = await fetchTemplate("/public/html/2fa.html");
	document.getElementById("main").innerHTML = template;
	addEventListeners();
}
