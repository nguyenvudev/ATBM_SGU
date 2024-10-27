// Kích hoạt input file khi nhấn vào biểu tượng
document.getElementById('upload_icon').addEventListener('click', function() {
    document.getElementById('private_key_file').click();
});

// Hiển thị tên tệp khi người dùng chọn tệp
document.getElementById('private_key_file').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : 'Không có tệp nào được chọn';
    document.getElementById('file_name_display').textContent = fileName;
});
