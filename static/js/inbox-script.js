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
    const mailRepReceivedBtn = document.querySelector('.btn-rep-email-received');
    const mailForwardReceivedBtn = document.querySelector('.btn-forward-email-received');
    const mailRepSentBtn = document.querySelector('.btn-rep-email-sent');
    const mailForwardSentBtn = document.querySelector('.btn-forward-email-sent');

    // Nút tắt
    const closeChangePassword = document.getElementById('close-change');
    const closeFormCreateMail = document.getElementById('close-compose');
    const closeFormSeenMail = document.getElementById('close-form-seen');
    const closeButton = document.getElementById('closeFormDecode');

    // Trả lời
    const closeRepSentMail = document.getElementById('close-rep-seen');
    const closeRepReceived = document.getElementById('close-rep-received');

    // ---- Const các form ---- //
    // Form sidebar
    const formMailCreate = document.querySelector('.form-create-mail');
    const formMailReceived = document.querySelector('.form-mail-received');
    const formMailSend = document.querySelector('.form-mail-send');
    const formMailTrash = document.querySelector('.form-trash-mail');

    // Form bên home-section
    const formProfile = document.querySelector('.form-account');
    const formRecoverKey = document.querySelector('.form-recover-key');
    const formSeenMail = document.getElementById('formSeen');
    const formDecode = document.getElementById('formDecode');
    const formRepSentMail = document.getElementById('form-rep-sent');
    const formRepReceivedMail = document.getElementById('form-rep-received');

    let isFormRecover = false;

    // Mặc định hiển thị form thư đến
    formMailReceived.classList.add('active');
    document.querySelector('a.mail-received').classList.add('hover-effect');

    // Reset form trước khi chuyển đổi form khác
    function resetForms() {
        formMailReceived.classList.remove('active');
        formMailSend.classList.remove('active');
        formMailTrash.classList.remove('active');
    }

    // Hàm xóa lớp 'hover-effect' khỏi tất cả các mục menu
    function removeAllHoverEffects() {
        document.querySelectorAll('.sidebar li a').forEach(item => {
            item.classList.remove('hover-effect');
        });
    }

    // Mở form hộp thư đến
    mailReceivedBtn.addEventListener('click', function() {
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailReceived.classList.add('active');
        removeAllHoverEffects();
        document.querySelector('a.mail-received').classList.add('hover-effect');
    });

    // Mở form thư đã gửi
    mailSendBtn.addEventListener('click', function() {
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailSend.classList.add('active');
        removeAllHoverEffects();
        document.querySelector('a.mail-send').classList.add('hover-effect');
    });

    // Mở form thùng rác
    mailTrashBtn.addEventListener('click', function() {
        hideFormDecode();
        hideFormSeen();
        resetForms();
        formMailTrash.classList.add('active');
        removeAllHoverEffects();
        document.querySelector('a.mail-trash').classList.add('hover-effect');
    });

    // Mở form soạn thư
    mailCreateBtn?.addEventListener('click', function() {
        formMailCreate.classList.toggle('active');
    
        if (formMailCreate.classList.contains('active')) {
            removeAllHoverEffects();
            document.querySelector('a.mail-create').classList.add('hover-effect');
        } else {
            document.querySelector('a.mail-create').classList.remove('hover-effect');
        }
    });

    // Đóng form soạn thư
    function closeCreateMail() {
        formMailCreate.classList.remove('active');
        document.getElementById('recipient').value = '';
        document.getElementById('subject').value = '';
        document.getElementById('main').innerText = '';
    }
    closeFormCreateMail?.addEventListener('click', closeCreateMail);

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

    // ----- Lấy thông tin cho formDecode ----- //
    function hideFormDecode() {
        if (formDecode) {
            formRepReceivedMail.classList.remove('active');
            formDecode.classList.remove('active');
        }
    }

    function showFormDecode() {
        if (formDecode) {
            formDecode.classList.add('active');
        }
    }

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
                    const timestamp = new Date(data.timestamp);
                    document.getElementById('timeEmailReceived').innerText = timestamp.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });
     
                    if (data.decrypted_body) {
                        let decryptedBody = data.decrypted_body; // Chuyển đổi các ký tự xuống dòng thành thẻ <br>
                        decryptedBody = decryptedBody.replace(/\n/g, '<br>');
                        document.getElementById('decryptedBody').innerHTML = decryptedBody;
                        document.getElementById('bodyContent').style.display = 'block';
                        document.getElementById('noDecryptedBody').style.display = 'none';
                    } else {
                        document.getElementById('bodyContent').style.display = 'none';
                        document.getElementById('noDecryptedBody').style.display = 'block';
                    }

                    if (data.decrypted_attachments && data.decrypted_attachments.length > 0) {
                        let attachmentsHTML = '';
                        data.decrypted_attachments.forEach(attachment => {
                            const fileIcon = getIconByFileExtension(attachment.filename);
                            attachmentsHTML += `
                                <div class="merge-file">
                                    <div class="form-file">
                                        <div class="line">
                                            ${fileIcon.icon} <!-- Icon lớn cho loại tệp -->
                                        </div>
                                        <a href="${attachment.path}" download>
                                            <span class="icon-small">${fileIcon.icon}</span> <!-- Icon nhỏ cạnh tên tệp -->
                                            ${attachment.filename}
                                        </a>
                                        <div class="corner-triangle" style="border-top-color: ${fileIcon.color};"></div>
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
                            case 'pdf':
                                return { icon: '<i class="bx bxs-file-pdf icon-file" style="color: red"></i>', color: 'red' };
                            case 'xlsx':
                                return { icon: '<i class="fa fa-file-excel icon-file" style="color: green"></i>', color: 'green' };
                            case 'txt':
                                return { icon: '<i class="bx bxs-file-txt icon-file"></i>', color: 'gray' };
                            case 'doc': case 'docx':
                                return { icon: '<i class="bx bxs-file-doc icon-file" style="color: blue"></i>', color: 'blue' };
                            case 'zip':
                                return { icon: '<i class="bx bxs-file-archive icon-file"></i>', color: 'orange' };
                            default:
                                return { icon: '<i class="bx bxs-file icon-file"></i>', color: 'black' };
                        }
                    }
                    emailRow.classList.remove('unread');
                    emailRow.classList.add('read');
                })
            .catch(error => console.error('Error fetching data:', error));
        });
    });

    // Mở form trả lời thư
    mailRepReceivedBtn?.addEventListener('click', function () {
        formRepReceivedMail.classList.toggle('active');
        document.getElementById('title-received').innerHTML = 'Trả lời thư';
        document.getElementById('recipient-received').value = document.getElementById('senderEmail').innerText;
        document.getElementById('subject-received').value = 'Rep: ';
        document.getElementById('main-received').innerText = 
            '\n\n\n\n' +
            'Vào lúc: ' + document.getElementById('timeEmailReceived').innerText + 
            ' < ' + document.getElementById('senderEmail').innerText + ' > đã viết:' + '\n\n' +
            document.getElementById('decryptedBody').innerText;
    })

    // Mở form chuyển tiếp
    mailForwardReceivedBtn?.addEventListener('click', function () {
        formRepReceivedMail.classList.toggle('active');  
        document.getElementById('title-received').innerHTML = 'Chuyển tiếp thư';
        document.getElementById('recipient-received').value = '';
        document.getElementById('subject-received').value = 'Forward: ';
        document.getElementById('main-received').innerText = 
            '\n\n\n\n' +
            '----Forwarded message----' + '\n' +
            'Từ: < ' + document.getElementById('senderEmail').innerText + ' >' + '\n' +
            'Thời gian: ' + document.getElementById('timeEmailReceived').innerText + '\n' +
            'Tiêu đề: ' + document.getElementById('subjectEmail').innerText + '\n' + 
            'Với nội dung sau:' + '\n\n' +
            document.getElementById('decryptedBody').innerText; 
    }) 

    // Đóng form trả lời thư
    closeRepReceived?.addEventListener('click', function () {
        formRepReceivedMail.classList.remove('active');
    });


     // ----- Lấy thông tin cho formSentMail ----- //
    function hideFormSeen() {
        if (formSeenMail) {
            formRepSentMail.classList.remove('active');
            formSeenMail.classList.remove('active');
        }
    }

    function showFormSeen() {
        if (formSeenMail) {
            formSeenMail.classList.add('active');
        }
    }

    document.querySelectorAll('.btn-show-details').forEach(btn => {
        btn.addEventListener('click', function(event) {
            event.preventDefault();

            fetch(this.href)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('messEmail').innerText = data.message;
                    document.getElementById('receiverEmail').innerText = data.receiver_email;
                    document.getElementById('sendEmail').innerText = data.send_email;
                    document.getElementById('subjectSeen').innerText = data.subject;
                    const timestamp = new Date(data.timestamp);
                    document.getElementById('timeEmailSent').innerText = timestamp.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

                    if (data.decrypted_body_send) {
                        let decrypted_Body_send = data.decrypted_body_send.replace(/\n/g, '<br>');
                        document.getElementById('decryptedBodySeen').innerHTML = decrypted_Body_send;
                        document.getElementById('bodyContent').style.display = 'block';
                        document.getElementById('noDecryptedBody').style.display = 'none';
                    } else {
                        document.getElementById('bodyContent').style.display = 'none';
                        document.getElementById('noDecryptedBody').style.display = 'block';
                    }

                    if (data.decrypted_attachments && data.decrypted_attachments.length > 0) {
                        let attachmentsHTML = '';
                        data.decrypted_attachments.forEach(attachment => {
                            const fileIcon = getIconByFileExtension(attachment.filename);
                            attachmentsHTML += `
                                <div class="merge-file">
                                    <div class="form-file">
                                        <div class="line">${fileIcon.icon}</div>
                                        <a href="${attachment.path}" download>
                                            <span class="icon-small">${fileIcon.icon}</span>
                                            ${attachment.filename}
                                        </a>
                                        <div class="corner-triangle" style="border-top-color: ${fileIcon.color};"></div>
                                    </div>
                                </div>
                            `;
                        });

                        document.getElementById('attachmentsSeenList').innerHTML = attachmentsHTML;
                        document.getElementById('attachmentsSeenContent').style.display = 'block';
                        document.getElementById('noAttachmentsSeenContent').style.display = 'none';
                    } else {
                        document.getElementById('attachmentsSeenContent').style.display = 'none';
                        document.getElementById('noAttachmentsSeenContent').style.display = 'block';
                    }

                    if (closeFormSeenMail) {
                        closeFormSeenMail.addEventListener('click', hideFormSeen);
                    }

                    showFormSeen();

                    function getIconByFileExtension(filename) {
                        const ext = filename.split('.').pop().toLowerCase();
                        switch (ext) {
                            case 'pdf': return { icon: '<i class="bx bxs-file-pdf icon-file" style="color: red"></i>', color: 'red' };
                            case 'xlsx': return { icon: '<i class="fa fa-file-excel icon-file" style="color: green"></i>', color: 'green' };
                            case 'txt': return { icon: '<i class="bx bxs-file-txt icon-file"></i>', color: 'gray' };
                            case 'doc': case 'docx': return { icon: '<i class="bx bxs-file-doc icon-file" style="color: blue"></i>', color: 'blue' };
                            case 'zip': return { icon: '<i class="bx bxs-file-archive icon-file"></i>', color: 'orange' };
                            default: return { icon: '<i class="bx bxs-file icon-file"></i>', color: 'black' };
                        }
                    }
                })
            .catch(error => console.error('Error fetching data:', error));
        });
    });

    // Mở form trả lời thư
    mailRepSentBtn?.addEventListener('click', function () {
        formRepSentMail.classList.toggle('active');
        document.getElementById('title-sent').innerHTML = 'Trả lời thư';
        document.getElementById('recipient-sent').value = document.getElementById('receiverEmail').innerText;
        document.getElementById('subject-sent').value = 'Rep: ';
        document.getElementById('main-sent').innerText = 
            '\n\n\n\n' +
            'Vào lúc: ' + document.getElementById('timeEmailSent').innerText + 
            ' < ' + document.getElementById('receiverEmail').innerText + ' > đã viết:' + '\n\n' +
            document.getElementById('decryptedBodySeen').innerText;
    })

    // Mở form chuyển tiếp
    mailForwardSentBtn?.addEventListener('click', function () {
        formRepSentMail.classList.toggle('active');
        document.getElementById('title-sent').innerHTML = 'Chuyển tiếp thư';
        document.getElementById('recipient-sent').value = '';
        document.getElementById('subject-sent').value = 'Forward: ';
        document.getElementById('main-sent').innerText = 
            '\n\n\n\n' +
            '----Forwarded message----' + '\n' +
            'Từ: < ' + document.getElementById('sendEmail').innerText + ' >' + '\n' +
            'Thời gian: ' + document.getElementById('timeEmailSent').innerText + '\n' +
            'Tiêu đề: ' + document.getElementById('subjectSeen').innerText + '\n' +
            'Đến: < ' + document.getElementById('receiverEmail').innerText + ' >' + '\n\n' + 
            document.getElementById('decryptedBodySeen').innerText;   
    }) 

    // Đóng form trả lời thư
    closeRepSentMail?.addEventListener('click', function () {
        formRepSentMail.classList.remove('active');
    });
    
    // ----- Đóng form khi click ngoài form ----- //
    document.addEventListener('click', function(event) {
        if (!formRecoverKey.contains(event.target) && !event.target.closest('.recover-key')) {
            closeFormRecoverKey();
        }
    });

    // Hàm chung để điều chỉnh vị trí formRep theo form cha
    function setPositionAtBottom(form, parentForm) { 
        const clientHeight = parentForm.clientHeight;  
        const scrollTop = parentForm.scrollTop; 
        
        form.style.top = `${scrollTop + clientHeight - form.offsetHeight}px`;
    }

    if (formDecode && formRepReceivedMail) {
        formDecode.addEventListener('scroll', function () {
            setPositionAtBottom(formRepReceivedMail, formDecode);
        });

        setPositionAtBottom(formRepReceivedMail, formDecode);
    }

    if (formSeenMail && formRepSentMail) {
        formSeenMail.addEventListener('scroll', function () {
            setPositionAtBottom(formRepSentMail, formSeenMail);
        });

        setPositionAtBottom(formRepSentMail, formSeenMail);
    }
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

document.getElementById('delete-icon-3').addEventListener('click', function() {
    let selectedEmails = document.querySelectorAll('.email-checkbox-trash:checked');
    let emailIds = [];

    selectedEmails.forEach(checkbox => {
        let emailRow = checkbox.closest('tr');
        if (emailRow) {
            emailIds.push(emailRow.dataset.emailId);
            emailRow.style.display = 'none';
        }
    });

    // Gửi yêu cầu xóa tới máy chủ
    fetch('/delete_emails', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ emailIds: emailIds })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Emails deleted:', data);
    })
    .catch(error => console.error('Error deleting emails:', error));
});

document.getElementById('delete-now').addEventListener('click', function() {
    if (confirm('Bạn có chắc chắn muốn xóa tất cả thư trong thùng rác không?')) {
        // Gửi yêu cầu xóa tất cả thư trong thùng rác
        fetch('/delete_all_trash', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Tất cả thư trong thùng rác đã được xóa thành công!');
                location.reload(); // Tải lại trang để cập nhật trạng thái
            } else {
                alert('Có lỗi xảy ra khi xóa tất cả thư. Vui lòng thử lại.');
            }
        })
        .catch(error => {
            console.error('Error deleting all emails:', error);
            alert('Có lỗi xảy ra khi xóa tất cả thư. Vui lòng thử lại.');
        });
    }
});

// ---- Chuyển đến thùng rác ---- //
function moveToTrash(folderType) {
    let emailIds = [];

    if (folderType === 'received') {
        document.querySelectorAll('.email-checkbox-received:checked').forEach(checkbox => {
            emailIds.push(checkbox.getAttribute('data-email-id'));
        });
    } else if (folderType === 'sent') {
        document.querySelectorAll('.email-checkbox-send:checked').forEach(checkbox => {
            emailIds.push(checkbox.getAttribute('data-email-id'));
        });
    }

    if (emailIds.length === 0) {
        alert('Vui lòng chọn ít nhất một email.');
        return;
    }

    fetch('/move_to_trash', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email_ids: emailIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            emailIds.forEach(id => {
                const emailRow = document.getElementById(`email-${id}`);
                if (emailRow) {
                    emailRow.style.display = 'none';
                }
            });
            updateTrashEmails();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Lỗi:', error);
        alert('Đã xảy ra lỗi khi di chuyển email vào thùng rác.');
    });
}

function updateTrashEmails() {
    fetch('/get_trash_emails')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const trashTableBody = document.querySelector('.form-trash-mail tbody');
                trashTableBody.innerHTML = '';

                data.emails.forEach(email => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="checkbox" class="email-checkbox-trash" data-email-id="${email.id}"></td>
                        <td class="col-trash-1">${email.sender_email}</td>
                        <td class="col-trash-2">${email.subject}</td>
                        <td class="col-trash-3">${email.local_time}</td>
                    `;
                    trashTableBody.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error fetching trash emails:', error));
}

///__________Thông báo của việc thực hiện gửi maill__________///
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const alertBox = document.querySelector(".alert");
        if (alertBox) {
            alertBox.style.display = "none";
        }
    }, 3000);
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
    document.getElementById('hidden-body-sent').value = document.getElementById('main-sent').innerHTML;
    document.getElementById('hidden-body-received').value = document.getElementById('main-received').innerHTML;
}

