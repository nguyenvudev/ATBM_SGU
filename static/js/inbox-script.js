// Đóng mở sidebar
let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");

closeBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    menuBtnChange();
});

function menuBtnChange() {
    if (sidebar.classList.contains("open")) {
        closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
    } else {
        closeBtn.classList.replace("bx-menu-alt-right", "bx-menu");
    }
}

// Hiển thị
document.addEventListener("DOMContentLoaded", function() {
    // Lấy các phần tử
    const mailCreateBtn = document.querySelector('.mail-create');
    const mailReceivedBtn = document.querySelector('.mail-received');
    const mailSendBtn = document.querySelector('.mail-send');
    const mailTrashBtn = document.querySelector('.mail-trash');

    const formMailCreate = document.querySelector('.form-create-mail');
    const formMailReceived = document.querySelector('.form-mail-received');
    const formMailSend = document.querySelector('.form-mail-send');
    const formMailTrash = document.querySelector('.form-trash-mail');
    const formRecoverKey = document.querySelector('.form-recover-key');
    const closeComposeIcon = document.getElementById('close-compose');
    const closeRecoverKey = document.getElementById('close-change');
    const btnRecover = document.querySelector(".recover-key button");
    const btnForm = document.querySelector(".profile-details");

    let isFormRecover = false;
    let isFormVisible = false;

    // Chức năng chuyển đổi giữa các form hộp thư
    function resetForms() {
        formMailReceived.classList.remove('active');
        formMailSend.classList.remove('active');
        formMailTrash.classList.remove('active');
    }

    // Hiển thị hộp thư đến mặc định
    formMailReceived.classList.add('active');

    mailReceivedBtn.addEventListener('click', function() {
        resetForms();
        formMailReceived.classList.add('active');
    });
    mailSendBtn.addEventListener('click', function() {
        resetForms();
        formMailSend.classList.add('active');
    });
    mailTrashBtn.addEventListener('click', function(){
        resetForms();
        formMailTrash.classList.add('active');
    });

    // Chức năng mở và đóng form Tạo Email
    mailCreateBtn?.addEventListener('click', function() {
        formMailCreate.classList.toggle('active');
    });

    function closeCreateMail() {
        formMailCreate.classList.remove('active');
    }
    closeComposeIcon?.addEventListener('click', closeCreateMail);

    // Chức năng mở và đóng form Khôi Phục Mật Khẩu
    btnRecover?.addEventListener("click", function(e) {
        e.preventDefault();
        if (!isFormRecover) {
            formRecoverKey.style.opacity = 1;
            formRecoverKey.style.visibility = "visible";
            formRecoverKey.style.transform = "scale(1)";
            isFormRecover = true;
        } else {
            formRecoverKey.style.opacity = 0;
            formRecoverKey.style.visibility = "hidden";
            formRecoverKey.style.transform = "scale(0)";
            isFormRecover = false;
        }
    });

    function closeFormRecoverKey() {
        formRecoverKey.classList.remove('active');
        formRecoverKey.style.opacity = 0;
        formRecoverKey.style.visibility = "hidden";
        formRecoverKey.style.transform = "scale(0)";
        isFormRecover = false;
    }
    closeRecoverKey?.addEventListener('click', closeFormRecoverKey);

    // Đóng form khi nhấp ra ngoài
    document.addEventListener('click', function(event) {
        if (!formMailCreate.contains(event.target) && !event.target.closest('.mail-create')) {
            closeCreateMail();
        }
        if (!formRecoverKey.contains(event.target) && !event.target.closest('.recover-key')) {
            closeFormRecoverKey();
        }
    });

    // Chức năng hiển thị thông tin tài khoản
    btnForm?.addEventListener("click", function() {
        if (!isFormVisible) {
            btnForm.classList.add("active");
            isFormVisible = true;
        } else {
            btnForm.classList.remove("active");
            isFormVisible = false;
        }
    });
});

// Icon delete thư đến
function toggleDeleteIconReceived() {
   let checkboxesChecked = document.querySelectorAll('.email-checkbox-received:checked').length > 0;
   let deleteIcon = document.getElementById('delete-icon-1');
   deleteIcon.style.display = checkboxesChecked ? 'block' : 'none';
}

document.getElementById('select-all-received').addEventListener('change', function(event) {
   let checkboxes = document.querySelectorAll('.email-checkbox-received');
   checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
   toggleDeleteIconReceived();
});

document.querySelectorAll('.email-checkbox-received').forEach(checkbox => {
   checkbox.addEventListener('change', toggleDeleteIconReceived);
});

toggleDeleteIconReceived();

