from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
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

@app.route('/')
def index():
    html_content = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة سياحة جازان - حجز الرحلات السياحية</title>
    <meta name="description" content="احجز رحلتك السياحية القادمة في جزر وجبال جازان بكل سهولة ويسر. استكشف أجمل الوجهات السياحية وسجل حجوزاتك الفورية معنا.">
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
        .booking-card {
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            width: 100%;
            max-width: 450px;
        }
        h2 {
            text-align: center;
            color: #0077b6;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 14px;
            background-color: #fff;
        }
        button {
            width: 100%;
            background-color: #28a745;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #218838;
        }
        #message {
            text-align: center;
            margin-top: 15px;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="booking-card">
        <h2>حجز رحلة سياحية في جازان 🌴</h2>
        
        <form id="bookingForm">
            <div class="form-group">
                <label for="trip_id">اختر الرحلة:</label>
                <select id="trip_id" required onchange="updateTotal()">
                    <option value="" disabled selected>-- اختر الرحلة السياحية --</option>
                    <option value="1" data-price="300">الرحلة الأولى - جزر فرسان (300 ريال)</option>
                    <option value="2" data-price="400">الرحلة الثانية - جبال فيفا (400 ريال)</option>
                    <option value="3" data-price="500">الرحلة الثالثة - وادي لجب (500 ريال)</option>
                    <option value="4" data-price="600">الرحلة الرابعة - الكورنيش الجنوبي (600 ريال)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>اسم العميل:</label>
                <input type="text" id="customer_name" required>
            </div>
            
            <div class="form-group">
                <label>رقم الجوال:</label>
                <input type="text" id="customer_phone" required>
            </div>
            
            <div class="form-group">
                <label>عدد الأشخاص:</label>
                <input type="number" id="slots_booked" value="1" min="1" required oninput="updateTotal()">
            </div>
            
            <div class="form-group">
                <label>الإجمالي (ريال):</label>
                <input type="number" id="total_price" readonly required>
            </div>

            <button type="submit">تأكيد الحجز</button>
        </form>
        
        <p id="message"></p>
    </div>

    <script>
        function updateTotal() {
            const tripSelect = document.getElementById('trip_id');
            const selectedOption = tripSelect.options[tripSelect.selectedIndex];
            const pricePerTicket = parseFloat(selectedOption.getAttribute('data-price')) || 0;
            
            const slotsInput = document.getElementById('slots_booked');
            const slots = parseInt(slotsInput.value) || 1;
            
            const total = pricePerTicket * slots;
            document.getElementById('total_price').value = total;
        }

        document.getElementById('bookingForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const data = {
                trip_id: document.getElementById('trip_id').value,
                customer_name: document.getElementById('customer_name').value,
                customer_phone: document.getElementById('customer_phone').value,
                slots_booked: document.getElementById('slots_booked').value,
                total_price: document.getElementById('total_price').value,
                payment_status: 'Paid'
            };

            try {
                const response = await fetch('/api/book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                const msgElement = document.getElementById('message');
                
                if (result.success) {
                    msgElement.style.color = 'green';
                    msgElement.textContent = `تم الحجز بنجاح! رقم الحجز: ${result.booking_id}`;
                } else {
                    msgElement.style.color = 'red';
                    msgElement.textContent = 'حدث خطأ أثناء الحجز، حاول مرة أخرى.';
                }
            } catch (err) {
                console.error(err);
                document.getElementById('message').style.color = 'red';
                document.getElementById('message').textContent = 'تعذر الاتصال بالسيرفر.';
            }
        });
    </script>
</body>
</html>'''
    return render_template_string(html_content)

@app.route('/api/book', methods=['POST'])
def book():
    data = request.json
    try:
        conn = sqlite3.connect('database.db')
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
            data.get('payment_status', 'Paid')
        ))
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'booking_id': booking_id})
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
