import pdfplumber
from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, session , send_from_directory , send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file
import os
from models import db, User, EncryptedEmail
from flask import redirect, url_for, session, render_template
import pytz
from utils import (
    generate_keys,
    serialize_keys,
    rsa_encrypt,
    rsa_decrypt,
    aes_encrypt,
    aes_decrypt,
    create_signature,
    generate_aes_key,
)
import os
from sqlalchemy.exc import IntegrityError
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_encryption.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('inbox'))
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email đã được sử dụng. Vui lòng chọn một email khác."

        # Kiểm tra tên người dùng có bị trùng không
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return "Tên người dùng đã được sử dụng. Vui lòng chọn một tên khác."

        # Băm mật khẩu trước khi lưu
        hashed_password = generate_password_hash(password)

        private_key, public_key = generate_keys()
        pem_private, pem_public = serialize_keys(private_key, public_key)

        user = User(email=email, username=username, password=hashed_password, public_key=pem_public,
                    private_key=pem_private)
        db.session.add(user)
        db.session.commit()

        # Đường dẫn thư mục lưu khóa riêng tư
        private_key_dir = 'private_keys'
        os.makedirs(private_key_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

        # Đường dẫn đầy đủ tới file khóa riêng tư
        private_key_filename = os.path.join(private_key_dir, f"private_key_{email}.pem")

        # Lưu khóa riêng vào file trong thư mục đã chỉ định
        with open(private_key_filename, 'w') as f:
            f.write(pem_private)

        # Gửi file khóa riêng tư cho người dùng
        return send_file(private_key_filename, as_attachment=True)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['username'] = user.username
            session['private_key'] = user.private_key
            return redirect(url_for('inbox'))
        return "Email hoặc mật khẩu không đúng."

    return render_template('login.html')


# thêm hiện thư đã gửi
@app.route('/inbox', methods=['GET'])
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    # Lấy danh sách email nhận
    received_emails = EncryptedEmail.query.filter_by(receiver_id=session['user_id'])

    # Nếu có từ khóa tìm kiếm, lọc email theo người gửi hoặc chủ đề
    if search_query:
        received_emails = received_emails.filter(
            (User.email.ilike(f'%{search_query}%')) |
            (EncryptedEmail.subject.ilike(f'%{search_query}%'))
        ).join(User, User.id == EncryptedEmail.sender_id)

    received_emails = received_emails.all()

    # Lấy danh sách email đã gửi
    sent_emails = (
        db.session.query(
            EncryptedEmail.subject,
            EncryptedEmail.timestamp,
            User.email.label('receiver_email')
        )
        .join(User, User.id == EncryptedEmail.receiver_id)
        .filter(EncryptedEmail.sender_id == session['user_id'])
        .all()
    )

    local_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    # Chuyển đổi thời gian cho email nhận
    for email in received_emails:
        sender = User.query.get(email.sender_id)
        email.sender_email = sender.email if sender else "Người gửi không xác định"
        if email.timestamp:
            utc_time = email.timestamp
            email.local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        else:
            email.local_time = None

    # Chuyển đổi thời gian cho email đã gửi
    email_data = []
    for email in sent_emails:
        local_time = email.timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz)
        email_data.append({
            'receiver_email': email.receiver_email,
            'subject': email.subject,
            'local_time': local_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('inbox.html', received_emails=received_emails, sent_emails=email_data)


# @app.route('/inbox', methods=['GET'])
# def inbox():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     search_query = request.args.get('search', '')
#     emails = EncryptedEmail.query.filter_by(receiver_id=session['user_id'])

#     # Nếu có từ khóa tìm kiếm, lọc email theo người gửi hoặc chủ đề
#     if search_query:
#         emails = emails.filter(
#             (User.email.ilike(f'%{search_query}%')) |
#             (EncryptedEmail.subject.ilike(f'%{search_query}%'))
#         ).join(User, User.id == EncryptedEmail.sender_id)

#     emails = emails.all()

#     local_tz = pytz.timezone('Asia/Ho_Chi_Minh')

#     for email in emails:
#         sender = User.query.get(email.sender_id)
#         email.sender_email = sender.email if sender else "Người gửi không xác định"
#         if email.timestamp:
#             utc_time = email.timestamp
#             email.local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
#         else:
#             email.local_time = None

#     return render_template('inbox.html', emails=emails)


@app.route('/send', methods=['GET', 'POST'])
def send_email():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient_email = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        if recipient_email == session['email']:
            return "Bạn không thể gửi email cho chính mình."

        receiver = User.query.filter_by(email=recipient_email).first()
        if not receiver:
            return "Người nhận không tồn tại."

        aes_key = generate_aes_key()
        encrypted_body = aes_encrypt(body.encode('utf-8'), aes_key)
        encrypted_aes_key = rsa_encrypt(aes_key.hex(), receiver.public_key)

        signature = create_signature(body, session['private_key'])

        # Handle attachment
        attachment = request.files.get('attachment')
        attachment_filename = None
        encrypted_attachment_hex = None  # Biến để lưu nội dung mã hóa
        if attachment:
            encrypted_attachment = aes_encrypt(attachment.read(), aes_key)
            encrypted_attachment_hex = encrypted_attachment.hex()  # Lưu dạng hex
            attachment_filename = f"encrypted_{attachment.filename}"

            # Lưu file mã hóa
            os.makedirs('attachments', exist_ok=True)
            with open(os.path.join('attachments', attachment_filename), 'wb') as f:
                f.write(encrypted_attachment)

        email = EncryptedEmail(
            sender_id=session['user_id'],
            receiver_id=receiver.id,
            subject=subject,
            body=encrypted_body.hex(),
            aes_key=encrypted_aes_key,
            signature=signature,
            attachment=attachment_filename,
            encrypted_attachment_content=encrypted_attachment_hex  # Thêm cột để lưu nội dung mã hóa
        )
        db.session.add(email)
        db.session.commit()
        return "Email đã được gửi."

    return render_template('send_email.html')


# @app.route('/send', methods=['GET', 'POST'])
# def send_email():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#
#     if request.method == 'POST':
#         recipient_email = request.form['recipient']
#         subject = request.form['subject']
#         body = request.form['body']
#
#
#         # Kiểm tra nếu người gửi đang cố gửi email cho chính mình
#         if recipient_email == session['email']:
#             return "Bạn không thể gửi email cho chính mình."
#
#         receiver = User.query.filter_by(email=recipient_email).first()
#         if not receiver:
#             return "Người nhận không tồn tại."
#
#         aes_key = generate_aes_key()
#         encrypted_body = aes_encrypt(body.encode('utf-8'), aes_key)
#         encrypted_aes_key = rsa_encrypt(aes_key.hex(), receiver.public_key)
#
#         signature = create_signature(body, session['private_key'])
#
#         # Handle attachment
#         attachment = request.files.get('attachment')
#         attachment_filename = None
#         if attachment:
#             # Mã hóa file đính kèm
#             encrypted_attachment = aes_encrypt(attachment.read(), aes_key)
#             attachment_filename = f"encrypted_{attachment.filename}"
#
#             # Lưu file mã hóa
#             os.makedirs('attachments', exist_ok=True)
#             with open(os.path.join('attachments', attachment_filename), 'wb') as f:
#                 f.write(encrypted_attachment)
#
#         email = EncryptedEmail(
#             sender_id=session['user_id'],
#             receiver_id=receiver.id,
#             subject=subject,
#             body=encrypted_body.hex(),
#             aes_key=encrypted_aes_key,
#             signature=signature,
#             attachment=attachment_filename
#         )
#         db.session.add(email)
#         db.session.commit()
#         return "Email đã được gửi."
#
#     return render_template('send_email.html')



@app.route('/decrypt_email/<int:email_id>', methods=['GET', 'POST'])
def decrypt_email(email_id):
    email = EncryptedEmail.query.get_or_404(email_id)
    decrypted_body = None
    decrypted_attachment_path = None
    decryption_error = None

    if request.method == 'POST':
        action = request.form.get('action')
        private_key_file = request.files.get('private_key_file')

        if private_key_file:
            try:
                # Đọc nội dung của tệp khóa riêng
                private_key = private_key_file.read().decode('utf-8')

                # Giải mã khóa AES
                decrypted_aes_key = rsa_decrypt(email.aes_key, private_key)
                if decrypted_aes_key is None:
                    raise ValueError("Giải mã khóa AES không thành công.")

                decrypted_aes_key_bytes = bytes.fromhex(decrypted_aes_key)

                # Nếu action là 'decrypt_both', thực hiện cả giải mã nội dung và tệp đính kèm
                if action == 'decrypt_both':
                    # Giải mã nội dung email
                    decrypted_body_bytes = aes_decrypt(bytes.fromhex(email.body), decrypted_aes_key_bytes)
                    decrypted_body = decrypted_body_bytes.decode('utf-8')

                    # Giải mã tệp đính kèm (nếu có)
                    if email.attachment:
                        # Tạo thư mục nếu chưa tồn tại
                        os.makedirs('attachments', exist_ok=True)

                        # Đường dẫn tệp đính kèm
                        attachment_path = os.path.join('attachments', email.attachment)

                        # Đọc tệp đã mã hóa
                        with open(attachment_path, 'rb') as file:
                            encrypted_data = file.read()

                        # Giải mã dữ liệu
                        decrypted_attachment = aes_decrypt(encrypted_data, decrypted_aes_key_bytes)

                        # Tạo đường dẫn để lưu tệp đã giải mã với đúng định dạng
                        decrypted_attachment_path = os.path.join('attachments', 'decrypted_' + email.attachment)
                        with open(decrypted_attachment_path, 'wb') as decrypted_file:
                            decrypted_file.write(decrypted_attachment)

            except Exception as e:
                decryption_error = f"Giải mã thất bại: {str(e)}"

    return render_template('decrypt_email.html', email=email, decrypted_body=decrypted_body,
                           decryption_error=decryption_error, decrypted_attachment_path=decrypted_attachment_path)

@app.route('/download_attachment/<int:email_id>', methods=['GET', 'POST'])
def download_attachment(email_id):
    email = EncryptedEmail.query.get_or_404(email_id)

    if request.method == 'POST':
        private_key = request.form.get('private_key')
        if email.attachment and private_key:
            attachment_path = os.path.join('attachments', email.attachment)

            # Đọc tệp đã mã hóa
            with open(attachment_path, 'rb') as file:
                encrypted_data = file.read()

            try:
                # Giải mã khóa AES
                decrypted_aes_key = rsa_decrypt(email.aes_key, private_key)
                decrypted_aes_key_bytes = base64.b64decode(decrypted_aes_key)

                # Giải mã dữ liệu
                decrypted_body = aes_decrypt(encrypted_data, decrypted_aes_key_bytes)

                # Đường dẫn lưu tệp giải mã
                decrypted_file_path = os.path.join('downloads', 'decrypted_' + email.attachment)

                # Xóa tệp cũ nếu đã tồn tại
                if os.path.exists(decrypted_file_path):
                    os.remove(decrypted_file_path)

                # Lưu file đã giải mã
                with open(decrypted_file_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted_body)

                return send_file(decrypted_file_path, as_attachment=True)  # Tải file đã giải mã về

            except Exception as e:
                return f"Không thể giải mã file đính kèm: {str(e)}"
        else:
            return "Cần có khóa riêng để giải mã tệp đính kèm."

    return render_template('download_attachment.html', email=email)

@app.route('/download_decrypted_file')
def download_decrypted_file():
    file_path = request.args.get('file_path')

    if file_path and os.path.exists(file_path):
        # Lấy tên file gốc để đặt tên cho file tải xuống
        filename = os.path.basename(file_path)

        # Sử dụng hàm `send_file` để gửi file với đúng định dạng
        return send_file(file_path, as_attachment=True, download_name=filename)

    return "Không tìm thấy tệp đã giải mã."


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    return "Đã xảy ra lỗi: " + str(error.orig), 400



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/recover_private_key', methods=['GET', 'POST'])
def recover_private_key():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Đường dẫn đến thư mục để lưu tệp khóa riêng
            directory = 'private_keys'
            os.makedirs(directory, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

            # Tạo tên tệp với đường dẫn đầy đủ
            private_key_filename = os.path.join(directory, f"private_key_{email}.pem")
            with open(private_key_filename, 'w') as f:
                f.write(user.private_key)

            # Gửi file khóa riêng tư cho người dùng
            return send_file(private_key_filename, as_attachment=True)

        return "Email hoặc mật khẩu không đúng."

    return render_template('recover_private_key.html')


@app.route('/delete_email/<int:email_id>', methods=['POST'])
def delete_email(email_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    email = EncryptedEmail.query.get_or_404(email_id)

    # Kiểm tra xem người dùng có quyền xóa email này không
    if email.receiver_id != session['user_id']:
        return "Bạn không có quyền xóa thư này."

    try:
        # Xóa file đính kèm nếu có
        if email.attachment:
            attachment_path = os.path.join('attachments', email.attachment)
            if os.path.exists(attachment_path):
                os.remove(attachment_path)

        # Xóa email từ cơ sở dữ liệu
        db.session.delete(email)
        db.session.commit()

        return redirect(url_for('inbox'))
    except Exception as e:
        db.session.rollback()
        return f"Đã xảy ra lỗi khi xóa email: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
