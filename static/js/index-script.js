function showLogin() {
    document.querySelector('.screen-login').classList.add('active');
    document.querySelector('.screen-register').classList.remove('active');
}
function showRegister() {
    document.querySelector('.screen-register').classList.add('active');
    document.querySelector('.screen-login').classList.remove('active');
}
function closeModal() {
    document.querySelector('.screen-login').classList.remove('active');
    document.querySelector('.screen-register').classList.remove('active');
}