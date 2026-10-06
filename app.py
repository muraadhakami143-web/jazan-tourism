from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)

# استخدام مجلد مؤقت أو مسار صالح لـ SQLite على منصة Render
DB_PATH = 'database.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                slots_booked INTEGER NOT NULL,
                total_price REAL NOT NULL,
                payment_status TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

init_db()

@app.route('/')
def index():
    html_content = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة سياحة جازان - حجز الرحلات</title>
    <style>
        body {
            font-family: 'Cairo', Tahoma, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .logo-container {
            margin-bottom: 20px;
            text-align: center;
        }
        .logo-container img {
            max-width: 120px;
            height: auto;
            border-radius: 50%;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .booking-card {
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            width: 100%;
            max-width: 500px;
        }
        h2 {
            text-align: center;
            color: #0077b6;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        select, input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 16px;
        }
        button {
            background-color: #2b9348;
            color: white;
            border: none;
            padding: 12px;
            width: 100%;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #1f6f35;
        }
        #message {
            margin-top: 15px;
            text-align: center;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="logo-container">
        <img src="/logo.jpg" alt="شعار سياحة جازان">
    </div>

    <div class="booking-card">
        <h2>حجز رحلة سياحية في جازان 🌴</h2>
        <form id="bookingForm">
            <div class="form-group">
                <label>اختر الرحلة:</label>
                <select id="trip_id" required>
                    <option value="" disabled selected>-- اختر الرحلة السياحية --</option>
                    <option value="trip_1">الرحلة الأولى (300 ريال)</option>
                    <option value="trip_2">الرحلة الثانية (500 ريال)</option>
                </select>
            </div>

            <div class="form-group">
                <label>اسم العميل:</label>
                <input type="text" id="customer_name" required placeholder="أدخل اسمك الكامل">
            </div>

            <div class="form-group">
                <label>رقم الجوال:</label>
                <input type="tel" id="customer_phone" required placeholder="05xxxxxxxx">
            </div>

            <div class="form-group">
                <label>عدد الأشخاص:</label>
                <input type="number" id="slots_booked" min="1" value="1" required>
            </div>

            <div class="form-group">
                <label>الإجمالي (ريال):</label>
                <input type="text" id="total_price" readonly value="300">
            </div>

            <button type="submit">تأكيد الحجز</button>
            <div id="message"></div>
        </form>
    </div>

    <script>
        const tripSelect = document.getElementById('trip_id');
        const slotsInput = document.getElementById('slots_booked');
        const totalPriceInput = document.getElementById('total_price');

        function updatePrice() {
            let pricePerPerson = 300;
            if (tripSelect.value === 'trip_2') {
                pricePerPerson = 500;
            } else if (tripSelect.value === 'trip_1') {
                pricePerPerson = 300;
            }
            let slots = parseInt(slotsInput.value) || 1;
            totalPriceInput.value = pricePerPerson * slots;
        }

        tripSelect.addEventListener('change', updatePrice);
        slotsInput.addEventListener('input', updatePrice);

        document.getElementById('bookingForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const messageDiv = document.getElementById('message');
            messageDiv.style.color = '#555';
            messageDiv.textContent = 'جاري تسجيل الحجز...';

            const data = {
                trip_id: tripSelect.value,
                customer_name: document.getElementById('customer_name').value,
                customer_phone: document.getElementById('customer_phone').value,
                slots_booked: parseInt(slotsInput.value),
                total_price: parseFloat(totalPriceInput.value)
            };

            try {
                const response = await fetch('/book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (response.ok) {
                    messageDiv.style.color = 'green';
                    messageDiv.textContent = result.message || 'تم الحجز بنجاح!';
                    document.getElementById('bookingForm').reset();
                    totalPriceInput.value = 300;
                } else {
                    messageDiv.style.color = 'red';
                    messageDiv.textContent = result.error || 'حدث خطأ أثناء الحجز، حاول مرة أخرى.';
                }
            } catch (error) {
                messageDiv.style.color = 'red';
                messageDiv.textContent = 'حدث خطأ في الاتصال بالخادم.';
            }
        });
    </script>
</body>
</html>'''
    return render_template_string(html_content)

@app.route('/book', methods=['POST'])
def book():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'بيانات غير صالحة'}), 400
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (trip_id, customer_name, customer_phone, slots_booked, total_price, payment_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('trip_id'),
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('slots_booked'),
            data.get('total_price'),
            'Pending'
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'تم حجز الرحلة بنجاح! ننتظر زيارتك لجازان 🌴'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
