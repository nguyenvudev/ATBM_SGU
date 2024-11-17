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
    document.querySelector('.forgot-password').classList.remove('active');
}
function forgotPassword() {
    document.querySelector('.forgot-password').classList.add('active');
    document.querySelector('.screen-login').classList.remove('active');
}

// Hiển thị modal thành công
function showSuccessModal() {
    document.getElementById('successModal').style.display = 'block';
}

// Chuyển hướng đến trang đăng nhập
function redirectToLogin() {
    closeModal(); 
    document.getElementById('successModal').style.display = 'none';
    showLogin();  
}

// Hiển thị modal lỗi
function showErrorModal(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').style.display = 'block';
}

// Đóng modal lỗi
function closeErrorModal() {
    document.getElementById('errorModal').style.display = 'none';
}

// Xử lý gửi form đăng ký
document.querySelector('.register').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);

    fetch(this.action, {
        method: this.method,
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessModal();

            // Tự động tải file khóa riêng tư
            setTimeout(() => {
                fetch(`/download_private_key?filename=${encodeURIComponent(data.private_key_file)}`, {
                    method: 'GET',
                })
                .then(response => response.blob())
                .then(blob => {
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = `private_key_${formData.get('email')}.pem`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                })
                .catch(error => console.error('Error downloading key:', error));
            }, 2000);
        } else {
            showErrorModal(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});

// Hiển thị modal lỗi khi đăng nhập
function showErrorModalLogin(message) {
    document.getElementById('errorMessageLogin').textContent = message;
    document.getElementById('errorModalLogin').style.display = 'block';
}

// Đóng modal lỗi đăng nhập
function closeErrorModalLogin() {
    document.getElementById('errorModalLogin').style.display = 'none';
}

// Xử lý gửi form đăng nhập
document.querySelector('.login').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);

    fetch(this.action, {
        method: this.method,
        body: formData,
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;  // Chuyển hướng đến URL được trả về (inbox)
        } else {
            return response.json();  // Nếu không chuyển hướng, trả về JSON để kiểm tra lỗi
        }
    })
    .then(data => {
        if (data && !data.success) {
            showErrorModalLogin(data.message);  // Hiển thị modal lỗi khi có lỗi
        }
    })
    .catch(error => console.error('Error:', error));
});