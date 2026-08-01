# دليل إنشاء Windows Installer لنظام Thamarat ERP

## 🛠️ الأدوات المطلوبة

### 1. Inno Setup (مجاني)
- **التحميل:** https://jrsoftware.org/isdl.php
- **الإصدار:** 6.2.2 أو أحدث
- **الحجم:** ~3 MB

### 2. Python للتوزيع (اختياري)
- **PyInstaller:** لتحويل Python إلى exe
- **التحميل:** `pip install pyinstaller`

---

## 📥 الخطوة 1: تحميل وتثبيت Inno Setup

### 1.1 تحميل Inno Setup
```
1. افتح المتصفح
2. اذهب إلى: https://jrsoftware.org/isdl.php
3. اضغط على "Download"
4. اختر الملف: isetup-6.2.2.exe
```

### 1.2 تثبيت Inno Setup
```
1. شغّل ملف التثبيت (.exe)
2. اضغط "Next"
3. اقرأ اتفاقية الترخيص واضغط "I Agree"
4. اختر مجلد التثبيت (افتراضي: C:\Program Files (x86)\Inno Setup 6)
5. اضغط "Next" ثم "Install"
6. اضغط "Finish"
```

---

## 🔧 الخطوة 2: تجهيز ملفات التطبيق

### 2.1 هيكل الملفات المطلوب
```
thamarat-desktop-release/
├── backend/
│   ├── main.exe              # Python compiled
│   ├── models/
│   ├── routes/
│   └── utils/
├── frontend/
│   └── build/
│       ├── index.html
│       ├── static/
│       └── assets/
├── electron/
│   ├── Thamarat ERP.exe
│   └── resources/
└── data/
    └── (سيتم إنشاؤه تلقائياً)
```

### 2.2 تحويل Backend Python إلى EXE
```bash
# 1. تثبيت PyInstaller
pip install pyinstaller

# 2. الانتقال لمجلد backend
cd thamarat-desktop/backend

# 3. إنشاء EXE
pyinstaller --onefile --windowed --name "ThamaratBackend" main.py

# 4. الملف التنفيذي سيكون في:
#    dist/ThamaratBackend.exe
```

### 2.3 بناء React Frontend
```bash
# 1. الانتقال لمجلد frontend
cd thamarat-desktop/frontend

# 2. تثبيت الاعتماديات
npm install

# 3. بناء الإنتاج
npm run build

# 4. الملفات ستكون في:
#    build/
```

---

## 📝 الخطوة 3: إنشاء ملف Inno Setup Script

### 3.1 إنشاء ملف .iss جديد
```
1. افتح Inno Setup Compiler
2. اضغط "File" → "New"
3. سيظهر معالج إنشاء Setup
```

### 3.2 ملف Script الكامل (thamarat.iss)
```iss
; Thamarat ERP Windows Installer Script
; ================================

#define MyAppName "Thamarat ERP"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NexaGuard_Ye AI Solutions"
#define MyAppURL "https://nexaguard-ye.com"
#define MyAppExeName "Thamarat ERP.exe"
#define MyAppCopyright "Copyright (c) 2026 NexaGuard_Ye AI Solutions"

[Setup]
; معلومات التطبيق
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; مجلدات التثبيت
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; ملفات التثبيت
LicenseFile=..\LICENSE.txt
OutputDir=.\Output
OutputBaseFilename=Thamarat-Setup-{#MyAppVersion}
SetupIconFile=..\electron\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; الضغط والتحسين
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; واجهة المستخدم
WizardStyle=modern
WizardSizePercent=100
SetupLogging=yes

; المتطلبات
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; أبعاد النافذة
WindowWidth=800
WindowHeight=600

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "إنشاء اختصار على سطح المكتب"; GroupDescription: "اختصارات:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "إنشاء اختصار في شريط التشغيل السريع"; GroupDescription: "اختصارات:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Backend files
Source: "..\backend\dist\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\frontend\build\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs

; Electron files  
Source: "..\electron\Thamarat ERP.exe"; DestDir: "{app}"; Flags: ignoreversion

; Runtime files
Source: "..\runtime\*"; DestDir: "{app}\runtime"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\runtime'))

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\وثائق النظام"; Filename: "{app}\README.html"
Name: "{group}\إلغاء التثبيت"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; WorkingDir: "{app}"

[Run]
; تشغيل بعد التثبيت
Filename: "{app}\{#MyAppExeName}"; Description: "تشغيل {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Registry]
; بدء تلقائي (اختياري)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ThamaratERP"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks:

[Code]
// ==================== Pascal Script ====================

var
  DownloadPage: TOutputMsgWizardPage;

function DirExists(DirName: String): Boolean;
begin
  Result := DirExists(DirName);
end;

procedure InitializeWizard();
begin
  // صفحة ترحيبية مخصصة
  WizardForm.WelcomeLabel1.Caption := 'مرحباً بك في تثبيت Thamarat ERP';
  WizardForm.WelcomeLabel2.Caption := 
    'هذا المعالج سيرشدك خطوة بخطوة لتثبيت نظام محاسبة المنظمات الإنسانية.' + #13#10 + #13#10 +
    'متطلبات النظام:' + #13#10 +
    '- Windows 10 أو أحدث' + #13#10 +
    '- 4 GB RAM (8 GB مستحسن)' + #13#10 +
    '- 2 GB مساحة فارغة على القرص';
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // إنشاء مجلد البيانات
    ForceDirectories(ExpandConstant('{userappdata}\Thamarat'));
    
    // إنشاء مجلد النسخ الاحتياطي
    ForceDirectories(ExpandConstant('{userappdata}\Thamarat\backups'));
  end;
  
  if CurStep = ssPostUninstall then
  begin
    // سؤال عن حذف البيانات
    if MsgBox('هل تريد حذف جميع بيانات النظام؟', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{userappdata}\Thamarat'), True, True, True);
    end;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
```

