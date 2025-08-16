from flask import Flask, request, abort
import os
import urllib.parse
from datetime import datetime, date, time
from dotenv import load_dotenv
from database import DatabaseManager

# 使用新版的LINE Bot SDK v3
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)

# 載入環境變數
load_dotenv()

app = Flask(__name__)
db = DatabaseManager()

# 設定LINE Bot
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 多語言支援
MESSAGES = {
    'zh': {
        'welcome': '歡迎使用交通車預約訂餐系統！',
        'bind_required': '請先輸入您的員工編號進行綁定\n格式：IGA1-02849',
        'bind_success': '✅ 綁定成功！歡迎 {}！',
        'bind_failed': '❌ 綁定失敗：{}',
        'main_menu_title': '交通車預約訂餐系統',
        'main_menu_text': '請選擇您要使用的功能：',
        'bus_booking': '🚌 預約交通車',
        'meal_booking': '🍱 訂餐服務',
        'view_booking': '📋 查看我的預約',
        'cancel_booking': '❌ 取消預約',
        'route_selection': '選擇交通車路線',
        'route_selection_text': '請選擇您要預約的路線：',
        'schedule_selection_text': '請選擇班次時間：',
        'meal_location': '選擇取餐地點',
        'meal_location_text': '請選擇您要訂餐的地點：',
        'back_to_menu': '🔙 返回主選單',
        'booking_success': '✅ 預約成功！',
        'booking_failed': '❌ 預約失敗：{}',
        'time_limit_exceeded': '❌ 超過預約時間限制',
        'no_bookings': '您目前沒有預約記錄',
        'qr_code_title': '🍱 領餐認證QR碼',
        'qr_code_desc': '請向餐廳人員出示此QR碼領取餐點',
        'qr_code_invalid': '❌ 您今日沒有訂餐記錄，無法生成QR碼',
        'language_changed': '✅ 語言已切換為：{}',
        'cancel_success': '✅ 取消成功！',
        'cancel_failed': '❌ 取消失敗：{}',
        'nothing_to_cancel': '❌ 沒有可取消的預約'
    },
    'en': {
        'welcome': 'Welcome to Bus & Meal Booking System!',
        'bind_required': 'Please enter your employee ID for binding\nFormat: IGA1-02849',
        'bind_success': '✅ Binding successful! Welcome {}!',
        'bind_failed': '❌ Binding failed: {}',
        'main_menu_title': 'Bus & Meal Booking System',
        'main_menu_text': 'Please select the function you want to use:',
        'bus_booking': '🚌 Book Bus',
        'meal_booking': '🍱 Order Meal',
        'view_booking': '📋 View My Bookings',
        'cancel_booking': '❌ Cancel Booking',
        'route_selection': 'Select Bus Route',
        'route_selection_text': 'Please select the route you want to book:',
        'schedule_selection_text': 'Please select departure time:',
        'meal_location': 'Select Meal Location',
        'meal_location_text': 'Please select where you want to order:',
        'back_to_menu': '🔙 Back to Main Menu',
        'booking_success': '✅ Booking successful!',
        'booking_failed': '❌ Booking failed: {}',
        'time_limit_exceeded': '❌ Booking time limit exceeded',
        'no_bookings': 'You have no current bookings',
        'qr_code_title': '🍱 Meal Pickup QR Code',
        'qr_code_desc': 'Please show this QR code to restaurant staff',
        'qr_code_invalid': '❌ No meal order today, cannot generate QR code',
        'language_changed': '✅ Language changed to: {}',
        'cancel_success': '✅ Cancelled successfully!',
        'cancel_failed': '❌ Cancel failed: {}',
        'nothing_to_cancel': '❌ Nothing to cancel'
    },
    'vi': {
        'welcome': 'Chào mừng đến với Hệ thống Đặt xe & Đặt cơm!',
        'bind_required': 'Vui lòng nhập mã nhân viên để liên kết\nĐịnh dạng: IGA1-02849',
        'bind_success': '✅ Liên kết thành công! Chào mừng {}!',
        'bind_failed': '❌ Liên kết thất bại: {}',
        'main_menu_title': 'Hệ thống Đặt xe & Đặt cơm',
        'main_menu_text': 'Vui lòng chọn chức năng bạn muốn sử dụng:',
        'bus_booking': '🚌 Đặt xe',
        'meal_booking': '🍱 Đặt cơm',
        'view_booking': '📋 Xem đặt chỗ của tôi',
        'cancel_booking': '❌ Hủy đặt chỗ',
        'route_selection': 'Chọn tuyến xe',
        'route_selection_text': 'Vui lòng chọn tuyến bạn muốn đặt:',
        'schedule_selection_text': 'Vui lòng chọn giờ khởi hành:',
        'meal_location': 'Chọn địa điểm ăn',
        'meal_location_text': 'Vui lòng chọn nơi bạn muốn đặt cơm:',
        'back_to_menu': '🔙 Về menu chính',
        'booking_success': '✅ Đặt chỗ thành công!',
        'booking_failed': '❌ Đặt chỗ thất bại: {}',
        'time_limit_exceeded': '❌ Đã quá thời gian đặt chỗ',
        'no_bookings': 'Bạn hiện tại không có đặt chỗ nào',
        'qr_code_title': '🍱 Mã QR nhận cơm',
        'qr_code_desc': 'Vui lòng xuất trình mã QR này cho nhân viên nhà hàng',
        'qr_code_invalid': '❌ Không có đơn đặt cơm hôm nay, không thể tạo mã QR',
        'language_changed': '✅ Đã chuyển ngôn ngữ sang: {}',
        'cancel_success': '✅ Hủy thành công!',
        'cancel_failed': '❌ Hủy thất bại: {}',
        'nothing_to_cancel': '❌ Không có gì để hủy'
    }
}

