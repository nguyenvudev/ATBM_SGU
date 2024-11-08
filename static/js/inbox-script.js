///__________Ẩn hiện các form__________///
// ---- Ẩn hiện sidebar ---- //
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

// ---- Ẩn hiện các form ---- //
document.addEventListener("DOMContentLoaded", function() {
    // ---- Const các nút bấm ---- //
    // Nút sidebar
    const mailCreateBtn = document.querySelector('.mail-create');
    const mailReceivedBtn = document.querySelector('.mail-received');
    const mailSendBtn = document.querySelector('.mail-send');
    const mailTrashBtn = document.querySelector('.mail-trash');

    // Nút bên home-section
    const mailProfileBtn = document.querySelector(".profile-details");
    const mailChangeBtn = document.querySelector(".recover-key");
    const mailSeenBtn = document.querySelector('.btn-show-details');
    const mailRepBtn = document.querySelector('.btn-rep-email');
    const mailForwardBtn = document.querySelector('.btn-forward-email');

    // Nút tắt
    const closeChangePassword = document.getElementById('close-change');
    const closeFormCreateMail = document.getElementById('close-compose');
    const closeFormSeenMail = document.getElementById('close-form-seen');
    const closeButton = document.getElementById('closeFormDecode');

    // ---- Const các form ---- //
    // Form sidebar
    const formMailCreate = document.querySelector('.form-create-mail');
    const formMailReceived = document.querySelector('.form-mail-received');
    const formMailSend = document.querySelector('.form-mail-send');
    const formMailTrash = document.querySelector('.form-trash-mail');

    // Form bên home-section
    const formProfile = document.querySelector('.form-account');
    const formRecoverKey = document.querySelector('.form-recover-key');
    const formSeenMail = document.querySelector('.form-seen');
    const formDecode = document.getElementById('formDecode');

    let isFormRecover = false;
    let isFormVisible = false;

    // Mặc định hiển thị form thư đến
    formMailReceived.classList.add('active');

    // Reset form trước khi chuyển đổi form khác
    function resetForms() {
        formMailReceived.classList.remove('active');
        formMailSend.classList.remove('active');
        formMailTrash.classList.remove('active');
    }

    // ----- Mở form liên kết với nút bên sidebar ----- //
    // Mở form thư đến
    mailReceivedBtn.addEventListener('click', function() {
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailReceived.classList.add('active');
    });

    // Mở form thư đã gửi
    mailSendBtn.addEventListener('click', function() {
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailSend.classList.add('active');
    });

    // Mở form thùng rác
    mailTrashBtn.addEventListener('click', function(){
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailTrash.classList.add('active');
    });

    // Mở form soạn thư
    mailCreateBtn?.addEventListener('click', function() {
        formMailCreate.classList.toggle('active');
    });

    // ----- Mở form bên home-section ----- //
    // Mở form thông tin tài khoản
    mailProfileBtn?.addEventListener("click", function() {
         formProfile.classList.toggle('active');
    });
    // Mở và đóng form đổi mật khẩu
    mailChangeBtn?.addEventListener("click", function(e) {
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
    closeChangePassword?.addEventListener('click', closeFormRecoverKey);

    // Mở và đóng thư đã gửi
    mailSeenBtn?.addEventListener('click', function(){
        formSeenMail.classList.toggle('active');
    });

    function hideFormSeen() {
        if (formSeenMail) {
            formSeenMail.classList.remove('active');
        }
    }

    if (closeFormSeenMail) {
        closeFormSeenMail.addEventListener('click', hideFormSeen);
    }

    // Mở và đóng thư đến để đọc
    function hideFormDecode() {
        if (formDecode) {
            formDecode.classList.remove('active');
        }
    }

    function showFormDecode() {
        if (formDecode) {
            formDecode.classList.add('active');
        }
    }

    // Mở và đóng trả lời thu
    mailRepBtn?.addEventListener('click', function() {
        formMailCreate.classList.add('active');
        document.getElementById('recipient').value = document.getElementById('senderEmail').innerText;
        document.getElementById('subject').value = '';
        document.getElementById('main').innerText = '';
    });

    mailForwardBtn?.addEventListener('click', function() {
        formMailCreate.classList.add('active');
        document.getElementById('recipient').value = '';
        document.getElementById('subject').value = 'Re: ' + document.getElementById('subjectEmail').innerText;
        document.getElementById('main').innerText =  document.getElementById('decryptedBody').innerText;
    });

    function closeCreateMail() {
        formMailCreate.classList.remove('active');
        document.getElementById('recipient').value = '';
        document.getElementById('subject').value = '';
        document.getElementById('main').innerText = '';
    }
    closeFormCreateMail?.addEventListener('click', closeCreateMail);

    // ----- Lấy thông tin cho formDecode ----- //
    document.querySelectorAll('.btn-show-decode').forEach(btn => {
        btn.addEventListener('click', function(event) {
            event.preventDefault();

            const url = this.href;
            const emailRow = this.closest('.email-row');

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('senderEmail').innerText = data.sender_email;
                    document.getElementById('subjectEmail').innerText = data.subject;

                    if (data.decrypted_body) {
                        document.getElementById('decryptedBody').innerText = data.decrypted_body;
                        document.getElementById('bodyContent').style.display = 'block';
                        document.getElementById('noDecryptedBody').style.display = 'none';
                    } else {
                        document.getElementById('bodyContent').style.display = 'none';
                        document.getElementById('noDecryptedBody').style.display = 'block';
                    }

                    if (data.decrypted_attachments && data.decrypted_attachments.length > 0) {
                        let attachmentsHTML = '';
                        data.decrypted_attachments.forEach(attachment => {
                            attachmentsHTML += `
                                <div class="merge-file">
                                    <div class="form-file">
                                        <div class="line"></div>
                                        <a href="${attachment.path}" download>
                                            ${getIconByFileExtension(attachment.filename)}
                                            ${attachment.filename}
                                        </a>
                                        <div class="corner-triangle"></div>
                                    </div>
                                </div>
                            `;
                        });
                        document.getElementById('attachmentsList').innerHTML = attachmentsHTML;
                        document.getElementById('attachmentsContent').style.display = 'block';
                        document.getElementById('noAttachmentsContent').style.display = 'none';
                    } else {
                        document.getElementById('attachmentsContent').style.display = 'none';
                        document.getElementById('noAttachmentsContent').style.display = 'block';
                    }

                    if (closeButton) {
                        closeButton.addEventListener('click', hideFormDecode);
                    }

                    showFormDecode();

                    function getIconByFileExtension(filename) {
                        const ext = filename.split('.').pop().toLowerCase();
                        switch (ext) {
                            case 'pdf': return '<i class="bx bxs-file-pdf" style="color: red"></i>';
                            case 'xlsx': return '<i class="fa fa-file-excel" style="color: green"></i>';
                            case 'txt': return '<i class="bx bxs-file-txt"></i>';
                            case 'doc': case 'docx': return '<i class="bx bxs-file-doc" style="color: blue"></i>';
                            case 'zip': return '<i class="bx bxs-file-archive"></i>';
                            default: return '<i class="bx bxs-file"></i>';
                        }
                    }

                    emailRow.classList.remove('unread');
                    emailRow.classList.add('read');
                })
                .catch(error => console.error('Error fetching data:', error));
        });
    });

    // ----- Đóng form khi click ngoài form ----- //
    document.addEventListener('click', function(event) {
        //if (!formMailCreate.contains(event.target) && !event.target.closest('.mail-create')) {
        //    closeCreateMail();
        //}
        if (!formRecoverKey.contains(event.target) && !event.target.closest('.recover-key')) {
            closeFormRecoverKey();
        }
        //if (formSeenMail && !formSeenMail.contains(event.target) && !event.target.closest('.btn-show-details')) {
        //    hideFormSeen();
        //}
    });
});

