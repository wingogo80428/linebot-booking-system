from database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# 新增測試員工
cursor.execute('''
    INSERT INTO employees (employee_id, name, department_id, shift_type, preferred_language)
    VALUES ('IGA1-02849', '測試員工', 1, 'day', 'zh')
''')

conn.commit()
conn.close()
print("✅ 測試員工新增完成！")