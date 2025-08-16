from database import DatabaseManager

def fix_time_limits():
    print("🕐 正在關閉雲端資料庫的時間限制...")
    
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 將所有時間限制設為 23:59
    cursor.execute('''
        UPDATE system_settings 
        SET setting_value = '23:59' 
        WHERE setting_key IN (
            'bus_day_deadline', 
            'bus_night_deadline', 
            'meal_day_deadline', 
            'meal_night_deadline'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 雲端時間限制已關閉！")

if __name__ == "__main__":
    fix_time_limits()