import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
import base64
import pdfplumber

from os.path import basename
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import pdfplumber
from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

from models import db, User, EncryptedEmail, EncryptForward
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, EncryptedEmail, EncryptForward, ConnectAES
from bs4 import BeautifulSoup
from flask_mail import Mail
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Import CORS
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
import random
import string

# Khởi tạo ứng dụng Flask
app = Flask(__name__)


CORS(app)  # Cho phép tất cả các nguồn kết nối đến server Flask

socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả các origin kết nối đến

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_encryption.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=100)
app.secret_key = os.urandom(24)

# Cấu hình SMTP email (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ikon1605@gmail.com'  # Email của bạn
app.config['MAIL_PASSWORD'] = 'iyyo oxhg cnji epfm'  # Mật khẩu email của bạn

mail = Mail(app)
db.init_app(app)

# Hàm tạo mã token ngẫu nhiên
def generate_token(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))



from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import smtplib

def send_reset_email(user_email, token):
    msg = MIMEMultipart()

    # Đặt người gửi với mã hóa UTF-8
    sender_name = Header('Tên Người Gửi', 'utf-8').encode()
    msg['From'] = formataddr((sender_name, app.config['MAIL_USERNAME']))
    msg['To'] = user_email

    # Đặt tiêu đề với mã hóa UTF-8
    subject = Header("Mã xác nhận khôi phục mật khẩu", 'utf-8').encode()
    msg['Subject'] = subject

    # Nội dung email (sử dụng UTF-8)
    body = f"Mã xác nhận để khôi phục mật khẩu của bạn là: {token}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Gửi email
    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.ehlo()  # Bắt đầu giao thức giao tiếp với máy chủ
            server.starttls()  # Bảo mật kết nối
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

            # Chuyển đổi `msg` thành chuỗi và đảm bảo mã hóa UTF-8
            server.sendmail(app.config['MAIL_USERNAME'], user_email, msg.as_string().encode('utf-8'))
            print(f"Đã gửi mã xác nhận đến {user_email}")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")


# Danh sách các tên miền email được phép
ALLOWED_DOMAINS = ['ATBM.com', 'ATBM.org']

CORS(app)  # Cho phép tất cả các nguồn kết nối đến server Flask

socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả các origin kết nối đến

with app.app_context():
    db.create_all()

# Trang chủ
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('inbox'))
    return render_template('index.html')

# Chức năng quên mật khẩu
# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email_backup']
#         user = User.query.filter_by(backup_email = email).first()
#
#
#         print(user.backup_email)
#         if user and user.backup_email:
#         # Kiểm tra xem người dùng có email dự phòng không
#             # Tạo token và gửi email
#             token = generate_token()
#             session['reset_token'] = token
#             session['reset_email'] = email
#             send_reset_email(email, token)  # Gửi email đến email dự phòng
#             return jsonify(success=True, message="Mã xác nhận đã được gửi đến email dự phòng của bạn.")
#         else:
#             return jsonify(success=False, message="Email không hợp lệ hoặc không có email dự phòng.")
#
#     return render_template('forgot_password.html')
#
# # Chức năng thay đổi mật khẩu
# @app.route('/reset_password', methods=['GET', 'POST'])
# def reset_password():
#     if request.method == 'POST':
#         token = request.form['token']
#         new_password = request.form['new_password']
#         confirm_password = request.form['confirm_password']
#
#         # Kiểm tra token và email trong session
#         if 'reset_token' in session and 'reset_email' in session:
#             reset_email = session['reset_email']  # Lấy email từ session để dễ kiểm tra
#             print(f"Email trong session: {reset_email}")  # Log email để kiểm tra
#             if session['reset_token'] == token:  # Kiểm tra token
#                 if new_password == confirm_password:  # Kiểm tra mật khẩu mới và xác nhận mật khẩu
#                     # Tìm người dùng theo backup_email thay vì email
#                     user = User.query.filter_by(backup_email=reset_email).first()
#                     if user:
#                         # Băm mật khẩu mới và cập nhật vào cơ sở dữ liệu
#                         hashed_password = generate_password_hash(new_password)
#                         user.password = hashed_password
#                         db.session.commit()
#
#                         # Xóa thông tin trong session
#                         session.pop('reset_token', None)
#                         session.pop('reset_email', None)
#
#                         return jsonify(success=True, message="Mật khẩu đã được thay đổi thành công.")
#                     else:
#                         print(f"Không tìm thấy người dùng với email dự phòng: {reset_email}")  # Log lỗi chi tiết
#                         return jsonify(success=False, message="Không tìm thấy người dùng.")
#                 else:
#                     return jsonify(success=False, message="Mật khẩu không khớp.")
#             else:
#                 return jsonify(success=False, message="Mã xác nhận không hợp lệ.")
#         else:
#             return jsonify(success=False, message="Phiên làm việc không hợp lệ hoặc đã hết hạn.")
#
#     return render_template('reset_password.html')


