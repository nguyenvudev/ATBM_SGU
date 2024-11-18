from datetime import datetime, timedelta
import json
from os.path import basename
import pytz
import pdfplumber
from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, EncryptedEmail, EncryptForward
from flask_cors import CORS
from bs4 import BeautifulSoup
from utils import (
    generate_keys,
    serialize_keys,
    rsa_encrypt,
    rsa_decrypt,
    aes_encrypt,
    aes_decrypt,
    create_signature,
    generate_aes_key,
    generate_aes_key_from_password,
    encrypt_with_password,
    decrypt_with_password
)
import os
from sqlalchemy.exc import IntegrityError
import base64


from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Import CORS

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_encryption.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=100)
app.secret_key = os.urandom(24)
db.init_app(app)

CORS(app)  # Cho phép tất cả các nguồn kết nối đến server Flask

socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả các origin kết nối đến

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

        # Kiểm tra email đã được sử dụng
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify(success=False, message="Email đã được sử dụng. Vui lòng chọn một email khác.")

        # Kiểm tra tên người dùng đã được sử dụng
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return jsonify(success=False, message="Tên người dùng đã được sử dụng. Vui lòng chọn một tên khác.")

        # Băm mật khẩu và tạo người dùng
        private_key, public_key = generate_keys()
        pem_private, pem_public = serialize_keys(private_key, public_key)

        private_key_pass = encrypt_with_password(password, pem_private)

        hashed_password = generate_password_hash(password)

        user = User(email=email, username=username, password=hashed_password, public_key=pem_public, private_key=private_key_pass)
        db.session.add(user)
        db.session.commit()

        # Đường dẫn tới file khóa riêng tư
        private_key_dir = 'private_keys'
        os.makedirs(private_key_dir, exist_ok=True)
        private_key_filename = os.path.join(private_key_dir, f"private_key_{email}.pem")

        # Lưu khóa riêng tư vào file
        with open(private_key_filename, 'w') as f:
            f.write(pem_private)

        # Lưu thông tin vào session
        session['user_id'] = user.id
        session['email'] = user.email
        session['username'] = user.username
        session['private_key'] = decrypt_with_password(password, user.private_key)
        session['public_key'] = user.public_key

        # Gửi phản hồi JSON để client hiển thị modal thành công
        response = jsonify(success=True, message="Đăng ký thành công!")
        response.headers['X-Private-Key-File'] = private_key_filename  # Thêm tên file vào header để client có thể tải file

        return response

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Lưu thông tin vào session khi đăng nhập thành công
            session['user_id'] = user.id
            session['email'] = user.email
            session['username'] = user.username
            session['private_key'] = decrypt_with_password(password, user.private_key)
            session['public_key'] = user.public_key
            return redirect(url_for('inbox'))

        return jsonify(success=False, message="Email hoặc mật khẩu không đúng.")


    # return render_template('inbox.html')  # Change this to 'index.html'
