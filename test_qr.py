import qrcode
import json
from datetime import date

# 測試QR Code生成
def test_qr_generation():
    # 模擬的領餐資料
    qr_data = {
        'type': 'meal_pickup',
        'employee_id': 'IGA1-02849',
        'employee_name': '測試員工',
        'date': str(date.today()),
        'restaurant': '6樓拉亞漢堡',
        'verification_code': f"IGA1-02849-{date.today().strftime('%Y%m%d')}"
    }
    
    # 轉換為JSON
    qr_content = json.dumps(qr_data, ensure_ascii=False)
    print("QR碼內容：", qr_content)
    
    # 生成QR碼並保存
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save("test_meal_qr.png")
    print("✅ QR碼已保存為 test_meal_qr.png")

if __name__ == "__main__":
    test_qr_generation()