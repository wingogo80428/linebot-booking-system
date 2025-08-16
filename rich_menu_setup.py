import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# LINE Bot 設定
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

def create_rich_menu():
    """建立6格Rich Menu"""
    
    # Rich Menu 設定 (3x2 格式)
    rich_menu_data = {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": True,
        "name": "交通車預約選單",
        "chatBarText": "功能選單",
        "areas": [
            # 第一排左：預約交通車
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=bus_booking",
                    "displayText": "預約交通車"
                }
            },
            # 第一排中：訂餐服務
            {
                "bounds": {
                    "x": 833,
                    "y": 0,
                    "width": 834,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=meal_booking",
                    "displayText": "訂餐服務"
                }
            },
            # 第一排右：查看預約
            {
                "bounds": {
                    "x": 1667,
                    "y": 0,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=view_booking",
                    "displayText": "查看預約"
                }
            },
            # 第二排左：取消預約
            {
                "bounds": {
                    "x": 0,
                    "y": 843,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=cancel_booking",
                    "displayText": "取消預約"
                }
            },
            # 第二排中：QR Code領餐
            {
                "bounds": {
                    "x": 833,
                    "y": 843,
                    "width": 834,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=generate_qr",
                    "displayText": "生成領餐QR"
                }
            },
            # 第二排右：語言切換
            {
                "bounds": {
                    "x": 1667,
                    "y": 843,
                    "width": 833,
                    "height": 843
                },
                "action": {
                    "type": "postback",
                    "data": "action=language_menu",
                    "displayText": "語言設定"
                }
            }
        ]
    }
    
    # 建立 Rich Menu
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = 'https://api.line.me/v2/bot/richmenu'
    response = requests.post(url, headers=headers, json=rich_menu_data)
    
    if response.status_code == 200:
        rich_menu_id = response.json()['richMenuId']
        print(f"✅ Rich Menu 建立成功！ID: {rich_menu_id}")
        return rich_menu_id
    else:
        print(f"❌ Rich Menu 建立失敗: {response.status_code}")
        print(response.text)
        return None

