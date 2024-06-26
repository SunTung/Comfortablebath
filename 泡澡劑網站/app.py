from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mail import Mail, Message
from geopy.geocoders import Nominatim
import random
import re
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
geolocator = Nominatim(user_agent="geoapiExercises")

# 設置Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
mail = Mail(app)

verification_codes = {}
orders = {}  # 用於存儲用戶訂單
TRANSACTION_FEE_PERCENTAGE = 0.07  # 假設手續費為5%

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    msg = Message('驗證碼', sender='your-email@example.com', recipients=[email])
    msg.body = f'您的驗證碼是: {code}'
    mail.send(msg)

def validate_address(address):
    try:
        location = geolocator.geocode(address)
        if location and location.latitude and location.longitude:
            if location.latitude > 90 or location.latitude < -90 or location.longitude > 180 or location.longitude < -180:
                return False
            return True
    except:
        return False
    return False

def validate_phone(phone):
    # 台灣手機號碼正則表達式
    pattern = re.compile(r"^09[0-9]{8}$")
    return pattern.match(phone) is not None

def calculate_total_amount(cart):
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            total += product['price'] * int(quantity)
    return total

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products')
def products():
    return render_template('products.html', products=products)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if 'username' in session:
        if request.method == 'POST':
            cart = request.form.getlist('product')
            quantity = request.form.getlist('quantity')
            if not any(int(qty) > 0 for qty in quantity):
                flash('請至少選擇一件商品並且數量大於0')
                return redirect(url_for('orders'))
            session['cart'] = dict(zip(cart, quantity))
            return redirect(url_for('shipping'))
        return render_template('orders.html', products=products)
    return redirect(url_for('login'))

@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    if 'username' in session and 'cart' in session:
        if request.method == 'POST':
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']
            if not validate_phone(phone):
                flash('電話號碼格式錯誤，請輸入正確的電話號碼')
                return redirect(url_for('shipping'))

            phone_code = generate_verification_code()
            email_code = generate_verification_code()
            verification_codes[phone] = phone_code
            verification_codes[email] = email_code

            send_verification_email(email, email_code)
            flash('驗證碼已發送至您的電子郵件和手機，請輸入驗證碼進行驗證')
            return redirect(url_for('verify', address=address, phone=phone, email=email))
        return render_template('shipping.html')
    return redirect(url_for('login'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'username' in session and 'cart' in session:
        address = request.args.get('address')
        phone = request.args.get('phone')
        email = request.args.get('email')
        if request.method == 'POST':
            phone_code = request.form['phone_code']
            email_code = request.form['email_code']
            if verification_codes.get(phone) == phone_code and verification_codes.get(email) == email_code:
                if not validate_address(address):
                    flash('地址無法送達，請選擇有效的地址')
                    return redirect(url_for('shipping'))
                if 'addresses' not in session:
                    session['addresses'] = []
                if len(session['addresses']) < 2:
                    session['addresses'].append({'address': address, 'phone': phone, 'email': email})
                else:
                    flash('最多只能保存兩個地址，請刪除一個地址再添加')
                    return redirect(url_for('manage_addresses'))
                return redirect(url_for('payment'))
            else:
                flash('驗證碼錯誤，請重新輸入')
        return render_template('verify.html', phone=phone, email=email)
    return redirect(url_for('login'))

@app.route('/manage_addresses', methods=['GET', 'POST'])
def manage_addresses():
    if 'username' in session:
        if request.method == 'POST':
            if 'delete' in request.form:
                index = int(request.form['delete'])
                if 'addresses' in session and 0 <= index < len(session['addresses']):
                    del session['addresses'][index]
            return redirect(url_for('manage_addresses'))
        return render_template('manage_addresses.html', addresses=session.get('addresses', []))
    return redirect(url_for('login'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'username' in session and 'cart' in session and 'addresses' in session:
        if request.method == 'POST':
            payment_method = request.form['payment_method']
            session['payment_method'] = payment_method
            flash('當你申請退款時，我們的款項將會返還原本的信用卡或者是你付款的帳號')
            return redirect(url_for('confirm_payment'))
        return render_template('payment.html')
    return redirect(url_for('login'))

@app.route('/confirm_payment', methods=['GET', 'POST'])
def confirm_payment():
    if 'username' in session and 'cart' in session and 'addresses' in session and 'payment_method' in session:
        if request.method == 'POST':
            # 模擬生成訂單ID和保存訂單
            order_id = str(random.randint(100000, 999999))
            orders[order_id] = {
                'username': session['username'],
                'cart': session['cart'],
                'address': session['addresses'],
                'payment_method': session['payment_method'],
                'status': 'paid',
                'total_amount': calculate_total_amount(session['cart']),
                'order_date': datetime.datetime.now(),  # 保存訂單日期
                'received_date': None  # 初始狀態為未收到貨物
            }
            session['order_id'] = order_id
            flash('付款成功！')
            return redirect(url_for('order_confirmation'))
        return render_template('confirm_payment.html')
    return redirect(url_for('login'))

@app.route('/order_confirmation')
def order_confirmation():
    if 'username' in session and 'order_id' in session:
        order = orders.get(session['order_id'])
        return render_template('order_confirmation.html', order=order)
    return redirect(url_for('home'))

@app.route('/mark_received', methods=['POST'])
def mark_received():
    if 'username' in session and 'order_id' in session:
        order_id = session['order_id']
        order = orders.get(order_id)
        if order:
            order['received_date'] = datetime.datetime.now()
            flash('已標記為已收到貨物。')
            return redirect(url_for('order_confirmation'))
    return redirect(url_for('login'))

@app.route('/refund', methods=['GET', 'POST'])
def refund():
    if 'username' in session and 'order_id' in session:
        order_id = session['order_id']
        order = orders.get(order_id)
        if request.method == 'POST' and order:
            total_amount = order['total_amount']
            transaction_fee = total_amount * TRANSACTION_FEE_PERCENTAGE
            refund_amount = total_amount - transaction_fee
            order['status'] = 'refunded'
            order['refund_amount'] = refund_amount
            flash(f'退款申請成功，扣除手續費後的退款金額為 {refund_amount} 元，款項將返還至您的付款帳號。')
            return redirect(url_for('home'))
        return render_template('refund.html', order=order, transaction_fee=TRANSACTION_FEE_PERCENTAGE)
    return redirect(url_for('login'))

@app.route('/return', methods=['GET', 'POST'])
def return_order():
    if 'username' in session and 'order_id' in session:
        order_id = session['order_id']
        order = orders.get(order_id)
        if request.method == 'POST' and order:
            current_date = datetime.datetime.now()
            if order['received_date'] and (current_date - order['received_date']).days <= 7:
                total_amount = order['total_amount']
                transaction_fee = total_amount * TRANSACTION_FEE_PERCENTAGE
                refund_amount = total_amount - transaction_fee
                order['status'] = 'returned'
                order['refund_amount'] = refund_amount
                flash(f'退貨申請成功，扣除手續費後的退款金額為 {refund_amount} 元，款項將返還至您的付款帳號。')
            else:
                flash('退貨申請失敗，超過了退貨期限（7天）。')
            return redirect(url_for('home'))
        return render_template('return_order.html', order=order, transaction_fee=TRANSACTION_FEE_PERCENTAGE)
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download/<filename>')
def download(filename):
    if 'username' in session:
        return send_from_directory('static/music', filename)
    return redirect(url_for('login'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)

