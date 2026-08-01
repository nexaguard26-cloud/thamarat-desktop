# Thamarat ERP - نظام محاسبة المنظمات الإنسانية

<div align="center">

![Thamarat ERP Logo](https://via.placeholder.com/200x80/1890ff/ffffff?text=ثمرة+ERP)

**نظام محاسبة متكامل للمنظمات الإنسانية المحلية**

مناسب للأجهزة متوسطة المواصفات | Core i5 | RAM 8GB

</div>

---

## 📋 مميزات النظام

### 🎯 للمحاسبين
- شجرة حسابات متوافقة مع IPSAS
- قيود محاسبية مزدوجة (Debit/Credit)
- ميزان المراجعة
- القوائم المالية (الميزانية العمومية، قائمة الدخل)

### 💰 للمنظمات
- إدارة الصناديق (مقيدة وغير مقيدة)
- تتبع المانحين والتمويل
- إدارة الميزانيات السنوية
- تقارير استخدام الصناديق

### 🔐 للأمناء
- نظام صلاحيات متقدم
- سجل تدقيق غير قابل للتلاعب
- نسخ احتياطي تلقائي

### 💻 متوافق مع
- Windows 10/11
- Linux (Ubuntu, Debian)
- macOS

---

## 🚀 التثبيت السريع

### الطريقة 1: Windows Installer
```bash
# تحميل ملف التثبيت
Thamarat-Setup-1.0.0.exe

# تشغيل التثبيت
# سيقوم بتثبيت Python و Node.js تلقائياً
```

### الطريقة 2: Docker
```bash
docker-compose up -d
```

### الطريقة 3: التثبيت اليدوي
```bash
# 1. استنساخ المستودع
git clone https://github.com/nexaguard26-cloud/thamarat.git
cd thamarat-desktop

# 2. تشغيل Backend
cd backend
pip install -r requirements.txt
python main.py

# 3. تشغيل Frontend
cd frontend
npm install
npm start
```

---

## 📊 المتطلبات التقنية

| المكون | الحد الأدنى | الموصى به |
|--------|-----------|----------|
| المعالج | Core i3 | Core i5+ |
| الذاكرة | 4 GB | 8 GB |
| القرص | 2 GB | 10 GB |
| النظام | Windows 10 | Windows 11 |

---

## 🔑 بيانات الدخول الافتراضية

| الدور | البريد الإلكتروني | كلمة المرور |
|-------|------------------|-------------|
| Admin | admin@thamarat.local | Admin@123 |

---

## 📂 هيكل المشروع

```
thamarat-desktop/
├── backend/              # Python FastAPI Backend
│   ├── models/          # نماذج قاعدة البيانات
│   ├── routes/          # نقاط نهاية API
│   ├── utils/           # أدوات مساعدة
│   └── main.py          # نقطة البداية
├── frontend/            # React Frontend
│   ├── src/
│   │   ├── components/  # مكونات React
│   │   ├── pages/       # صفحات التطبيق
│   │   └── services/    # خدمات API
│   └── public/          # ملفات عامة
├── electron/            # Electron Desktop
│   ├── main.js          # العملية الرئيسية
│   └── preload.js       # Preload script
└── installer/           # ملفات التثبيت
```

---

## 🔒 الأمان

- ✅ تشفير كلمات المرور (bcrypt)
- ✅ JWT Authentication
- ✅ سجل تدقيق بـ SHA-256 Checksum
- ✅ HTTPS في الاتصال المحلي

---

## 📞 الدعم الفني

- 📧 Email: support@nexaguard-ye.com
- 🌐 Website: https://nexaguard-ye.com
- 📱 WhatsApp: متاح قريباً

---

## 📄 الترخيص

هذا المنتج مرخص للاستخدام التجاري.
للحصول على ترخيص دائم، يرجى التواصل مع فريق المبيعات.

---

## 🚀 خطوات التشغيل (من الحزمة المباشرة)

### الخطوة 1: تشغيل النظام
```
انقر مرتين على: تشغيل النظام.bat
```

هذا سيقوم بـ:
1. ✅ تشغيل خادم Backend
2. ✅ فتح واجهة المستخدم في المتصفح

### الخطوة 2: تسجيل الدخول
```
البريد: admin@thamarat.local
كلمة المرور: Admin@123
```

---

## 📁 محتويات الحزمة

| الملف | الوصف |
|-------|-------|
| `ThamaratBackend.exe` | خادم النظام (Backend) |
| `ThamaratBackend.bat` | تشغيل الخادم يدوياً |
| `تشغيل النظام.bat` | تشغيل سريع (خادم + واجهة) |
| `frontend/index.html` | واجهة المستخدم |

---

## ❓ حل المشاكل

| المشكلة | الحل |
|---------|------|
| الخادم لا يبدأ | تأكد من عدم استخدام منفذ 5000 |
| لا يمكن فتح الملف | استخدم متصفح حديث (Chrome, Firefox) |
| خطأ في تسجيل الدخول | تأكد من تشغيل ThamaratBackend.exe أولاً |

---

<div align="center">

**© 2026 NexaGuard_Ye AI Solutions**

*جميع الحقوق محفوظة*

</div>