@app.route("/", methods=['GET'])
def home():
    return "交通車預約系統正在運行中！"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    return 'OK'

def get_user_language(line_user_id: str) -> str:
    """取得使用者語言設定"""
    employee = db.get_employee_by_line_id(line_user_id)
    if employee:
        return employee.get('preferred_language', 'zh')
    return 'zh'

def get_message(key: str, lang: str = 'zh', *args) -> str:
    """取得多語言訊息"""
    message = MESSAGES.get(lang, MESSAGES['zh']).get(key, key)
    if args:
        return message.format(*args)
    return message

def check_time_limit(shift_type: str, booking_type: str) -> bool:
    """檢查是否超過預約時間限制"""
    now = datetime.now().time()
    
    if booking_type == 'bus':
        if shift_type == 'day':
            limit = time(14, 30)  # 14:30
        else:
            limit = time(9, 0)    # 09:00
    elif booking_type == 'meal':
        if shift_type == 'day':
            limit = time(9, 0)    # 09:00
        else:
            limit = time(21, 0)   # 21:00
    
    return now <= limit

def generate_meal_verification_code(employee_data: dict, meal_data: dict) -> str:
    """生成領餐驗證碼"""
    today = date.today()
    verification_code = f"{employee_data['employee_id']}-{today.strftime('%Y%m%d')}"
    return verification_code

def create_main_menu(lang: str = 'zh'):
    """建立主選單"""
    buttons_template = ButtonsTemplate(
        title=get_message('main_menu_title', lang),
        text=get_message('main_menu_text', lang),
        actions=[
            PostbackAction(
                label=get_message('bus_booking', lang),
                data='action=bus_booking'
            ),
            PostbackAction(
                label=get_message('meal_booking', lang),
                data='action=meal_booking'
            ),
            PostbackAction(
                label=get_message('view_booking', lang),
                data='action=view_booking'
            ),
            PostbackAction(
                label=get_message('cancel_booking', lang),
                data='action=cancel_booking'
            )
        ]
    )
    return TemplateMessage(alt_text=get_message('main_menu_title', lang), template=buttons_template)

def create_language_menu(current_lang: str = 'zh'):
    """建立語言選擇選單"""
    languages = {
        'zh': '中文 🇹🇼',
        'en': 'English 🇺🇸', 
        'vi': 'Tiếng Việt 🇻🇳'
    }
    
    actions = []
    for lang_code, lang_name in languages.items():
        if lang_code != current_lang:  # 不顯示當前語言
            actions.append(PostbackAction(
                label=lang_name,
                data=f'action=change_language&lang={lang_code}'
            ))
    
    actions.append(PostbackAction(
        label=get_message('back_to_menu', current_lang),
        data='action=main_menu'
    ))
    
    buttons_template = ButtonsTemplate(
        title='語言設定 Language',
        text='選擇語言 Choose Language:',
        actions=actions
    )
    return TemplateMessage(alt_text='Language Settings', template=buttons_template)

