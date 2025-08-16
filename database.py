import sqlite3
import datetime
from typing import Optional, List, Dict

class DatabaseManager:
    def __init__(self, db_path='linebot_booking.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """取得資料庫連線"""
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    
    def init_database(self):
        """初始化資料庫，建立所有資料表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 部門資料表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dept_code VARCHAR(10) UNIQUE NOT NULL,
                    dept_name_zh VARCHAR(100) NOT NULL,
                    dept_name_en VARCHAR(100) NOT NULL,
                    dept_name_vi VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. 員工資料表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id VARCHAR(20) UNIQUE NOT NULL,  -- IGA1-02849 格式
                    name VARCHAR(100) NOT NULL,
                    department_id INTEGER,
                    shift_type VARCHAR(10) CHECK(shift_type IN ('day', 'night')) NOT NULL,
                    preferred_language VARCHAR(5) DEFAULT 'zh',  -- zh, en, vi
                    status VARCHAR(10) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                )
            ''')
            
            # 3. LINE使用者綁定表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS line_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    line_user_id VARCHAR(100) UNIQUE NOT NULL,
                    employee_id INTEGER,
                    is_bound BOOLEAN DEFAULT FALSE,
                    bound_at TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                )
            ''')
            
            # 4. 交通車路線表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bus_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_code VARCHAR(20) UNIQUE NOT NULL,
                    route_name_zh VARCHAR(100) NOT NULL,
                    route_name_en VARCHAR(100) NOT NULL,
                    route_name_vi VARCHAR(100) NOT NULL,
                    description_zh TEXT,
                    description_en TEXT,
                    description_vi TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # 5. 交通車班次表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bus_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id INTEGER NOT NULL,
                    shift_type VARCHAR(10) CHECK(shift_type IN ('day', 'night')) NOT NULL,
                    departure_time TIME NOT NULL,
                    schedule_name_zh VARCHAR(50),
                    schedule_name_en VARCHAR(50),
                    schedule_name_vi VARCHAR(50),
                    seat_limit INTEGER DEFAULT 50,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (route_id) REFERENCES bus_routes(id)
                )
            ''')
            
            # 6. 交通車預約表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bus_reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    schedule_id INTEGER NOT NULL,
                    reservation_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',  -- active, cancelled
                    notes TEXT,
                    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id),
                    FOREIGN KEY (schedule_id) REFERENCES bus_schedules(id)
                )
            ''')
            
            # 7. 餐廳表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    floor VARCHAR(10) NOT NULL,
                    name_zh VARCHAR(100) NOT NULL,
                    name_en VARCHAR(100) NOT NULL,
                    name_vi VARCHAR(100) NOT NULL,
                    type VARCHAR(20) NOT NULL,  -- bento, noodle, light
                    has_daily_menu BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # 8. 每日菜單表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_menus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_id INTEGER NOT NULL,
                    menu_date DATE NOT NULL,
                    menu_items_zh TEXT,  -- JSON格式
                    menu_items_en TEXT,  -- JSON格式
                    menu_items_vi TEXT,  -- JSON格式
                    price DECIMAL(8,2),
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
                )
            ''')
            
            # 9. 訂餐記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meal_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    restaurant_id INTEGER NOT NULL,
                    order_date DATE NOT NULL,
                    menu_id INTEGER,
                    special_request TEXT,
                    price DECIMAL(8,2),
                    status VARCHAR(20) DEFAULT 'active',  -- active, cancelled
                    ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(id),
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                    FOREIGN KEY (menu_id) REFERENCES daily_menus(id)
                )
            ''')
            
            # 10. 系統設定表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    description VARCHAR(255),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("✅ 資料庫初始化完成")
            
        except Exception as e:
            print(f"❌ 資料庫初始化錯誤: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def insert_initial_data(self):
        """插入初始資料"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 插入部門資料
            departments = [
                ('IT', 'IT部門', 'IT Department', 'Phòng IT'),
                ('HR', '人資部', 'HR Department', 'Phòng Nhân sự'),
                ('PROD', '生產部', 'Production Department', 'Phòng Sản xuất'),
                ('QC', '品管部', 'Quality Control', 'Phòng Kiểm tra chất lượng'),
                ('ADMIN', '行政部', 'Administration', 'Phòng Hành chính')
            ]
            
            cursor.execute('SELECT COUNT(*) FROM departments')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO departments (dept_code, dept_name_zh, dept_name_en, dept_name_vi)
                    VALUES (?, ?, ?, ?)
                ''', departments)
                print("✅ 部門資料插入完成")
            
            # 插入交通車路線
            routes = [
                ('pingzhen', '平鎮線', 'Pingzhen Route', 'Tuyến Pingzhen', '平鎮地區接送', 'Pingzhen area shuttle', 'Xe đưa đón khu vực Pingzhen'),
                ('xinli', '新壢線', 'Xinli Route', 'Tuyến Xinli', '中壢宜得利、內壢家樂福 (停2站)', 'Zhongli NITORI, Neili Carrefour (2 stops)', 'Zhongli NITORI, Neili Carrefour (2 điểm dừng)'),
                ('xinkan', '新崁線', 'Xinkan Route', 'Tuyến Xinkan', '桃園火車站及桃園市區站點 (停4站)', 'Taoyuan Station and city stops (4 stops)', 'Ga Taoyuan và các điểm dừng thành phố (4 điểm dừng)')
            ]
            
            cursor.execute('SELECT COUNT(*) FROM bus_routes')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO bus_routes (route_code, route_name_zh, route_name_en, route_name_vi, description_zh, description_en, description_vi)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', routes)
                print("✅ 交通車路線資料插入完成")
            
            # 插入班次資料
            schedules = [
                # 日班班次
                (1, 'day', '17:45', '日班早下班', 'Day Early Off', 'Ca ngày tan sớm'),
                (1, 'day', '20:20', '日班晚下班', 'Day Late Off', 'Ca ngày tan muộn'),
                (2, 'day', '17:45', '日班早下班', 'Day Early Off', 'Ca ngày tan sớm'),
                (2, 'day', '20:20', '日班晚下班', 'Day Late Off', 'Ca ngày tan muộn'),
                (3, 'day', '17:45', '日班早下班', 'Day Early Off', 'Ca ngày tan sớm'),
                (3, 'day', '20:20', '日班晚下班', 'Day Late Off', 'Ca ngày tan muộn'),
                # 夜班班次
                (1, 'night', '05:45', '夜班早下班', 'Night Early Off', 'Ca đêm tan sớm'),
                (1, 'night', '08:20', '夜班晚下班', 'Night Late Off', 'Ca đêm tan muộn'),
                (2, 'night', '05:45', '夜班早下班', 'Night Early Off', 'Ca đêm tan sớm'),
                (2, 'night', '08:20', '夜班晚下班', 'Night Late Off', 'Ca đêm tan muộn'),
                (3, 'night', '05:45', '夜班早下班', 'Night Early Off', 'Ca đêm tan sớm'),
                (3, 'night', '08:20', '夜班晚下班', 'Night Late Off', 'Ca đêm tan muộn')
            ]
            
            cursor.execute('SELECT COUNT(*) FROM bus_schedules')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO bus_schedules (route_id, shift_type, departure_time, schedule_name_zh, schedule_name_en, schedule_name_vi)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', schedules)
                print("✅ 班次資料插入完成")
            
            # 插入餐廳資料
            restaurants = [
                ('1F', '1樓團膳', '1F Catering', 'Suất ăn tầng 1', 'bento', False),
                ('1F', '1樓麵食', '1F Noodles', 'Mì tầng 1', 'noodle', False),
                ('6F', '拉亞漢堡', 'Laya Burger', 'Burger Laya', 'light', True),
                ('7F', '7樓團膳', '7F Catering', 'Suất ăn tầng 7', 'bento', False),
                ('7F', '7樓麵食', '7F Noodles', 'Mì tầng 7', 'noodle', False)
            ]
            
            cursor.execute('SELECT COUNT(*) FROM restaurants')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO restaurants (floor, name_zh, name_en, name_vi, type, has_daily_menu)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', restaurants)
                print("✅ 餐廳資料插入完成")
            
            # 插入系統設定
            settings = [
                ('bus_day_deadline', '14:30', '日班交通車預約截止時間'),
                ('bus_night_deadline', '09:00', '夜班交通車預約截止時間'),
                ('meal_day_deadline', '09:00', '日班訂餐截止時間'),
                ('meal_night_deadline', '21:00', '夜班訂餐截止時間')
            ]
            
            cursor.execute('SELECT COUNT(*) FROM system_settings')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO system_settings (setting_key, setting_value, description)
                    VALUES (?, ?, ?)
                ''', settings)
                print("✅ 系統設定插入完成")
            
            conn.commit()
            print("🎉 所有初始資料插入完成！")
            
        except Exception as e:
            print(f"❌ 初始資料插入錯誤: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def bind_line_user(self, line_user_id: str, employee_id: str) -> Dict:
        """綁定LINE使用者與員工"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 檢查員工是否存在
            cursor.execute('SELECT id, name FROM employees WHERE employee_id = ?', (employee_id,))
            employee = cursor.fetchone()
            
            if not employee:
                return {'success': False, 'message': f'找不到員工編號：{employee_id}'}
            
            # 檢查是否已綁定
            cursor.execute('SELECT id FROM line_users WHERE line_user_id = ?', (line_user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新綁定
                cursor.execute('''
                    UPDATE line_users 
                    SET employee_id = ?, is_bound = TRUE, bound_at = CURRENT_TIMESTAMP
                    WHERE line_user_id = ?
                ''', (employee[0], line_user_id))
            else:
                # 新增綁定
                cursor.execute('''
                    INSERT INTO line_users (line_user_id, employee_id, is_bound, bound_at)
                    VALUES (?, ?, TRUE, CURRENT_TIMESTAMP)
                ''', (line_user_id, employee[0]))
            
            conn.commit()
            return {'success': True, 'message': f'成功綁定員工：{employee[1]}'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'綁定失敗：{str(e)}'}
        finally:
            conn.close()
    
    def get_employee_by_line_id(self, line_user_id: str) -> Optional[Dict]:
        """透過LINE ID取得員工資料"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT e.id, e.employee_id, e.name, e.shift_type, e.preferred_language,
                       d.dept_name_zh, d.dept_name_en, d.dept_name_vi
                FROM employees e
                JOIN line_users lu ON e.id = lu.employee_id
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE lu.line_user_id = ? AND lu.is_bound = TRUE
            ''', (line_user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'employee_id': result[1],
                    'name': result[2],
                    'shift_type': result[3],
                    'preferred_language': result[4],
                    'department': {
                        'zh': result[5],
                        'en': result[6],
                        'vi': result[7]
                    }
                }
            return None
            
        except Exception as e:
            print(f"查詢員工錯誤: {e}")
            return None
        finally:
            conn.close()

# 初始化資料庫
if __name__ == "__main__":
    print("🚀 開始初始化資料庫...")
    db = DatabaseManager()
    db.insert_initial_data()
    print("✅ 資料庫設置完成！")