// ----- Cập nhật nội dung không bị lỗi div/br ----- //
document.addEventListener("DOMContentLoaded", function() {
    const mainDiv = document.getElementById('main');

    // Thiết lập sự kiện input để xử lý mỗi khi người dùng nhập liệu
    mainDiv.addEventListener('input', function(event) {
        // Có thể điều chỉnh các thuộc tính hoặc xử lý nội dung tại đây nếu cần
    });

    mainDiv.addEventListener('click', function(event) {
        mainDiv.focus();
    });

    mainDiv.addEventListener('focus', function(event) {
        mainDiv.style.outline = 'none'; 
    });

    const content = "";
    mainDiv.innerHTML = content.replace(/\n/g, '<br/>');
});

// ----- Gửi nhiều file và chuyển thành dropdown với thanh upload ----- //
function handleFileSelection(inputId, containerId, countId) {
    let selectedFiles = [];

    document.getElementById(inputId).addEventListener('change', function () {
        const newFiles = Array.from(this.files);

        // Thêm file mới vào danh sách nếu chưa có
        newFiles.forEach(file => {
            if (!selectedFiles.some(f => f.file.name === file.name && f.file.size === file.size)) {
                selectedFiles.push({ file, uploaded: false });
            }
        });

        updateFileList(containerId);
        updateInputFiles(inputId);
        updateFileCount(countId);
    });

    // Hàm để cập nhật danh sách hiển thị file
    function updateFileList(containerId) {
        const fileListContainer = document.getElementById(containerId);
        fileListContainer.innerHTML = '';

        selectedFiles.forEach((item, index) => {
            const { file, uploaded } = item;
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';

            const fileName = document.createElement('span');
            fileName.className = 'file-name';
            fileName.textContent = file.name;

            const fileSize = document.createElement('span');
            fileSize.className = 'file-size';
            fileSize.textContent = `(${(file.size / 1024).toFixed(1)}K)`; // Chuyển đổi kích thước sang KB

            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            const progress = document.createElement('div');
            progress.className = 'progress';
            progressBar.appendChild(progress);

            const deleteButton = document.createElement('span');
            deleteButton.className = 'delete-button';
            deleteButton.textContent = 'X';

            // Xóa file khi nhấn nút "X"
            deleteButton.addEventListener('click', function () {
                selectedFiles.splice(index, 1);
                updateFileList(containerId);
                updateInputFiles(inputId);
                updateFileCount(countId);
            });

            fileItem.appendChild(fileName);
            fileItem.appendChild(progressBar);
            fileItem.appendChild(fileSize);
            fileItem.appendChild(deleteButton);
            fileListContainer.appendChild(fileItem);

            // Giả lập tiến trình upload nếu chưa upload
            if (!uploaded) {
                let uploadProgress = 0;
                const uploadSpeed = Math.min(Math.max(file.size / 10240, 100), 1000); // Giả lập tốc độ upload dựa vào kích thước file
                const uploadInterval = setInterval(() => {
                    uploadProgress += 10;
                    progress.style.width = `${uploadProgress}%`;
                    if (uploadProgress >= 100) {
                        clearInterval(uploadInterval);
                        item.uploaded = true;
                        progressBar.style.display = 'none';  // Ẩn thanh progress khi upload xong
                    }
                }, uploadSpeed); // Tốc độ upload dựa vào kích thước file
            } else {
                progress.style.width = '100%';
                progressBar.style.display = 'none';  // Ẩn thanh progress nếu đã upload
            }
        });
    }

    // Hàm để cập nhật lại input với các file đã chọn
    function updateInputFiles(inputId) {
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(item => dataTransfer.items.add(item.file));
        document.getElementById(inputId).files = dataTransfer.files;
    }

    // Hàm để cập nhật số lượng file đã chọn
    function updateFileCount(countId) {
        const fileCountContainer = document.getElementById(countId);
        if (fileCountContainer) {
            fileCountContainer.textContent = `${selectedFiles.length} tệp đã chọn`;
        }
    }
}

// Sử dụng hàm cho từng form riêng biệt
document.addEventListener('DOMContentLoaded', function () {
    handleFileSelection('attachment-create', 'file-dropdown-create', 'file-count-create');
    handleFileSelection('attachment-sent', 'file-dropdown-sent', 'file-count-sent');
    handleFileSelection('attachment-received', 'file-dropdown-received', 'file-count-received');
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