///_____________________Ẩn hiện nút Delete_____________________///
// ---- Nút Delete của form thư đến ---- //
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

// ---- Nút Delete của form thư đã gửi ---- //
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

// ---- Nút Delete của form thùng rác ---- //
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

///__________Thông báo của việc thực hiện gửi maill__________///
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const alertBox = document.querySelector(".alert");
        if (alertBox) {
            alertBox.style.display = "none";
        }
    }, 4000);
});

///__________Phân trang danh sách thư của các form__________///
document.addEventListener('DOMContentLoaded', function() {
    const rowsPerPage = 13;

    function paginateTable(table) {
        const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
        const paginationControls = table.nextElementSibling;
        let currentPage = 1;

        function displayRows() {
            const startRow = (currentPage - 1) * rowsPerPage;
            const endRow = startRow + rowsPerPage;
            for (let i = 0; i < rows.length; i++) {
                rows[i].style.display = i >= startRow && i < endRow ? '' : 'none';
            }
        }

        function setupPagination() {
            const pageCount = Math.ceil(rows.length / rowsPerPage);
            paginationControls.innerHTML = '';

            for (let i = 1; i <= pageCount; i++) {
                const pageButton = document.createElement('button');
                pageButton.textContent = i;
                pageButton.classList.add('page-button');
                pageButton.addEventListener('click', function() {
                    currentPage = i;
                    displayRows();
                    highlightCurrentPage();
                });
                paginationControls.appendChild(pageButton);
            }
        }

        function highlightCurrentPage() {
            const buttons = paginationControls.getElementsByClassName('page-button');
            for (let button of buttons) {
                button.style.backgroundColor = button.textContent == currentPage ? '#007BFF' : '#f5f5f5';
                button.style.color = button.textContent == currentPage ? '#FFF' : '#000';
            }
        }

        displayRows();
        setupPagination();
        highlightCurrentPage();
    }

    // Lặp qua tất cả các bảng email-table để phân trang
    document.querySelectorAll('.email-table').forEach(table => {
        paginateTable(table);
    });
});

