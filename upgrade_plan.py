# فایل: upgrade_plan.py

# 🧱 پوشه‌های پیشنهادی برای گسترش پروژه
folders = [
    "outputs/lst/",              # خروجی دمای سطح
    "outputs/sar/",              # خروجی Sentinel-1
    "outputs/ml/",               # خروجی مدل‌های یادگیری
    "outputs/kmz/advanced/",     # KMZ پیشرفته
    "data/lst/",                 # داده‌های خام Landsat
    "data/sar/",                 # داده‌های خام SAR
    "models/",                   # مدل‌های AI ذخیره شده
    "reports/pdf/",              # خروجی گزارش‌ها
    "batch/",                    # CSVهای دسته‌ای
]

# 📄 فایل‌های پیشنهادی (کد اصلی)
files = [
    "lst_analyze.py",            # تحلیل دمای سطح با Landsat
    "sar_analyze.py",            # تحلیل داده‌های SAR (راداری)
    "void_classifier.py",        # مدل هوش مصنوعی برای پیش‌بینی فضای خالی
    "generate_report.py",        # ساخت گزارش PDF خودکار
    "batch_process.py",          # پردازش گروهی نقاط
    "export_advanced_kmz.py",    # ساخت فایل KMZ با جزئیات پیشرفته
]

# 🧠 یادآوری: فایل‌های موجود تغییری نمی‌کنند، این‌ها فایل‌های مستقل هستند.

# 📌 توضیح کوتاه برای هر فایل جدید
explanations = {
    "lst_analyze.py": "تحلیل دمای سطح از طریق باند 10 Landsat و استخراج شاخص حرارتی LST.",
    "sar_analyze.py": "دریافت داده VV/VH از Sentinel-1 و تحلیل ساختار زیرزمینی یا بافت خاک.",
    "void_classifier.py": "استفاده از مدل یادگیری ماشین (مثل UNet) برای تشخیص الگوهای فضای خالی.",
    "generate_report.py": "خروجی PDF شامل نقشه، شاخص‌ها، تحلیل هوشمند برای هر نقطه.",
    "batch_process.py": "آپلود و اجرای خودکار چند مختصات از فایل CSV.",
    "export_advanced_kmz.py": "خروجی Google Earth با رنگ‌بندی، آیکون و لایه‌بندی.",
}

# ✅ اجرای اولیه برای ساخت پوشه‌ها (توصیه شده یک‌بار اجرا شود)
if __name__ == "__main__":
    import os
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("📁 همه پوشه‌های جدید ساخته شد.")

    print("\n📄 فایل‌های مورد نیاز برای ایجاد:")
    for file in files:
        print(f"- {file}: {explanations[file]}")