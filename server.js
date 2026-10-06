const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// استخدام الـ Body Parser لقراءة بيانات الـ JSON
app.use(bodyParser.json());
app.use(express.json());

// تقديم ملفات الواجهة الأمامية (مثل index.html) مباشرة من مجلد المشروع
app.use(express.static(__dirname));

// إعداد الاتصال بقاعدة البيانات (MySQL)
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '', // اتركها فارغة إذا لم تضع كلمة مرور لـ root
    database: 'jazan_tourism'
});

db.connect((err) => {
    if (err) {
        console.error('خطأ في الاتصال بقاعدة البيانات:', err);
        return;
    }
    console.log('تم الاتصال بقاعدة البيانات بنجاح! 🚀');
});

// مسار استقبال الحجوزات وإرسال رد بالنجاح
app.post('/api/book', (req, res) => {
    const { trip_id, customer_name, customer_phone, slots_booked, total_price, payment_status } = req.body;

    const query = 'INSERT INTO bookings (trip_id, customer_name, customer_phone, slots_booked, total_price, payment_status) VALUES (?, ?, ?, ?, ?, ?)';
    
    db.query(query, [trip_id, customer_name, customer_phone, slots_booked, total_price, payment_status], (err, result) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ success: false, message: 'فشل حفظ الحجز في قاعدة البيانات' });
        }
        
        // رسالة عند الطلب تظهر للعميل والسيرفر
        console.log(`تم تسجيل حجز جديد بنجاح باسم: ${customer_name}`);
        res.status(200).json({ 
            success: true, 
            message: 'تم الحجز بنجاح!', 
            booking_id: result.insertId 
        });
    });
});

// تشغيل السيرفر
app.listen(PORT, () => {
    console.log(`السيرفر شغال بكفاءة وجاهز لتحصيل الأرباح! 🚀 على البورت ${PORT}`);
});