def create_cancel_menu(lang: str = 'zh'):
    """建立取消預約選單"""
    title_text = {
        'zh': '取消預約',
        'en': 'Cancel Booking', 
        'vi': 'Hủy đặt chỗ'
    }
    
    desc_text = {
        'zh': '請選擇要取消的項目:',
        'en': 'Select item to cancel:',
        'vi': 'Chọn mục cần hủy:'
    }
    
    bus_text = {
        'zh': '🚌 取消交通車',
        'en': '🚌 Cancel Bus',
        'vi': '🚌 Hủy xe'
    }
    
    meal_text = {
        'zh': '🍱 取消訂餐',
        'en': '🍱 Cancel Meal',
        'vi': '🍱 Hủy cơm'
    }
    
    buttons_template = ButtonsTemplate(
        title=title_text[lang],
        text=desc_text[lang],
        actions=[
            PostbackAction(
                label=bus_text[lang],
                data='action=cancel_confirm&type=bus'
            ),
            PostbackAction(
                label=meal_text[lang],
                data='action=cancel_confirm&type=meal'
            ),
            PostbackAction(
                label=get_message('back_to_menu', lang),
                data='action=main_menu'
            )
        ]
    )
    return TemplateMessage(alt_text=title_text[lang], template=buttons_template)