def create_rich_menu_image():
    """建立6格Rich Menu圖片 (HTML canvas方式)"""
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Rich Menu Generator - 6格版本</title>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        canvas { border: 2px solid #ddd; border-radius: 8px; }
        .download-btn {
            margin-top: 15px;
            padding: 12px 30px;
            background: linear-gradient(45deg, #00B900, #00A000);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,185,0,0.3);
            transition: all 0.3s;
        }
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,185,0,0.4);
        }
        .info {
            margin-top: 15px;
            padding: 15px;
            background: #e8f5e8;
            border-radius: 8px;
            border-left: 4px solid #00B900;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎨 Rich Menu 圖片產生器 (6格版本)</h2>
        <p>包含QR Code領餐認證功能的專業設計</p>
        
        <canvas id="richMenuCanvas" width="2500" height="1686"></canvas>
        <br>
        <button class="download-btn" onclick="downloadImage()">📥 下載圖片 (rich_menu.png)</button>
        
        <div class="info">
            <h3>📋 功能說明：</h3>
            <ul>
                <li><strong>🚌 預約交通車</strong> - 選擇路線和班次</li>
                <li><strong>🍱 訂餐服務</strong> - 選擇取餐地點</li>
                <li><strong>📋 查看預約</strong> - 顯示當日預約記錄</li>
                <li><strong>❌ 取消預約</strong> - 取消交通車或訂餐</li>
                <li><strong>📱 QR Code</strong> - 生成領餐認證QR碼</li>
                <li><strong>🌐 語言設定</strong> - 切換中/英/越南文</li>
            </ul>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('richMenuCanvas');
        const ctx = canvas.getContext('2d');
        
        // 設定漸層背景
        const gradient = ctx.createLinearGradient(0, 0, 0, 1686);
        gradient.addColorStop(0, '#f0f8ff');  // 淡藍色
        gradient.addColorStop(0.5, '#f8f0ff'); // 淡紫色
        gradient.addColorStop(1, '#fff8f0');   // 淡橙色
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 2500, 1686);
        
        // 畫分隔線
        ctx.strokeStyle = '#E0E0E0';
        ctx.lineWidth = 6;
        
        // 垂直分隔線
        ctx.beginPath();
        ctx.moveTo(833, 0);
        ctx.lineTo(833, 1686);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(1667, 0);
        ctx.lineTo(1667, 1686);
        ctx.stroke();
        
        // 水平分隔線
        ctx.beginPath();
        ctx.moveTo(0, 843);
        ctx.lineTo(2500, 843);
        ctx.stroke();
        
        // 設定陰影效果
        ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
        ctx.shadowBlur = 4;
        ctx.shadowOffsetY = 2;
        
        // 按鈕資料
        const buttons = [
            // 第一排
            { x: 416, y: 421, icon: '🚌', title: '預約交通車', en: 'Bus Booking', vi: 'Đặt xe buýt', color: '#4CAF50' },
            { x: 1250, y: 421, icon: '🍱', title: '訂餐服務', en: 'Meal Order', vi: 'Đặt cơm', color: '#FF9800' },
            { x: 2084, y: 421, icon: '📋', title: '查看預約', en: 'View Booking', vi: 'Xem đặt chỗ', color: '#2196F3' },
            
            // 第二排
            { x: 416, y: 1264, icon: '❌', title: '取消預約', en: 'Cancel', vi: 'Hủy đặt', color: '#F44336' },
            { x: 1250, y: 1264, icon: 'QR', title: 'QR Code', en: 'QR Code', vi: 'Mã QR', color: '#9C27B0' },
            { x: 2084, y: 1264, icon: '🌐', title: '語言設定', en: 'Language', vi: 'Ngôn ngữ', color: '#607D8B' }
        ];
        
        // 繪製每個按鈕
        buttons.forEach((btn, index) => {
            // 按鈕區域背景漸層
            const btnGradient = ctx.createRadialGradient(btn.x, btn.y - 50, 50, btn.x, btn.y - 50, 400);
            btnGradient.addColorStop(0, btn.color + '15'); // 15% 透明度
            btnGradient.addColorStop(1, btn.color + '05'); // 5% 透明度
            ctx.fillStyle = btnGradient;
            
            // 填滿整個按鈕區域
            if (index < 3) { // 第一排
                ctx.fillRect(index * 833 + (index > 0 ? 3 : 0), 0, index === 1 ? 834 : 833, 843);
            } else { // 第二排
                const col = index - 3;
                ctx.fillRect(col * 833 + (col > 0 ? 3 : 0), 843, col === 1 ? 834 : 833, 843);
            }
            
            // 超大背景圖示 (幾乎填滿格子)
            ctx.fillStyle = btn.color + '30'; // 30% 透明度，更明顯
            ctx.font = 'bold 650px Arial'; // 更大的背景圖示
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            if (btn.icon === 'QR') {
                // 為QR Code繪製超大的二維碼圖案
                drawQRCode(ctx, btn.x, btn.y - 50, btn.color + '30', 400);
            } else {
                ctx.fillText(btn.icon, btn.x, btn.y - 50);
            }
            
            // 移除前景小圖示，直接顯示文字
            
            // 主標題 (超大字體)
            ctx.fillStyle = '#1a1a1a';  
            ctx.font = 'bold 110px "Microsoft JhengHei", Arial'; // 從95px增加到110px
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 4;
            ctx.strokeText(btn.title, btn.x, btn.y - 20); // 調整位置，因為沒有前景圖示
            ctx.fillText(btn.title, btn.x, btn.y - 20);
            
            // 英文副標題 (放大)
            ctx.fillStyle = '#444444';
            ctx.font = 'bold 65px Arial'; // 從55px增加到65px
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.strokeText(btn.en, btn.x, btn.y + 60);
            ctx.fillText(btn.en, btn.x, btn.y + 60);
            
            // 越南文副標題 (放大)
            ctx.fillStyle = '#666666';
            ctx.font = 'bold 60px Arial'; // 從50px增加到60px
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.strokeText(btn.vi, btn.x, btn.y + 130);
            ctx.fillText(btn.vi, btn.x, btn.y + 130);
        });
        
        // 繪製QR Code的函數
        function drawQRCode(ctx, centerX, centerY, color, size = 200) {
            const gridSize = size / 21; // 21x21格子
            const startX = centerX - (gridSize * 10.5);
            const startY = centerY - (gridSize * 10.5);
            
            // QR Code 基本圖案 (簡化版本)
            const pattern = [
                [1,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,1],
                [1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,0,1],
                [1,0,1,1,1,0,1,0,0,1,1,1,0,0,1,0,1,1,1,0,1],
                [1,0,1,1,1,0,1,0,1,0,0,0,1,0,1,0,1,1,1,0,1],
                [1,0,0,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1],
                [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [1,0,1,1,0,1,1,1,0,0,1,0,0,1,1,1,0,1,1,0,1],
                [0,1,0,0,1,0,0,0,1,1,0,1,1,0,0,0,1,0,0,1,0],
                [1,1,1,0,0,1,1,1,1,0,1,0,1,1,1,0,0,1,1,1,1],
                [0,0,0,1,1,0,0,0,0,1,1,1,0,0,0,1,1,0,0,0,0],
                [1,0,1,0,0,1,1,1,0,0,1,0,0,1,1,0,0,1,1,0,1],
                [0,0,0,0,0,0,0,0,1,1,0,1,1,0,1,1,0,0,0,1,0],
                [1,1,1,1,1,1,1,0,0,0,1,0,1,0,0,0,1,1,1,0,1],
                [1,0,0,0,0,0,1,0,1,1,1,1,0,1,1,0,0,0,0,1,1],
                [1,0,1,1,1,0,1,0,0,0,0,0,1,0,0,1,1,1,0,0,1],
                [1,0,1,1,1,0,1,0,1,1,0,1,0,1,1,0,1,1,1,1,0],
                [1,0,1,1,1,0,1,0,0,0,1,0,1,0,0,1,0,0,0,0,1],
                [1,0,0,0,0,0,1,0,1,1,1,1,0,1,1,0,1,0,1,1,0],
                [1,1,1,1,1,1,1,0,0,0,0,0,1,0,0,1,1,1,1,0,1]
            ];
            
            ctx.fillStyle = color;
            
            for (let i = 0; i < 21; i++) {
                for (let j = 0; j < 21; j++) {
                    if (pattern[i] && pattern[i][j] === 1) {
                        ctx.fillRect(
                            startX + j * gridSize,
                            startY + i * gridSize,
                            gridSize,
                            gridSize
                        );
                    }
                }
            }
        }
        
        // 重設陰影為原始狀態
        ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
        ctx.shadowBlur = 4;
        ctx.shadowOffsetY = 2;
        
        function downloadImage() {
            const link = document.createElement('a');
            link.download = 'rich_menu.png';
            
            // 壓縮圖片到1MB以下
            const compressedDataURL = canvas.toDataURL('image/jpeg', 0.8); // 80% 品質，減少檔案大小
            link.href = compressedDataURL;
            link.click();
            
            // 顯示成功訊息和檔案大小
            const sizeInBytes = Math.round((compressedDataURL.length - 'data:image/jpeg;base64,'.length) * 3/4);
            const sizeInKB = Math.round(sizeInBytes / 1024);
            
            const btn = document.querySelector('.download-btn');
            const originalText = btn.textContent;
            btn.textContent = `✅ 下載完成！檔案大小: ${sizeInKB}KB`;
            btn.style.background = sizeInKB < 1000 ? '#4CAF50' : '#FF5722';
            
            if (sizeInKB >= 1000) {
                setTimeout(() => {
                    alert('⚠️ 檔案大小超過1MB，請降低品質或簡化設計');
                }, 100);
            }
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = 'linear-gradient(45deg, #00B900, #00A000)';
            }, 3000);
        }
        
        console.log('🎨 Rich Menu 圖片已生成！點擊下載按鈕儲存圖片。');
        console.log('📱 包含QR Code領餐認證功能的6格專業設計');
    </script>