# Chức năng quên mật khẩu
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email_primary = request.form['email']       # Primary email input
        email_backup = request.form['email_backup'] # Backup email input

        # Fetch user by primary email and validate the backup email
        user = User.query.filter_by(email=email_primary, backup_email=email_backup).first()

        if user:
            # Generate token and send reset email if backup email is correct
            token = generate_token()
            session['reset_token'] = token
            session['reset_email'] = email_backup
            send_reset_email(email_backup, token)  # Send email to backup email
            return jsonify(success=True, message="Mã xác nhận đã được gửi đến email dự phòng của bạn.")
        else:
            return jsonify(success=False, message="Email chính hoặc email dự phòng không hợp lệ.")

    return render_template('forgot_password.html')

# Chức năng thay đổi mật khẩu
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        token = request.form['token']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra token và email trong session
        if 'reset_token' in session and 'reset_email' in session:
            reset_email = session['reset_email']  # Lấy email từ session để dễ kiểm tra
            print(f"Email trong session: {reset_email}")  # Log email để kiểm tra
            if session['reset_token'] == token:  # Kiểm tra token
                if new_password == confirm_password:  # Kiểm tra mật khẩu mới và xác nhận mật khẩu
                    # Tìm người dùng theo backup_email thay vì email
                    user = User.query.filter_by(backup_email=reset_email).first()
                    if user:
                        # Băm mật khẩu mới và cập nhật vào cơ sở dữ liệu
                        hashed_password = generate_password_hash(new_password)
                        user.password = hashed_password
                        db.session.commit()

                        # Xóa thông tin trong session
                        session.pop('reset_token', None)
                        session.pop('reset_email', None)

                        return jsonify(success=True, message="Mật khẩu đã được thay đổi thành công.")
                    else:
                        print(f"Không tìm thấy người dùng với email dự phòng: {reset_email}")  # Log lỗi chi tiết
                        return jsonify(success=False, message="Không tìm thấy người dùng.")
                else:
                    return jsonify(success=False, message="Mật khẩu không khớp.")
            else:
                return jsonify(success=False, message="Mã xác nhận không hợp lệ.")
        else:
            return jsonify(success=False, message="Phiên làm việc không hợp lệ hoặc đã hết hạn.")

    return render_template('reset_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        backup_email = request.form['backup_email']
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra tên miền của email
        domain = email.split('@')[-1]  # Lấy tên miền từ email
        if domain not in ALLOWED_DOMAINS:
            return jsonify(success=False, message="Tên miền email không hợp lệ. Vui lòng sử dụng email với tên miền hợp lệ.")

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

        user = User(email=email, username=username, password=hashed_password, public_key=pem_public, private_key=private_key_pass ,backup_email = backup_email)
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
        .order_by(EncryptedEmail.timestamp.desc()) 
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
        keyaes_email_id = ConnectAES.query.filter_by(id_body=email.id).first()
        keyaes_email_sender = db.session.get(EncryptForward, keyaes_email_id.id_aes)

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

                #kiểm tra id nào để giải mã đúng khóa
                decrypted_aes_key = None
                if keyaes_email_sender.receiver_id == session['user_id']:
                    decrypted_aes_key = rsa_decrypt(keyaes_email_sender.key_receiver, private_key)
                else :
                    decrypted_aes_key = rsa_decrypt(keyaes_email_sender.key_sender, private_key)

                decrypted_aes_key_bytes = bytes.fromhex(decrypted_aes_key)
                decrypted_body_bytes = aes_decrypt(bytes.fromhex(email.body), decrypted_aes_key_bytes)
                decrypted_body = decrypted_body_bytes.decode('utf-8')

                # Loại bỏ các thẻ HTML khỏi nội dung đã giải mã
                soup = BeautifulSoup(decrypted_body, 'html.parser')
                decrypted_body = soup.get_text(separator=' ')
                
                # Chỉ giữ nội dung trước "----Forwarded message----" 
                if "----Forwarded message----" in decrypted_body: 
                    decrypted_body = decrypted_body.split("----Forwarded message----")[0]
                
            email.decrypted_body = decrypted_body
        except Exception as e:
            email.decrypted_body = "Giải mã thất bại."

        # Chuyển đổi thời gian cho email đã gửi

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
        return jsonify({"success": False, "message": "Không được xác thực!!!"})

    data = request.get_json()
    email_ids = data.get('email_ids')
    user_id = session['user_id']

    if not email_ids:
        return jsonify({"success": False, "message": "Chưa chọn ít nhất một email!"})

    try:
        for email_id in email_ids:
            print(f"Cố gắng tìm email có ID: {email_id}")  
            email = EncryptedEmail.query.get(email_id)
            
            if not email:
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
        return jsonify({'success': False, 'message': 'Không được xác thực!!!'})
    
    user_id = session['user_id']
    trash_emails = EncryptedEmail.query.filter(
        ((EncryptedEmail.receiver_id == user_id) & (EncryptedEmail.receiver_deleted == True)) |
        ((EncryptedEmail.sender_id == user_id) & (EncryptedEmail.sender_deleted == True))
    ).order_by(EncryptedEmail.timestamp.desc()).all()
    
    emails_data = []
    local_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    for email in trash_emails:
        sender = User.query.get(email.sender_id)
        # Kiểm tra nếu email này là của người dùng hiện tại
        sender_email = sender.email if sender else "Người gửi không xác định"
        if email.sender_id == user_id:
            sender_email += " | tôi"
        
        # Xử lý thời gian
        if email.timestamp:
            utc_time = email.timestamp
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        else:
            local_time = None

        emails_data.append({
            'id': email.id,
            'sender_email': sender_email,
            'subject': email.subject,
            'local_time': local_time
        })
    
    return jsonify({'success': True, 'emails': emails_data})

@app.route('/delete_emails', methods=['POST'])
def delete_emails():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Không được xác thực!!!"})

    data = request.get_json()
    email_ids = data.get('emailIds', [])
    emails = EncryptedEmail.query.filter(EncryptedEmail.id.in_(email_ids)).all()

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
        return jsonify({"success": False, "message": "Không được xác thực!!!"})

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

        # Không cho phép gửi email cho chính mình
        if recipient_email == session['email']:
            flash("Bạn không thể gửi email cho chính mình.")
            return redirect(url_for('inbox'))

        # Tìm người nhận
        receiver = User.query.filter_by(email=recipient_email).first()
        if not receiver:
            flash("Người nhận không tồn tại.")
            return redirect(url_for('inbox'))

        # Kiểm tra email trước đó và lấy khóa AES nếu có
        previous_email = EncryptedEmail.query.filter(
            ((EncryptedEmail.sender_id == session['user_id']) & (EncryptedEmail.receiver_id == receiver.id)) |
            ((EncryptedEmail.sender_id == receiver.id) & (EncryptedEmail.receiver_id == session['user_id']))
        ).first()

        aes_key = None  # Khóa AES mặc định
        forward_mail = None  # Dữ liệu mã hóa AES
        aes_key_en_id = None
        if previous_email:
            try:
                ib_body_key = previous_email.id
                sender = User.query.filter_by(email=session['email']).first()
                table_connect_aes = ConnectAES.query.filter_by(id_body=ib_body_key).first()
                aes_key_en = EncryptForward.query.filter_by(id=table_connect_aes.id_aes).first()
                aes_key_en_id = aes_key_en.id

                if sender.id == previous_email.sender_id and aes_key_en:
                    aes_key_by = rsa_decrypt(aes_key_en.key_sender, session['private_key'])
                elif sender.id == previous_email.receiver_id and aes_key_en:
                    aes_key_by = rsa_decrypt(aes_key_en.key_receiver, session['private_key'])
                else:
                    aes_key_by = None

                if aes_key_by:
                    aes_key = bytes.fromhex(aes_key_by)
            except Exception as e:
                flash(f"Lỗi khi lấy khóa AES từ email trước đó: {str(e)}")
                return redirect(url_for('inbox'))

        # Nếu không tìm thấy khóa AES, tạo mới
        if not aes_key:
            aes_key = generate_aes_key()
            encrypted_aes_key_receiver = rsa_encrypt(aes_key.hex(), receiver.public_key)
            encrypted_aes_key_sender = rsa_encrypt(aes_key.hex(), session['public_key'])
            forward_mail = EncryptForward(
                key_sender=encrypted_aes_key_sender,
                key_receiver=encrypted_aes_key_receiver,
                sender_id=session['user_id'],
                receiver_id=receiver.id

            )
            db.session.add(forward_mail)
            db.session.commit()

        # Mã hóa nội dung email
        encrypted_body = aes_encrypt(body.encode('utf-8'), aes_key)

        # Mã hóa và lưu tệp đính kèm
        attachments = request.files.getlist('attachment')
        encrypted_attachments = []
        for attachment in attachments:
            if attachment and attachment.filename:  # Kiểm tra tệp hợp lệ
                encrypted_data = aes_encrypt(attachment.read(), aes_key)
                encrypted_filename = f"encrypted_{attachment.filename}"
                encrypted_attachments.append({
                    "filename": encrypted_filename,
                    "content": encrypted_data.hex()
                })
                os.makedirs('attachments', exist_ok=True)
                with open(os.path.join('attachments', encrypted_filename), 'wb') as f:
                    f.write(encrypted_data)

        # Tạo chữ ký để xác thực email
        try:
            signature = create_signature(body, session['private_key'])
        except Exception as e:
            flash(f"Lỗi khi tạo chữ ký: {str(e)}")
            return redirect(url_for('inbox'))

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

        # Lưu thông tin kết nối AES
        if not aes_key_en_id:
            connect_aes = ConnectAES(
                id_body=email.id,
                id_aes=forward_mail.id
            )
        else:
            connect_aes = ConnectAES(
                id_body=email.id,
                id_aes=aes_key_en_id
            )
        db.session.add(connect_aes)
        db.session.commit()

        # Phát sự kiện cho các client khác
        socketio.emit('new_email', {'message': 'Email đã được gửi.'})

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
    print(email_id)

    keyconnect_aes = ConnectAES.query.filter_by(id_body=email_id).first()
    keyAES_email = EncryptForward.query.filter_by(id=keyconnect_aes.id_aes).first()

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

            aes_decrypt_sender = None
            if keyAES_email.receiver_id == session['user_id']:
                aes_decrypt_sender = rsa_decrypt(keyAES_email.key_receiver, private_key)
            else:
                aes_decrypt_sender = rsa_decrypt(keyAES_email.key_sender, private_key)

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

                clean_filename = os.path.basename(decrypted_attachment_path).replace("decrypted_", "").replace(
                    "encrypted_", "")
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

        decrypted_aes_key = None
        if keyAES_email.receiver_id == session['user_id']:
            decrypted_aes_key = rsa_decrypt(keyAES_email.key_receiver, private_key)
        else:
            decrypted_aes_key = rsa_decrypt(keyAES_email.key_sender, private_key)

        # Giải mã nội dung email (giữ nguyên định dạng xuống dòng)
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
    print(decryption_error)
    return jsonify({
        'subject': email.subject,
        'sender_email': sender.email if sender else "Không xác định",
        'timestamp': timestamp_formatted,
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
            return jsonify(success=False, message="Mật khẩu mới và mật khẩu xác nhận không khớp.")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, current_password):
            try:
                # Decrypt the user's current private key with the old password
                decrypted_private_key = decrypt_with_password(current_password, user.private_key)

                # Re-encrypt the private key with the new password
                new_encrypted_private_key = encrypt_with_password(new_password, decrypted_private_key)

                # Update the user's password and private key
                user.password = generate_password_hash(new_password)
                user.private_key = new_encrypted_private_key
                db.session.commit()

                return jsonify(success=True, message="Mật khẩu đã được đổi thành công.")
            except Exception as e:
                # Handle decryption or encryption errors
                return jsonify(success=False, message=f"Lỗi khi đổi mật khẩu: {str(e)}")
        else:
            return jsonify(success=False, message="Email hoặc mật khẩu hiện tại không đúng.")

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