# دپارتمان املاک اندیشه - HomeProject

## نصب و راه‌اندازی
1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py createsuperuser`
4. `python manage.py runserver`

## نقش‌ها
- **superadmin**: مدیریت کل (پنل ادمین + پنل مدیریت سایت)
- **admin**: مدیریت سایت (لایسنس‌ها، آژانس‌ها)
- **agency**: آژانس املاک (داشبورد، ثبت آگهی)
- **user**: کاربر عادی (مشاهده)

## ویژگی‌ها
- ثبت آگهی با عکس و ویدیو (چندتایی)
- مدیریت لایسنس آژانس‌ها
- بخش‌های: خرید/فروش، رهن/اجاره، تهاتر، کاسبی، باغ، ساخت و ساز
- فرم وام بانکی
- صفحات پشتیبان

# دپارتمان املاک اندیشه - HomeProject

## 📋 توضیح
سامانه مدیریت املاک با سه پنل کاربری (سوپرادمین، مدیر سایت، آژانس).

## 🚀 نصب و راه‌اندازی

```bash
# 1. فعال‌سازی محیط مجازی
.venv\Scripts\activate

# 2. نصب وابستگی‌ها
pip install -r requirements.txt

# 3. مایگریت
python manage.py migrate

# 4. ساخت سوپر یوزر
python manage.py createsuperuser

# 5. اجرای سرور
python manage.py runserver

