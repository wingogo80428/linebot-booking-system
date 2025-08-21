from database import DatabaseManager

# 新增員工 IGA1-01657
def add_new_employee():
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # 新增員工資料
        cursor.execute('''
            INSERT INTO employees (employee_id, name, department_id, shift_type, preferred_language)
            VALUES (?, ?, ?, ?, ?)
        ''', ('IGA1-01657', '測試員工01657', 1, 'day', 'zh'))
        
        conn.commit()
        print("✅ 員工新增成功！")
        print("👤 員工編號：IGA1-01657")
        print("📛 姓名：測試員工01657") 
        print("🏢 部門：IT部門")
        print("⏰ 班別：日班")
        print("🌐 語言：中文")
        
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print("⚠️  員工編號 IGA1-01657 已存在！")
        else:
            print(f"❌ 新增失敗：{e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_new_employee()