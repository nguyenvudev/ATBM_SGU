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

// Delete icon mail received
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

// Delete icon mail send
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

// Show account
document.addEventListener("DOMContentLoaded", function() {
    // // Get the elements
    // const mailCreateBtn = document.querySelector('.mail-create');
    const mailReceivedBtn = document.querySelector('.mail-received');
    const mailSendBtn = document.querySelector('.mail-send');
    const mailTrashBtn = document.querySelector('.mail-trash');

    // const formMailCreate = document.querySelector('.form-create-mail');
    const formMailReceived = document.querySelector('.form-mail-received');
    const formMailSend = document.querySelector('.form-mail-send');
    const formMailTrash = document.querySelector('.form-trash-mail');

    // Function to remove active class from all forms except the mail-create form
    function resetForms() {
        formMailReceived.classList.remove('active');
        formMailSend.classList.remove('active');
        formMailTrash.classList.remove('active');
    }

    // Show mail-received by default
    formMailReceived.classList.add('active');

    // Add event listeners to buttons
    // mailCreateBtn.addEventListener('click', function() {
    //     formMailCreate.classList.toggle('active'); // Toggle instead of add
    // });

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
    })
});

document.addEventListener("DOMContentLoaded", function() {
    const formMailCreate = document.querySelector('.form-create-mail');
    const closeComposeIcon = document.getElementById('close-compose');

    // Hàm để tắt form
    function closeCreateMail() {
        formMailCreate.classList.remove('active'); // Xóa class active để ẩn form
    }

    // Bắt sự kiện khi nhấn vào biểu tượng "x"
    closeComposeIcon.addEventListener('click', closeCreateMail);

    // Bắt sự kiện khi nhấp ra ngoài form
    document.addEventListener('click', function(event) {
        if (!formMailCreate.contains(event.target) && !event.target.closest('.mail-create')) {
            closeCreateMail();
        }
    });

    // Giữ nguyên chức năng mở form từ sidebar
    const mailCreateBtn = document.querySelector('.mail-create');
    mailCreateBtn.addEventListener('click', function() {
        formMailCreate.classList.toggle('active'); // Mở/đóng form
    });
});






// Functionality for account profile toggle
let isFormVisible = false;
    const btnForm = document.querySelector(".profile-details");
    btnForm.addEventListener("click", function () {
        if (isFormVisible == false) {
            btnForm.classList.add("active");
            isFormVisible = true;
        } else {
            btnForm.classList.remove("active");
            isFormVisible = false;
        }
    });

    let isFormRecover = false;
    const btnRecover = document.querySelector(".recover-key button");
    const formRecover = document.querySelector(".form-recover-key");

    btnRecover.addEventListener("click", function(e) {
        e.preventDefault(); // Ngăn chặn nút gửi form mặc định
        if (isFormRecover == false) {
            formRecover.style.opacity = 1;
            formRecover.style.visibility = "visible";
            formRecover.style.transform = "scale(1)";
            isFormRecover = true;
        } else {
            formRecover.style.opacity = 0;
            formRecover.style.visibility = "hidden";
            formRecover.style.transform = "scale(0)";
            isFormRecover = false;
        }
    });


// attachment
document.getElementById('file-upload').addEventListener('change', function() {
    const fileList = document.getElementById('file-list');
    const mainContent = document.getElementById('main');
    const files = this.files;

    // Xóa nội dung cũ
    fileList.innerHTML = '';
    mainContent.innerHTML = ''; // Xóa nội dung chính trước khi thêm mới

    // Tạo dropdown (select element)
    const select = document.createElement('select');
    select.className = 'file-dropdown';

    const defaultOption = document.createElement('option');
    defaultOption.text = 'Danh sách file';
    select.appendChild(defaultOption);

    if (files.length > 0) {
        // Lặp qua từng file
        for (let i = 0; i < files.length; i++) {
            // Kiểm tra nếu file là ảnh
            if (files[i].type.startsWith('image/')) {
                const imgSrc = URL.createObjectURL(files[i]);
                const imgTag = `<img src="${imgSrc}" width="200" height="200" style="margin-right: 20px; border-radius: 5px; border: 1px solid #ddd;">`;

                // Thêm hình ảnh vào nội dung chính
                mainContent.innerHTML += imgTag; // Thêm vào nội dung chính với thẻ img

            } else {
                // Nếu file không phải ảnh, thêm vào dropdown
                const option = document.createElement('option');
                option.text = files[i].name;
                select.appendChild(option);
            }
        }

        // Chỉ hiển thị dropdown nếu có file không phải ảnh
        if (select.children.length > 1) {
            fileList.appendChild(select);
        }
    } else {
        const noFileMsg = document.createElement('p');
        noFileMsg.textContent = 'Không có file nào được chọn.';
        fileList.appendChild(noFileMsg);
    }
});
function updateBody() {
    // Cập nhật giá trị của trường ẩn 'body' từ nội dung của <div id="main">
    document.getElementById('hidden-body').value = document.getElementById('main').innerHTML;
}