@app.route('/inbox', methods=['GET'])
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    local_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    # Lấy danh sách email nhận (không phải đã xóa)
    received_emails = EncryptedEmail.query.filter_by(receiver_id=session['user_id'], receiver_deleted=False)

    if search_query:
        received_emails = received_emails.filter(
            (User.email.ilike(f'%{search_query}%')) |
            (EncryptedEmail.subject.ilike(f'%{search_query}%'))
        ).join(User, User.id == EncryptedEmail.sender_id)

    # Order received emails by timestamp descending
    received_emails = received_emails.order_by(EncryptedEmail.timestamp.desc()).all()

    # Lấy danh sách email đã gửi và sắp xếp theo thời gian giảm dần
    sent_emails = (
        db.session.query(
            EncryptedEmail.id,
            EncryptedEmail.subject,
            EncryptedEmail.timestamp,
            User.email.label('receiver_email'),
            EncryptedEmail.sender_deleted
        )
        .join(User, User.id == EncryptedEmail.receiver_id)
        .filter(EncryptedEmail.sender_id == session['user_id'], EncryptedEmail.sender_deleted == False)
        .order_by(EncryptedEmail.timestamp.desc())  # Đảm bảo thứ tự giảm dần
        .all()
    )

    # Chuyển đổi thời gian và chuẩn bị dữ liệu cho danh sách email đã gửi
    email_data = []
    for email in sent_emails:
        local_time = email.timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz)
        email_data.append({
            'id': email.id,
            'receiver_email': email.receiver_email,
            'subject': email.subject,
            'local_time': local_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for email in received_emails:
        sender = db.session.get(User, email.sender_id)
        keyaes_email_sender = EncryptForward.query.filter_by(id_body=email.id).first()
        email.sender_email = sender.email if sender else "Người gửi không xác định"

        # Giải mã nội dung email
        decrypted_body = None
        if email.timestamp:
            utc_time = email.timestamp
            email.local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        else:
            email.local_time = None

        try:
            private_key = session.get('private_key')
            if private_key:
                decrypted_aes_key = rsa_decrypt(keyaes_email_sender.key_receiver, private_key)
                decrypted_aes_key_bytes = bytes.fromhex(decrypted_aes_key)
                decrypted_body_bytes = aes_decrypt(bytes.fromhex(email.body), decrypted_aes_key_bytes)
                decrypted_body = decrypted_body_bytes.decode('utf-8')

                # Loại bỏ các thẻ HTML khỏi nội dung đã giải mã
                soup = BeautifulSoup(decrypted_body, 'html.parser')
                decrypted_body = soup.get_text(separator=' ')
                
            email.decrypted_body = decrypted_body
        except Exception as e:
            email.decrypted_body = "Giải mã thất bại."

    # Lấy danh sách email trong thùng rác
    trash_emails = EncryptedEmail.query.filter(
        ((EncryptedEmail.receiver_id == session['user_id']) & (EncryptedEmail.receiver_deleted == True)) |
        ((EncryptedEmail.sender_id == session['user_id']) & (EncryptedEmail.sender_deleted == True))
    ).order_by(EncryptedEmail.timestamp.desc()).all()

    for email in trash_emails:
        sender = User.query.get(email.sender_id)
        email.sender_email = sender.email if sender else "Người gửi không xác định"
        
        if email.timestamp:
            utc_time = email.timestamp
            email.local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        else:
            email.local_time = None

    return render_template('inbox.html', received_emails=received_emails, sent_emails=email_data, trash_emails=trash_emails)



@app.route('/move_to_trash', methods=['POST'])
def move_to_trash():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not authenticated"})

    data = request.get_json()
    email_ids = data.get('email_ids')
    user_id = session['user_id']

    if not email_ids:
        return jsonify({"success": False, "message": "Chưa chọn ít nhất một email!"})

    try:
        for email_id in email_ids:
            print(f"Attempting to find email with ID: {email_id}")  # Debugging log
            email = EncryptedEmail.query.get(email_id)
            
            if not email:  # If no email is found
                return jsonify({"success": False, "message": f"Không tìm thấy email với ID {email_id}!"})

            # Kiểm tra thư đã nhận hay đã gửi dựa trên sender_id và receiver_id
            if email.receiver_id == user_id:
                email.receiver_deleted = True
            elif email.sender_id == user_id:
                email.sender_deleted = True
            else:
                return jsonify({"success": False, "message": "Bạn không có quyền xóa email này"})
            
            db.session.commit()

        return jsonify({"success": True, "message": "Đã di chuyển email vào thùng rác."})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"})

@app.route('/get_trash_emails', methods=['GET'])
def get_trash_emails():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    user_id = session['user_id']
    trash_emails = EncryptedEmail.query.filter(
        ((EncryptedEmail.receiver_id == user_id) & (EncryptedEmail.receiver_deleted == True)) |
        ((EncryptedEmail.sender_id == user_id) & (EncryptedEmail.sender_deleted == True))
    ).order_by(EncryptedEmail.timestamp.desc()).all()

    emails_data = []
    local_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    for email in trash_emails:
        sender = User.query.get(email.sender_id)
        email.sender_email = sender.email if sender else "Người gửi không xác định"

        if email.timestamp:
            utc_time = email.timestamp
            email.local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        else:
            email.local_time = None

        emails_data.append({
            'id': email.id,
            'sender_email': email.sender_email,
            'subject': email.subject,
            'local_time': email.local_time
        })

    return jsonify({'success': True, 'emails': emails_data})

# @app.route('/delete_emails', methods=['POST'])
# def delete_emails():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     data = request.get_json()
#     email_ids = data.get('emailIds', [])
#     emails = EncryptedEmail.query.filter(EncryptedEmail.id.in_(email_ids)).all()

#     # Permanently delete the emails
#     for email in emails:
#         db.session.delete(email)

#     db.session.commit()

#     return jsonify({"message": "Emails deleted successfully"})  

@app.route('/delete_emails', methods=['POST'])
def delete_emails():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not authenticated"})

    data = request.get_json()
    email_ids = data.get('emailIds', [])
    emails = EncryptedEmail.query.filter(EncryptedEmail.id.in_(email_ids)).all()

    # Xóa email vĩnh viễn từ thùng rác
    for email in emails:
        # Kiểm tra xem người dùng có quyền xóa email này không
        if (email.receiver_id == session['user_id'] and email.receiver_deleted) or \
           (email.sender_id == session['user_id'] and email.sender_deleted):
            db.session.delete(email)
        else:
            return jsonify({"success": False, "message": "Không có quyền xóa email này"})

    db.session.commit()

    return jsonify({"success": True, "message": "Email đã được xóa thành công."})

@app.route('/delete_all_trash', methods=['POST'])
def delete_all_trash():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Not authenticated"})

    try:
        # Lấy tất cả thư trong thùng rác của người dùng
        emails_in_trash = EncryptedEmail.query.filter(
            ((EncryptedEmail.receiver_id == session['user_id']) & (EncryptedEmail.receiver_deleted == True)) |
            ((EncryptedEmail.sender_id == session['user_id']) & (EncryptedEmail.sender_deleted == True))
        ).all()

        # Xóa tất cả thư trong thùng rác
        for email in emails_in_trash:
            db.session.delete(email)

        db.session.commit()

        return jsonify({"success": True, "message": "Tất cả thư trong thùng rác đã được xóa thành công."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Lỗi khi xóa thư: {str(e)}"})

@app.route('/send', methods=['GET', 'POST'])
def send_email():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient_email = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        if recipient_email == session['email']:
            flash("Bạn không thể gửi email cho chính mình.")
            return redirect(url_for('inbox'))

        receiver = User.query.filter_by(email=recipient_email).first()
        if not receiver:
            flash("Người nhận không tồn tại.")
            return redirect(url_for('inbox'))

        # Kiểm tra xem người gửi và người nhận đã giao tiếp chưa
        previous_email = EncryptedEmail.query.filter(
            ((EncryptedEmail.sender_id == session['user_id']) & (EncryptedEmail.receiver_id == receiver.id)) |
            ((EncryptedEmail.sender_id == receiver.id) & (EncryptedEmail.receiver_id == session['user_id']))
        ).first()

        if previous_email:
            ib_body_key = previous_email.id
            aes_key_en = EncryptForward.query.filter_by(id_body=ib_body_key).first()
            if aes_key_en:
                aes_key_by = rsa_decrypt(aes_key_en.key_sender, session['private_key'])
                aes_key = bytes.fromhex(aes_key_by)
        else:
            # Trường hợp không tìm thấy, tạo AES key mới
            aes_key = generate_aes_key()

        # Mã hóa nội dung email với khóa AES
        encrypted_body = aes_encrypt(body.encode('utf-8'), aes_key)

        # Mã hóa khóa AES với khóa công khai của người nhận và người gửi
        encrypted_aes_key_receiver = rsa_encrypt(aes_key.hex(), receiver.public_key)
        encrypted_aes_key_sender = rsa_encrypt(aes_key.hex(), session['public_key'])

        # Tạo chữ ký để xác thực email
        signature = create_signature(body, session['private_key'])

        # Mã hóa và lưu các tệp đính kèm
        attachments = request.files.getlist('attachment')
        encrypted_attachments = []
        for attachment in attachments:
            if attachment:
                encrypted_data = aes_encrypt(attachment.read(), aes_key)
                encrypted_filename = f"encrypted_{attachment.filename}"
                encrypted_attachments.append({
                    "filename": encrypted_filename,
                    "content": encrypted_data.hex()
                })
                os.makedirs('attachments', exist_ok=True)
                with open(os.path.join('attachments', encrypted_filename), 'wb') as f:
                    f.write(encrypted_data)

        # Lưu email vào cơ sở dữ liệu
        email = EncryptedEmail(
            sender_id=session['user_id'],
            receiver_id=receiver.id,
            subject=subject,
            body=encrypted_body.hex(),
            attachments=json.dumps(encrypted_attachments)
        )

        db.session.add(email)
        db.session.commit()

        # Lưu thông tin mã hóa của AES key để gửi tới người nhận và người gửi
        if not previous_email:
            forward_mail = EncryptForward(
                id_body=email.id,
                key_sender=encrypted_aes_key_sender,
                key_receiver=encrypted_aes_key_receiver
            )
            db.session.add(forward_mail)
            db.session.commit()

        # Phát sự kiện cho tất cả các client khác
        socketio.emit('new_email', {'message': 'Email đã được gửi'})

        flash("Email đã được gửi.")
        return redirect(url_for('inbox'))

    return render_template('inbox.html')



@app.route('/decrypt_email/<int:email_id>', methods=['GET'])
def decrypt_email(email_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    email = EncryptedEmail.query.get_or_404(email_id)
    
    if not email.is_read:
        email.is_read = True
        db.session.commit()

    decrypted_body = None
    decrypted_attachments = []
    decryption_error = None

    # Kiểm tra nếu email là của người gửi
    is_sent_email = email.sender_id == session['user_id']
    keyAES_email = EncryptForward.query.filter_by(id_body=email_id).first()

        # Định dạng thời gian gửi
    # Thiết lập múi giờ cho thành phố Hồ Chí Minh
    local_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    if email.timestamp:
        local_time = email.timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz)
        timestamp_formatted = local_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        timestamp_formatted = "Không xác định"

        
    if is_sent_email:
        # Người gửi có thể giải mã nội dung đã gửi
        try:
            private_key = session.get('private_key')
            if not private_key:
                raise ValueError("Không tìm thấy khóa riêng tư trong phiên.")

            # Giải mã khóa AES bằng RSA
            aes_decrypt_sender = rsa_decrypt(keyAES_email.key_sender, private_key)
            if aes_decrypt_sender is None:
                raise ValueError("Giải mã khóa AES không thành công.")

            aes_decrypt_sender_bytes = bytes.fromhex(aes_decrypt_sender)

            # Giải mã nội dung email và giữ nguyên định dạng xuống dòng
            decrypted_body_bytes = aes_decrypt(bytes.fromhex(email.body), aes_decrypt_sender_bytes)
            decrypted_body = decrypted_body_bytes.decode('utf-8', errors='ignore')

            # Giải mã tệp đính kèm nếu có
            attachments = json.loads(email.attachments)
            for attachment in attachments:
                encrypted_data = bytes.fromhex(attachment['content'])
                decrypted_attachment = aes_decrypt(encrypted_data, aes_decrypt_sender_bytes)
                decrypted_attachment_path = os.path.join('attachments', 'decrypted_' + attachment['filename'])

                with open(decrypted_attachment_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted_attachment)

                clean_filename = os.path.basename(decrypted_attachment_path).replace("decrypted_", "").replace("encrypted_", "")
                decrypted_attachments.append({
                    'path': url_for('download_decrypted_file', file_path=decrypted_attachment_path),
                    'filename': clean_filename
                })
        except Exception as e:
            decryption_error = f"Giải mã thất bại: {str(e)}"
        receiver_email = db.session.get(User, email.receiver_id)
        return jsonify({
            'message': "Đây là email bạn đã gửi.",
            'subject': email.subject,
            'send_email': session['email'],  # Địa chỉ email của người gửi
            'receiver_email': receiver_email.email,
            'timestamp': timestamp_formatted,  # Thời gian gửi
            'decrypted_body_send': decrypted_body,
            'decryption_error': decryption_error,
            'decrypted_attachments': decrypted_attachments
        })

    # Logic giải mã cho người nhận
    sender = db.session.get(User, email.sender_id)

    try:
        private_key = session.get('private_key')
        if not private_key:
            raise ValueError("Không tìm thấy khóa riêng tư trong phiên.")

        decrypted_aes_key = rsa_decrypt(keyAES_email.key_receiver, private_key)
        if decrypted_aes_key is None:
            raise ValueError("Giải mã khóa AES không thành công.")

        decrypted_aes_key_bytes = bytes.fromhex(decrypted_aes_key)

        decrypted_body_bytes = aes_decrypt(bytes.fromhex(email.body), decrypted_aes_key_bytes)
        decrypted_body = decrypted_body_bytes.decode('utf-8', errors='ignore')

        attachments = json.loads(email.attachments)
        for attachment in attachments:
            encrypted_data = bytes.fromhex(attachment['content'])
            decrypted_attachment = aes_decrypt(encrypted_data, decrypted_aes_key_bytes)
            decrypted_attachment_path = os.path.join('attachments', 'decrypted_' + attachment['filename'])
            with open(decrypted_attachment_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_attachment)

            clean_filename = basename(decrypted_attachment_path).replace("decrypted_", "").replace("encrypted_", "")
            decrypted_attachments.append({
                'path': url_for('download_decrypted_file', file_path=decrypted_attachment_path),
                'filename': clean_filename
            })

    except Exception as e:
        decryption_error = f"Giải mã thất bại: {str(e)}"

    return jsonify({
        'subject': email.subject,
        'sender_email': sender.email if sender else "Không xác định",
        'timestamp': timestamp_formatted,  # Thời gian gửi
        'decrypted_body': decrypted_body,
        'decryption_error': decryption_error,
        'decrypted_attachments': decrypted_attachments
    })

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

                file_name = basename(decrypted_file_path).replace("decrypted_", "").replace("encrypted_", "")
                return send_file(decrypted_file_path, as_attachment=True, download_name=file_name)  # Tải file đã giải mã về

            except Exception as e:
                return f"Không thể giải mã file đính kèm: {str(e)}"
        else:
            return "Cần có khóa riêng để giải mã tệp đính kèm."

    return render_template('download_attachment.html', email=email)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email']
        current_password = request.form['ex-password']
        new_password = request.form['password']
        confirm_password = request.form['new_password']

        # Kiểm tra xem mật khẩu mới có trùng với mật khẩu xác nhận không
        if new_password != confirm_password:
            return "Mật khẩu mới và mật khẩu xác nhận không khớp."

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, current_password):
            # Cập nhật mật khẩu mới
            user.password = generate_password_hash(new_password)
            db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
            return "Mật khẩu đã được đổi thành công."

        return "Email hoặc mật khẩu hiện tại không đúng."

    return render_template('change_password.html')


@app.route('/download_decrypted_file')
def download_decrypted_file():
    file_path = request.args.get('file_path')

    if file_path and os.path.exists(file_path):
        # Lấy tên file gốc để đặt tên cho file tải xuống
        filename = os.path.basename(file_path).replace("decrypted_", "").replace("encrypted_", "")
        # Sử dụng hàm `send_file` có sẵn để gửi file với đúng định dạng
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


@app.before_request
def refresh_session_lifetime():
    if 'user_id' in session:
        session.permanent = True


@socketio.on('connect')
def handle_connect():
    print("A user connected.")
    # Các xử lý khi người dùng kết nối

@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected.")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)





