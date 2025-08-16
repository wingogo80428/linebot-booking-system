from database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# 暫時停用時間限制
cursor.execute('''
    UPDATE system_settings 
    SET setting_value = '23:59' 
    WHERE setting_key IN ('bus_day_deadline', 'bus_night_deadline', 'meal_day_deadline', 'meal_night_deadline')
''')

conn.commit()
conn.close()
print("✅ 時間限制已暫時關閉，可以隨時測試！")