def create_bus_route_menu(lang: str = 'zh'):
    """建立交通車路線選單"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, route_code, route_name_zh, route_name_en, route_name_vi FROM bus_routes WHERE is_active = TRUE')
    routes = cursor.fetchall()
    conn.close()
    
    actions = []
    for route in routes:
        route_id, code, name_zh, name_en, name_vi = route
        if lang == 'en':
            label = f'🚌 {name_en}'
        elif lang == 'vi':
            label = f'🚌 {name_vi}'
        else:
            label = f'🚌 {name_zh}'
        
        actions.append(PostbackAction(
            label=label,
            data=f'action=bus_route&route_id={route_id}&route_code={code}'
        ))
    
    actions.append(PostbackAction(
        label=get_message('back_to_menu', lang),
        data='action=main_menu'
    ))
    
    buttons_template = ButtonsTemplate(
        title=get_message('route_selection', lang),
        text=get_message('route_selection_text', lang),
        actions=actions
    )
    return TemplateMessage(alt_text=get_message('route_selection', lang), template=buttons_template)

def create_bus_schedule_menu(route_id: int, shift_type: str, lang: str = 'zh'):
    """建立班次選單"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bs.id, bs.departure_time, bs.schedule_name_zh, bs.schedule_name_en, bs.schedule_name_vi,
               br.route_name_zh, br.route_name_en, br.route_name_vi
        FROM bus_schedules bs
        JOIN bus_routes br ON bs.route_id = br.id
        WHERE bs.route_id = ? AND bs.shift_type = ? AND bs.is_active = TRUE
    ''', (route_id, shift_type))
    schedules = cursor.fetchall()
    conn.close()
    
    if not schedules:
        return TextMessage(text="目前沒有可用的班次")
    
    actions = []
    route_name = schedules[0][5] if lang == 'zh' else schedules[0][6] if lang == 'en' else schedules[0][7]
    
    for schedule in schedules:
        schedule_id, departure_time, name_zh, name_en, name_vi = schedule[:5]
        
        if lang == 'en':
            label = f'🕐 {departure_time} {name_en}'
        elif lang == 'vi':
            label = f'🕐 {departure_time} {name_vi}'
        else:
            label = f'🕐 {departure_time} {name_zh}'
        
        actions.append(PostbackAction(
            label=label,
            data=f'action=bus_confirm&schedule_id={schedule_id}&time={departure_time}'
        ))
    
    actions.append(PostbackAction(
        label=get_message('back_to_menu', lang),
        data='action=main_menu'
    ))
    
    buttons_template = ButtonsTemplate(
        title=route_name,
        text=get_message('schedule_selection_text', lang),
        actions=actions
    )
    return TemplateMessage(alt_text=route_name, template=buttons_template)

def create_meal_location_menu(lang: str = 'zh'):
    """建立訂餐地點選單"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, floor, name_zh, name_en, name_vi FROM restaurants WHERE is_active = TRUE')
    restaurants = cursor.fetchall()
    conn.close()
    
    # 按樓層分組
    floors = {}
    for restaurant in restaurants:
        floor = restaurant[1]
        if floor not in floors:
            floors[floor] = []
        floors[floor].append(restaurant)
    
    actions = []
    for floor, floor_restaurants in floors.items():
        restaurant_names = []
        restaurant_ids = []
        
        for rest in floor_restaurants:
            restaurant_ids.append(str(rest[0]))
            if lang == 'en':
                restaurant_names.append(rest[3])
            elif lang == 'vi':
                restaurant_names.append(rest[4])
            else:
                restaurant_names.append(rest[2])
        
        label = f'🍱 {floor} - {", ".join(restaurant_names)}'
        actions.append(PostbackAction(
            label=label,
            data=f'action=meal_confirm&restaurant_ids={",".join(restaurant_ids)}&floor={floor}'
        ))
    
    actions.append(PostbackAction(
        label=get_message('back_to_menu', lang),
        data='action=main_menu'
    ))
    
    buttons_template = ButtonsTemplate(
        title=get_message('meal_location', lang),
        text=get_message('meal_location_text', lang),
        actions=actions
    )
    return TemplateMessage(alt_text=get_message('meal_location', lang), template=buttons_template)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    line_user_id = event.source.user_id
    user_message = event.message.text.strip()
    
    # 檢查使用者是否已綁定
    employee = db.get_employee_by_line_id(line_user_id)
    lang = get_user_language(line_user_id)
    
    if not employee:
        # 檢查是否為員工編號格式 (例: IGA1-02849)
        if len(user_message) == 10 and '-' in user_message:
            result = db.bind_line_user(line_user_id, user_message.upper())
            if result['success']:
                reply_message = TextMessage(text=get_message('bind_success', lang, result['message']))
            else:
                reply_message = TextMessage(text=get_message('bind_failed', lang, result['message']))
        else:
            reply_message = TextMessage(text=get_message('bind_required', lang))
    else:
        # 已綁定使用者，顯示主選單
        if any(keyword in user_message.lower() for keyword in ['你好', 'hi', 'hello', '開始', '選單', 'menu', 'xin chào']):
            reply_message = create_main_menu(lang)
        else:
            reply_message = TextMessage(
                text=get_message('welcome', lang),
                quick_reply=QuickReply(
                    items=[
                        QuickReplyItem(
                            action=PostbackAction(label="🏠 主選單", data="action=main_menu")
                        )
                    ]
                )
            )
    
    # 送出回覆
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    line_user_id = event.source.user_id
    data = event.postback.data
    
    # 檢查使用者是否已綁定
    employee = db.get_employee_by_line_id(line_user_id)
    if not employee:
        reply_message = TextMessage(text=get_message('bind_required'))
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[reply_message]
                )
            )
        return
    
    lang = employee.get('preferred_language', 'zh')
    shift_type = employee.get('shift_type')
    employee_id = employee.get('id')
    
    # 解析postback data
    params = {}
    for param in data.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            params[key] = value
    
    action = params.get('action')
    
    # 處理不同的action
    if action == 'main_menu':
        reply_message = create_main_menu(lang)
        
    elif action == 'generate_qr':
        # 檢查今日是否有訂餐記錄
        conn = db.get_connection()
        cursor = conn.cursor()
        
        today = date.today()
        cursor.execute('''
            SELECT r.name_zh, r.floor, mo.ordered_at
            FROM meal_orders mo
            JOIN restaurants r ON mo.restaurant_id = r.id
            WHERE mo.employee_id = ? AND mo.order_date = ? AND mo.status = 'active'
        ''', (employee_id, today))
        
        meal_record = cursor.fetchone()
        conn.close()
        
        if meal_record:
            # 生成驗證碼
            verification_code = generate_meal_verification_code(employee, {
                'restaurant_name': meal_record[0],
                'floor': meal_record[1],
                'ordered_at': str(meal_record[2])
            })
            
            # 生成QR Code圖片URL
            qr_content = f"員工：{employee['name']}\n編號：{employee['employee_id']}\n餐廳：{meal_record[0]}\n樓層：{meal_record[1]}\n日期：{today}\n驗證碼：{verification_code}"
            encoded_content = urllib.parse.quote(qr_content)
            qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_content}"
            
            # 發送文字 + QR Code圖片
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text=f"{get_message('qr_code_title', lang)}\n\n{get_message('qr_code_desc', lang)}\n\n👤 {employee['name']}\n🍱 {meal_record[0]}\n📍 {meal_record[1]}\n📅 {today}\n\n🔢 驗證碼：{verification_code}\n\n📱 請出示下方QR碼給餐廳人員：",
                                quick_reply=QuickReply(
                                    items=[
                                        QuickReplyItem(
                                            action=PostbackAction(label="🏠 返回主選單", data="action=main_menu")
                                        )
                                    ]
                                )
                            ),
                            ImageMessage(
                                original_content_url=qr_image_url,
                                preview_image_url=qr_image_url
                            )
                        ]
                    )
                )
            return  # 提早返回，避免重複發送
        else:
            reply_message = TextMessage(text=get_message('qr_code_invalid', lang))
            
    elif action == 'language_menu':
        reply_message = create_language_menu(lang)
        
    elif action == 'change_language':
        new_lang = params.get('lang', 'zh')
        
        # 更新資料庫中的語言設定
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees 
            SET preferred_language = ? 
            WHERE id = ?
        ''', (new_lang, employee_id))
        conn.commit()
        conn.close()
        
        lang_names = {'zh': '中文', 'en': 'English', 'vi': 'Tiếng Việt'}
        reply_message = TextMessage(
            text=get_message('language_changed', new_lang, lang_names[new_lang]),
            quick_reply=QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(label="🏠 主選單", data="action=main_menu")
                    )
                ]
            )
        )
        
    elif action == 'cancel_booking':
        reply_message = create_cancel_menu(lang)
        
    elif action == 'cancel_confirm':
        cancel_type = params.get('type')
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            today = date.today()
            if cancel_type == 'bus':
                cursor.execute('''
                    UPDATE bus_reservations 
                    SET status = 'cancelled' 
                    WHERE employee_id = ? AND reservation_date = ? AND status = 'active'
                ''', (employee_id, today))
            elif cancel_type == 'meal':
                cursor.execute('''
                    UPDATE meal_orders 
                    SET status = 'cancelled' 
                    WHERE employee_id = ? AND order_date = ? AND status = 'active'
                ''', (employee_id, today))
            
            if cursor.rowcount > 0:
                conn.commit()
                type_name = '交通車' if cancel_type == 'bus' else '訂餐'
                if lang == 'en':
                    type_name = 'Bus' if cancel_type == 'bus' else 'Meal'
                elif lang == 'vi':
                    type_name = 'Xe' if cancel_type == 'bus' else 'Cơm'
                    
                reply_message = TextMessage(
                    text=get_message('cancel_success', lang) + f" ({type_name})",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyItem(
                                action=PostbackAction(label="🏠 返回主選單", data="action=main_menu")
                            )
                        ]
                    )
                )
            else:
                reply_message = TextMessage(text=get_message('nothing_to_cancel', lang))
                
        except Exception as e:
            conn.rollback()
            reply_message = TextMessage(text=get_message('cancel_failed', lang, str(e)))
        finally:
            conn.close()
    
    elif action == 'bus_booking':
        if not check_time_limit(shift_type, 'bus'):
            reply_message = TextMessage(text=get_message('time_limit_exceeded', lang))
        else:
            reply_message = create_bus_route_menu(lang)
        
    elif action == 'bus_route':
        route_id = int(params.get('route_id'))
        reply_message = create_bus_schedule_menu(route_id, shift_type, lang)
        
    elif action == 'bus_confirm':
        schedule_id = int(params.get('schedule_id'))
        time_str = params.get('time')
        
        # 儲存預約到資料庫
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # 先刪除今天的舊預約 (覆蓋機制)
            today = datetime.now().date()
            cursor.execute('''
                UPDATE bus_reservations 
                SET status = 'cancelled' 
                WHERE employee_id = ? AND reservation_date = ? AND status = 'active'
            ''', (employee_id, today))
            
            # 新增預約
            cursor.execute('''
                INSERT INTO bus_reservations (employee_id, schedule_id, reservation_date)
                VALUES (?, ?, ?)
            ''', (employee_id, schedule_id, today))
            
            conn.commit()
            reply_message = TextMessage(
                text=f"{get_message('booking_success', lang)}\n\n🚌 班次時間：{time_str}\n📅 日期：{today}",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyItem(
                            action=PostbackAction(label="🏠 返回主選單", data="action=main_menu")
                        ),
                        QuickReplyItem(
                            action=PostbackAction(label="🚌 再預約", data="action=bus_booking")
                        )
                    ]
                )
            )
            
        except Exception as e:
            conn.rollback()
            reply_message = TextMessage(text=get_message('booking_failed', lang, str(e)))
        finally:
            conn.close()
        
    elif action == 'meal_booking':
        if not check_time_limit(shift_type, 'meal'):
            reply_message = TextMessage(text=get_message('time_limit_exceeded', lang))
        else:
            reply_message = create_meal_location_menu(lang)
        
    elif action == 'meal_confirm':
        restaurant_ids = params.get('restaurant_ids', '').split(',')
        floor = params.get('floor')
        
        # 簡化處理：選擇第一個餐廳
        if restaurant_ids and restaurant_ids[0]:
            restaurant_id = int(restaurant_ids[0])
            
            conn = db.get_connection()
            cursor = conn.cursor()
            
            try:
                # 先刪除今天的舊訂餐 (覆蓋機制)
                today = datetime.now().date()
                cursor.execute('''
                    UPDATE meal_orders 
                    SET status = 'cancelled' 
                    WHERE employee_id = ? AND order_date = ? AND status = 'active'
                ''', (employee_id, today))
                
                # 新增訂餐
                cursor.execute('''
                    INSERT INTO meal_orders (employee_id, restaurant_id, order_date)
                    VALUES (?, ?, ?)
                ''', (employee_id, restaurant_id, today))
                
                conn.commit()
                reply_message = TextMessage(
                    text=f"{get_message('booking_success', lang)}\n\n🍱 取餐地點：{floor}\n📅 日期：{today}",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyItem(
                                action=PostbackAction(label="🏠 返回主選單", data="action=main_menu")
                            ),
                            QuickReplyItem(
                                action=PostbackAction(label="🍱 再訂餐", data="action=meal_booking")
                            )
                        ]
                    )
                )
                
            except Exception as e:
                conn.rollback()
                reply_message = TextMessage(text=get_message('booking_failed', lang, str(e)))
            finally:
                conn.close()
        
    elif action == 'view_booking':
        # 查看預約記錄
        conn = db.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute('''
            SELECT 'bus' as type, br.route_name_zh, bs.departure_time, bs.schedule_name_zh
            FROM bus_reservations bresv
            JOIN bus_schedules bs ON bresv.schedule_id = bs.id
            JOIN bus_routes br ON bs.route_id = br.id
            WHERE bresv.employee_id = ? AND bresv.reservation_date = ? AND bresv.status = 'active'
            
            UNION ALL
            
            SELECT 'meal' as type, r.name_zh, r.floor, ''
            FROM meal_orders mo
            JOIN restaurants r ON mo.restaurant_id = r.id
            WHERE mo.employee_id = ? AND mo.order_date = ? AND mo.status = 'active'
        ''', (employee_id, today, employee_id, today))
        
        bookings = cursor.fetchall()
        conn.close()
        
        if bookings:
            booking_text = f"📋 今日預約記錄 ({today}):\n\n"
            for booking in bookings:
                if booking[0] == 'bus':
                    booking_text += f"🚌 交通車：{booking[1]} {booking[2]} ({booking[3]})\n"
                else:
                    booking_text += f"🍱 訂餐：{booking[2]} {booking[1]}\n"
        else:
            booking_text = get_message('no_bookings', lang)
        
        reply_message = TextMessage(
            text=booking_text,
            quick_reply=QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(label="🏠 返回主選單", data="action=main_menu")
                    )
                ]
            )
        )
        
    else:
        reply_message = TextMessage(text="系統錯誤，請重新開始")
    
    # 送出回覆
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )

if __name__ == "__main__":
    print("LINE Bot 伺服器啟動中...")
    app.run(debug=True, port=5000)