// Icon delete thư đã gửi
function toggleDeleteIconSend() {
   let checkboxesChecked = document.querySelectorAll('.email-checkbox-send:checked').length > 0;
   let deleteIcon = document.getElementById('delete-icon-2');
   deleteIcon.style.display = checkboxesChecked ? 'block' : 'none';
}

document.getElementById('select-all-send').addEventListener('change', function(event) {
    let checkboxes = document.querySelectorAll('.email-checkbox-send');
    checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
    toggleDeleteIconSend();
});

document.querySelectorAll('.email-checkbox-send').forEach(checkbox => {
    checkbox.addEventListener('change', toggleDeleteIconSend);
});

toggleDeleteIconSend();

// Icon delete thùng rác
function toggleDeleteIconTrash() {
   let checkboxesChecked = document.querySelectorAll('.email-checkbox-trash:checked').length > 0;
   let deleteIcon = document.getElementById('delete-icon-3');
   deleteIcon.style.display = checkboxesChecked ? 'block' : 'none';
}

document.getElementById('select-all-trash').addEventListener('change', function(event) {
    let checkboxes = document.querySelectorAll('.email-checkbox-trash');
    checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
    toggleDeleteIconTrash();
});

document.querySelectorAll('.email-checkbox-trash').forEach(checkbox => {
    checkbox.addEventListener('change', toggleDeleteIconTrash);
});

toggleDeleteIconTrash();

// Chức năng soạn thư

//  Cập nhật body
function updateBody() {
    // Cập nhật giá trị của trường ẩn 'body' từ nội dung của <div id="main">
    document.getElementById('hidden-body').value = document.getElementById('main').innerHTML;
}

// Tệp đính kèm
let selectedFiles = []; // Khởi tạo mảng để lưu trữ các file đã chọn

document.getElementById('attachment').addEventListener('change', function () {
    const fileList = document.getElementById('file-list');
    const files = Array.from(this.files); // Lấy danh sách file đã chọn và chuyển thành mảng

    // Bổ sung các file mới vào mảng selectedFiles
    selectedFiles = selectedFiles.concat(files);

    // Cập nhật danh sách file hiển thị
    fileList.innerHTML = ''; // Xóa nội dung cũ
    const select = document.createElement('select');
    select.className = 'file-dropdown';

    const defaultOption = document.createElement('option');
    defaultOption.text = 'Danh sách file';
    select.appendChild(defaultOption);

    // Lặp qua từng file trong mảng selectedFiles để hiển thị
    selectedFiles.forEach((file, index) => {
        const option = document.createElement('option');
        option.text = file.name;
        option.value = index; // Lưu trữ chỉ mục của file để xóa nếu cần
        select.appendChild(option);
    });

    fileList.appendChild(select);

    // Xóa các file đã chọn sau khi thêm vào mảng để tránh chọn lại khi người dùng nhấp vào input file
    this.value = '';
});

///////////////////////////////////
function moveToTrash() {
    const selectedEmails = document.querySelectorAll('.email-checkbox-received:checked');

    if (selectedEmails.length === 0) {
        alert('Vui lòng chọn ít nhất một email để xóa.');
        return;
    }

    const emailIds = Array.from(selectedEmails).map(checkbox => checkbox.getAttribute('data-email-id'));

    if (confirm('Bạn có chắc chắn muốn chuyển email đã chọn vào Thùng rác?')) {
        fetch('/move_to_trash', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email_ids: emailIds })
        })
        .then(response => {
            if (response.ok) {
                // Xóa email khỏi DOM ngay lập tức
                selectedEmails.forEach(email => {
                    email.closest('tr').remove(); // Xóa dòng tương ứng với email khỏi DOM
                });
            } else {
                alert('Đã xảy ra lỗi khi chuyển email vào Thùng rác.');
            }
        })
        .catch(error => {
            console.error('Lỗi:', error);
        });
    }
}

function deleteSelectedTrash() {
    const selectedEmails = document.querySelectorAll('.email-checkbox-trash:checked');

    if (selectedEmails.length === 0) {
        alert('Vui lòng chọn ít nhất một email để xóa.');
        return;
    }

    const emailIds = Array.from(selectedEmails).map(checkbox => checkbox.getAttribute('data-email-id'));

    if (confirm('Bạn có chắc chắn muốn xóa vĩnh viễn các email đã chọn?')) {
        fetch('/delete_emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email_ids: emailIds })
        })
        .then(response => {
            if (response.ok) {
                // Xóa email khỏi DOM
                selectedEmails.forEach(email => {
                    email.closest('tr').remove(); // Xóa dòng tương ứng với email khỏi DOM
                });
            } else {
                alert('Đã xảy ra lỗi khi xóa email.');
            }
        })
        .catch(error => {
            console.error('Lỗi:', error);
        });
    }
}