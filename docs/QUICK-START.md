# 🚀 دليل التشغيل السريع

## لسطح المكتب (Windows)

### الخطوة 1: تثبيت Python
```bash
# تحميل Python 3.11+ من:
https://www.python.org/downloads/

# أثناء التثبيت، تأكد من اختيار:
# ☑ Add Python to PATH
```

### الخطوة 2: تشغيل Backend
```bash
# افتح Terminal جديد
cd thamarat-desktop/backend

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل
python main.py

# ستظهر رسالة:
# Uvicorn running on http://127.0.0.1:5000
```

### الخطوة 3: تشغيل Frontend
```bash
# افتح Terminal جديد
cd thamarat-desktop/frontend

# تثبيت المتطلبات
npm install

# تشغيل
npm start

# سيفتح المتصفح تلقائياً على:
# http://localhost:3000
```

---

## 🐳 باستخدام Docker

### المتطلبات
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### التشغيل
```bash
cd thamarat-desktop

# تشغيل
docker-compose up -d

# التحقق
docker-compose ps

# الوصول:
# - Frontend: http://localhost:3000
# - Backend:  http://localhost:5000
```

---

## 📱 للاختبار

### بيانات الدخول
```
البريد: admin@thamarat.local
كلمة المرور: Admin@123
```

---

## 🔧 حل المشاكل

### خطأ: pip not found
```bash
# الحل: أعد تثبيت Python مع إضافة PATH
```

### خطأ: Port 5000 already in use
```bash
# الحل: أوقف أي برنامج يستخدم المنفذ
netstat -ano | findstr :5000
taskkill /PID <number> /F
```

### خطأ: npm ERR!
```bash
# الحل: مسح cache وإعادة التثبيت
npm cache clean --force
rm -rf node_modules
npm install
```

---

## 📞 للدعم

- Email: support@nexaguard-ye.com