</body>
</html>
    '''
    
    # 儲存HTML檔案
    with open('rich_menu_generator.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Rich Menu 圖片產生器已建立！")
    print("📁 請開啟 'rich_menu_generator.html' 檔案")
    print("🖼️  點擊下載按鈕儲存 rich_menu.png 圖片")
    return 'rich_menu_generator.html'

def upload_rich_menu_image(rich_menu_id, image_path):
    """上傳Rich Menu圖片"""
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'image/png'
    }
    
    url = f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content'
    
    try:
        with open(image_path, 'rb') as image_file:
            response = requests.post(url, headers=headers, data=image_file)
        
        if response.status_code == 200:
            print("✅ Rich Menu 圖片上傳成功！")
            return True
        else:
            print(f"❌ Rich Menu 圖片上傳失敗: {response.status_code}")
            print(response.text)
            return False
    except FileNotFoundError:
        print(f"❌ 找不到圖片檔案: {image_path}")
        return False

def set_default_rich_menu(rich_menu_id):
    """設定為預設Rich Menu"""
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}'
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Rich Menu 已設定為預設選單！")
        return True
    else:
        print(f"❌ 設定預設 Rich Menu 失敗: {response.status_code}")
        print(response.text)
        return False

def main():
    """主要執行流程"""
    print("🚀 開始建立 6格 Rich Menu (含QR Code功能)...")
    
    # 步驟1: 建立Rich Menu圖片產生器
    generator_file = create_rich_menu_image()
    print(f"\n📋 請按照以下步驟操作：")
    print(f"1. 開啟瀏覽器，打開檔案: {generator_file}")
    print(f"2. 點擊「📥 下載圖片」按鈕，儲存為 'rich_menu.png'")
    print(f"3. 將 rich_menu.png 放在專案資料夾中")
    print(f"4. 按 Enter 繼續...")
    
    input()  # 等待使用者操作
    
    # 步驟2: 建立Rich Menu
    rich_menu_id = create_rich_menu()
    if not rich_menu_id:
        return
    
    # 步驟3: 上傳圖片
    image_uploaded = upload_rich_menu_image(rich_menu_id, 'rich_menu.png')
    if not image_uploaded:
        return
    
    # 步驟4: 設定為預設選單
    set_default_rich_menu(rich_menu_id)
    
    print("\n🎉 6格 Rich Menu 設定完成！")
    print("📱 現在打開LINE Bot，應該可以看到下方的6格功能選單了！")
    print(f"🆔 Rich Menu ID: {rich_menu_id}")
    print("\n🔥 新功能：")
    print("   📱 QR Code 領餐認證")
    print("   🌐 多語言切換")
    print("   🎨 專業視覺設計")

if __name__ == "__main__":
    main()