---

## 🔨 الخطوة 4: التحويل من Python إلى EXE

### 4.1 تثبيت PyInstaller
```bash
pip install pyinstaller
```

### 4.2 تحويل Backend
```bash
cd thamarat-desktop/backend

# الطريقة 1: ملف واحد
pyinstaller --onefile --windowed --name "ThamaratBackend" main.py

# الطريقة 2: معبيانات
pyinstaller --onefile --windowed --name "ThamaratBackend" --add-data "models;models" --add-data "routes;routes" --add-data "utils;utils" main.py
```

### 4.3 ملفات إضافية مطلوبة
```
# تأكد من نسخ هذه الملفات مع EXE:
- requirements.txt (للمرجع)
- .env.example (للمستخدم)
```

---

## 🎨 الخطوة 5: إضافة أيقونة مخصصة

### 5.1 إنشاء أيقونة
```
1. افتح موقع: https://www.favicon.cc/
2. صمم أيقونة 256x256
3. حملها بصيغة .ico
4. ضعها في: electron/icon.ico
```

### 5.2 تحويل PNG إلى ICO
```
1. افتح: https://icoconvert.com/
2. ارفع صورة PNG
3. اختر الحجم: 256x256, 48x48, 32x32, 16x16
4. اضغط Convert
5. حمل ملف .ico
```

---

## 🚀 الخطوة 6: بناء ملف التثبيت

### 6.1 فتح Script في Inno Setup
```
1. افتح Inno Setup Compiler
2. اضغط File → Open
3. اذهب إلى: thamarat-desktop/installer/thamarat.iss
4. اضغط Open
```

### 6.2 الترجمة (Compile)
```
1. من القائمة: Project → Compile
2. أو اضغط F9
3. انتظر حتى يظهر:
   "Successful"
4. ملف التثبيت سيكون في:
   installer/Output/Thamarat-Setup-1.0.0.exe
```

### 6.3 التحقق من الملف
```
1. اذهب إلى: installer/Output/
2. تأكد من وجود: Thamarat-Setup-1.0.0.exe
3. حجم الملف يجب أن يكون بين 50-200 MB تقريباً
```

---

## ✅ الخطوة 7: اختبار التثبيت

### 7.1 التثبيت على جهاز الاختبار
```
1. انسخ ملف Thamarat-Setup-1.0.0.exe لجهاز Windows
2. شغّل الملف (Double Click)
3. اتبع خطوات التثبيت
4. تأكد من:
   ✓ ظهور أيقونة على سطح المكتب
   ✓ ظهور البرنامج في Start Menu
   ✓ تشغيل البرنامج بنجاح
```

### 7.2 التحقق من عمل البرنامج
```
1. شغّل Thamarat ERP
2. تأكد من:
   ✓ فتح المتصفح الداخلي
   ✓ تشغيل Backend
   ✓ ظهور واجهة تسجيل الدخول
```

---

## 📦 الخطوة 8: التوزيع

### 8.1 طرق التوزيع
```
الطريقة 1: ملف مضغوط
- ضغط: Thamarat-Setup-1.0.0.exe
- رفع على Google Drive / OneDrive
- إرسال رابط التحميل للعميل

الطريقة 2: USB
- نسخ الملف على USB
- تسليم للعميل

الطريقة 3: رابط تحميل مباشر
- رفع على موقع الشركة
- إرسال الرابط للعميل
```

### 8.2 معلومات ما بعد البيع
```
- رقم الإصدار: 1.0.0
- حجم التثبيت: ~150 MB
- متطلبات إضافية: لا
- يحتاج صلاحيات: User (عادي)
```

---

## 🔧 حل المشاكل الشائعة

### المشكلة 1: خطأ في Script
```
الحل:
1. تأكد من صحة مسار الملفات
2. تأكد من وجود الملف: License.txt
3. تأكد من وجود أيقونة: icon.ico
```

### المشكلة 2: Antivirus يحذف الملف
```
الحل:
1. أضف ملف التثبيت للاستثناء
2. أو أرسل للعميل مع تعليمات:
   "قد يطلب Antivirus إذن التشغيل"
```

### المشكلة 3: Python EXE لا يعمل
```
الحل:
1. تأكد من تثبيت Visual C++ Redistributable
2. حمل من: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## 📞 للدعم الفني

- **Email:** support@nexaguard-ye.com
- **WhatsApp:** متاح قريباً
- **الموقع:** https://nexaguard-ye.com

---

## 📋 ملخص الخطوات

| الخطوة | الوصف | الوقت |
|--------|-------|-------|
| 1 | تحميل Inno Setup | 2 دقيقة |
| 2 | تجهيز ملفات التطبيق | 10 دقائق |
| 3 | تحويل Python لـ EXE | 5 دقائق |
| 4 | إنشاء Script | 5 دقائق |
| 5 | بناء التثبيت | 3 دقائق |
| 6 | الاختبار | 5 دقائق |

**الإجمالي: ~30 دقيقة**
