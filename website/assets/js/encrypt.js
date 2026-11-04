// @ts-check

import * as age from "age-encryption";

const PUBLIC_KEY = "age1xpexzyk4k608tsccev20d7uakptkmgxr4nc8s0azzywkgtz86aaqsdryr4";

const e = new age.Encrypter();
e.addRecipient(PUBLIC_KEY);

/**
 * @param {string} secret
 * @return {Promise<string>}
 */
async function encrypt(secret) {
    const cipherText = await e.encrypt(secret);
    const base64String = btoa(String.fromCharCode(...cipherText));
    return `AGE-ENCRYPTED:${base64String}`
}

document.getElementById("encrypt")?.addEventListener('click', () => {
    const inputEl = getElement("input");
    if (!(inputEl instanceof HTMLInputElement)) {
        throw new Error("input element not found")
    };
    const secret = inputEl.value
    encrypt(secret).then(cipherText => {
        getElement("output").innerText = cipherText;
    }).catch(e => {
        getElement("error").innerText = e;
    });
})

/**
 * @param {string} id
 * @return {HTMLElement}
 */
function getElement(id) {
    const el = document.getElementById(id);
    if (!el) {
        throw new Error(`element with id ${id} not found`);
    }
    return el;
}
