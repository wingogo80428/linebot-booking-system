echo "# 安裝與設定指南" > SETUP.md
echo "" >> SETUP.md
echo "## 環境需求" >> SETUP.md
echo "- Python 3.8+" >> SETUP.md
echo "- LINE Bot Channel Access Token" >> SETUP.md
echo "- LINE Bot Channel Secret" >> SETUP.md
echo "" >> SETUP.md
echo "## 安裝步驟" >> SETUP.md
echo "1. Clone 專案：" >> SETUP.md
echo "   \`\`\`bash" >> SETUP.md
echo "   git clone https://github.com/您的帳號/linebot-booking-system.git" >> SETUP.md
echo "   cd linebot-booking-system" >> SETUP.md
echo "   \`\`\`" >> SETUP.md
echo "" >> SETUP.md
echo "2. 安裝套件：" >> SETUP.md
echo "   \`\`\`bash" >> SETUP.md
echo "   pip install -r requirements.txt" >> SETUP.md
echo "   \`\`\`" >> SETUP.md
echo "" >> SETUP.md
echo "3. 設定環境變數：" >> SETUP.md
echo "   建立 \`.env\` 檔案：" >> SETUP.md
echo "   \`\`\`" >> SETUP.md
echo "   CHANNEL_ACCESS_TOKEN=您的_Access_Token" >> SETUP.md
echo "   CHANNEL_SECRET=您的_Channel_Secret" >> SETUP.md
echo "   \`\`\`" >> SETUP.md
echo "" >> SETUP.md
echo "4. 初始化資料庫：" >> SETUP.md
echo "   \`\`\`bash" >> SETUP.md
echo "   python database.py" >> SETUP.md
echo "   \`\`\`" >> SETUP.md
echo "" >> SETUP.md
echo "5. 啟動系統：" >> SETUP.md
echo "   \`\`\`bash" >> SETUP.md
echo "   python app.py" >> SETUP.md
echo "   \`\`\`" >> SETUP.md

git add SETUP.md
git commit -m "📝 新增專案安裝指南"
git push