///__________Các chỉnh sửa cho phần soạn thư__________///
// ----- Cập nhật nội dung vào div ----- //
function updateBody() {
    document.getElementById('hidden-body').value = document.getElementById('main').innerHTML;
}

// ----- Cập nhật nội dung không bị lỗi div/br ----- //
document.addEventListener("DOMContentLoaded", function() {
    const mainDiv = document.getElementById('main');

    // Thiết lập sự kiện input để xử lý mỗi khi người dùng nhập liệu
    mainDiv.addEventListener('input', function(event) {
        // Có thể điều chỉnh các thuộc tính hoặc xử lý nội dung tại đây nếu cần
    });

    // Đặt focus vào phần tử khi người dùng click vào nó
    mainDiv.addEventListener('click', function(event) {
        mainDiv.focus();
    });

    // Thiết lập các thuộc tính khi phần tử được focus
    mainDiv.addEventListener('focus', function(event) {
        mainDiv.style.outline = 'none'; // Loại bỏ viền mặc định khi focus
    });

    // Mẫu nội dung ban đầu
    const content = "";
    mainDiv.innerHTML = content.replace(/\n/g, '<br/>');
});

// ----- Gửi nhiều file và chuyển thành dropdown ----- //
let selectedFiles = [];
document.getElementById('attachment').addEventListener('change', function() {
    const newFiles = Array.from(this.files);

    newFiles.forEach(file => {
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });

    const dataTransfer = new DataTransfer();
    selectedFiles.forEach(file => dataTransfer.items.add(file));
    this.files = dataTransfer.files;

    const fileDropdownContainer = document.getElementById('file-dropdown-container');
    fileDropdownContainer.innerHTML = '';

    const select = document.createElement('select');
    select.className = 'file-dropdown';

    selectedFiles.forEach(file => {
        const option = document.createElement('option');
        option.value = file.name;
        option.text = file.name;
        select.appendChild(option);
    });

    fileDropdownContainer.appendChild(select);
});

///__________ Ajax tự động reload để cập nhật mail khi gửi mail__________///
document.getElementById('send-email-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    fetch("{{ url_for('send_email') }}", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'success') {
            updateSentEmails();
        }
    })
    .catch(error => console.error('Error:', error));
});

function updateSentEmails() {
    fetch("{{ url_for('inbox') }}")
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTbody = doc.getElementById('sent-emails-tbody');
        document.getElementById('sent-emails-tbody').innerHTML = newTbody.innerHTML;
    })
    .catch(error => console.error('Error:', error));
}

////////////////Chưa chỉnh///////////////////
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