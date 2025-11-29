# 2FA Bypass Testing Tool - User Guide

## 🎯 Mô Tả

Tool tự động kiểm tra các lỗ hổng bảo mật 2FA (Two-Factor Authentication) trên 2 nền tảng:
- **GHN** (Giao Hàng Nhanh): https://sso.ghn.vn
- **BEST Express**: https://www.best-inc.vn

Tool sẽ tự động:
1. Đăng nhập vào website với tài khoản/mật khẩu của bạn
2. Phát hiện loại 2FA (SMS OTP, Email OTP, hoặc Google Authenticator)
3. Thử lần lượt các phương pháp bypass 2FA phổ biến
4. Dừng lại ngay khi tìm thấy phương pháp bypass thành công
5. Lưu screenshot kết quả

## 🔧 Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.8+
- Google Chrome browser
- Windows/Linux/MacOS

### Bước 1: Clone Repository
```bash
git clone https://github.com/anht3k52/2FA-Bypass.git
cd 2FA-Bypass
```

### Bước 2: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

Hoặc với virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Bước 3: Cấu Hình (Optional)
Copy file `.env.example` thành `.env` và điền thông tin:
```bash
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
GHN_USERNAME=0987654321
GHN_PASSWORD=your_password

BEST_USERNAME=your_username
BEST_PASSWORD=your_password

HEADLESS_MODE=False
BROWSER_TIMEOUT=30
```

## 🚀 Sử Dụng

### Chạy Tool
```bash
python bypass_2fa.py
```

### Quy Trình Sử Dụng

1. **Chọn Website**
   ```
   Select website:
   1. GHN (Giao Hàng Nhanh)
   2. BEST Express
   
   Enter choice (1 or 2): 1
   ```

2. **Nhập Thông Tin Đăng Nhập**
   ```
   GHN Login Details
   Enter username/phone: 0987654321
   Enter password: ********
   ```

3. **Xác Nhận**
   ```
   Do you confirm you have permission to test this account? (yes/no)
   yes
   ```

4. **Quan Sát Kết Quả**
   - Tool sẽ tự động mở Chrome browser
   - Đăng nhập với credentials bạn cung cấp
   - Phát hiện loại 2FA
   - Thử từng phương pháp bypass theo thứ tự:
     1. Response Manipulation
     2. Status Code Manipulation
     3. Null/Missing OTP
     4. Session Hijacking
     5. CSRF/Referrer Manipulation
     6. Rate Limiting Test

5. **Kết Quả**
   - ✅ Nếu bypass thành công → Tool dừng lại và lưu screenshot
   - ❌ Nếu tất cả phương pháp đều thất bại → Báo 2FA được bảo vệ tốt

## 📊 Các Phương Pháp Bypass

### 1. Response Manipulation
Thay đổi response từ server (ví dụ: `success: false` → `success: true`)

### 2. Status Code Manipulation  
Thay đổi HTTP status code (ví dụ: `401` → `200 OK`)

### 3. Null/Missing OTP
Thử submit các giá trị null hoặc mặc định:
- Empty string
- "000000"
- "123456"
- "null"

### 4. Session Hijacking
Thử truy cập trực tiếp vào trang được bảo vệ bằng session hiện tại

### 5. CSRF/Referrer Manipulation
Thao túng referrer header để giả mạo nguồn request

### 6. Rate Limiting Test
Kiểm tra có rate limiting không (để ngăn chặn brute force)

## 📁 Cấu Trúc Output

```
2FA-Bypass/
├── screenshots/           # Screenshots khi bypass thành công
│   ├── ghn_Response_Manipulation.png
│   └── best_Null_OTP.png
├── logs/                 # Logs chi tiết (nếu có)
└── bypass_2fa.py        # Main script
```

## ⚠️ Lưu Ý Quan Trọng

### An Toàn
1. **Chỉ test trên tài khoản của bạn** hoặc có văn bản cho phép
2. **Sử dụng VPN** khi test để bảo vệ IP thật
3. **Backup dữ liệu** trước khi test
4. **Test với tần suất hợp lý** để tránh bị khóa tài khoản

### Pháp Lý
- ✅ Test trên tài khoản của bạn: **Hợp pháp** cho mục đích học tập
- ❌ Test trên tài khoản người khác không có phép: **Bất hợp pháp**
- ⚖️ Vi phạm có thể bị xử lý theo:
  - Luật An ninh mạng Việt Nam (2018)
  - Nghị định 53/2022/NĐ-CP

### Kỹ Thuật
- Tool yêu cầu Chrome browser được cài đặt
- Một số website có CAPTCHA có thể cần giải thủ công
- Kết quả phụ thuộc vào cấu hình bảo mật của từng website
- Tool sử dụng `selenium-wire` để intercept HTTP requests/responses

## 🐛 Troubleshooting

### Lỗi: ChromeDriver not found
```bash
# Cài đặt lại webdriver-manager
pip install --upgrade webdriver-manager
```

### Lỗi: Selenium không tìm thấy element
- Website có thể đã thay đổi cấu trúc HTML
- Cập nhật CSS selectors trong code

### Browser bị phát hiện là bot
- Website có thể dùng anti-bot protection
- Thử chạy ở chế độ không headless
- Sử dụng undetected-chromedriver (cần cài thêm)

### Rate limit bị chặn
- Đợi 15-30 phút trước khi thử lại
- Sử dụng VPN/proxy khác
- Giảm số lần thử trong code

## 📚 Tài Liệu Tham Khảo

- [README.md](README.md) - Danh sách đầy đủ các kỹ thuật bypass 2FA
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [HowToHunt - OTP Bypass](https://kathan19.gitbook.io/howtohunt/authentication-bypass/otp_bypass)

## 🤝 Đóng Góp

Nếu bạn phát hiện thêm phương pháp bypass hoặc muốn cải thiện tool:
1. Fork repository
2. Tạo branch mới: `git checkout -b feature/new-bypass-method`
3. Commit changes: `git commit -m "Add new bypass method"`
4. Push: `git push origin feature/new-bypass-method`
5. Tạo Pull Request

## 📝 License

This project is for **educational purposes only**. Use at your own risk.

## 📧 Contact

- GitHub: [@anht3k52](https://github.com/anht3k52)
- Repository: https://github.com/anht3k52/2FA-Bypass

---

**Disclaimer**: Công cụ này được tạo ra với mục đích giáo dục và nghiên cứu bảo mật. Tác giả không chịu trách nhiệm về bất kỳ hành vi lạm dụng nào. Luôn tuân thủ pháp luật và đạo đức khi sử dụng.
