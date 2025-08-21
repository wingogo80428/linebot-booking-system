from database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# 新增測試員工
cursor.execute('''
    INSERT INTO employees (employee_id, name, department_id, shift_type, preferred_language)
    VALUES ('IGA1-02849', '測試員工', 1, 'day', 'zh'),
    ('IGA1-01657', '測試員工2', 1, 'day', 'zh'),
    ('IGA1-02851', '測試員工3', 1, 'day', 'zh'),
    ('IGA1-02852', '測試員工4', 1, 'day', 'zh'),
    ('IGA1-02853', '測試員工5', 1, 'day', 'zh'),
    ('IGA1-02854', '測試員工6', 1, 'day', 'zh'),
    ('IGA1-02855', '測試員工7', 1, 'day', 'zh'),
    ('IGA1-02856', '測試員工8', 1, 'day', 'zh'),
''')

conn.commit()
conn.close()
print("✅ 測試員工新增完成！")