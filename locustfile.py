from locust import HttpUser, task, between
import json
from dotenv import load_dotenv
import os

load_dotenv()
# def check_env_credentials():
#     """
#     ฟังก์ชันสำหรับทดสอบว่าตัวแปรจาก .env ถูกโหลดเข้าสู่ Environment หรือไม่
#     """
#     username = os.environ.get("LOCUST_TEST_USERNAME")
#     password = os.environ.get("LOCUST_TEST_PASSWORD")
#     device = os.environ.get("LOCUST_TEST_DEVICE")
    
#     print("\n=============================================")
#     print("      🔑 ตรวจสอบ Credentials จากไฟล์ .env")
#     print("=============================================")
    
#     if username is None or password is None:
#         print("❌ ERROR: ดึงตัวแปร LOCUST_TEST_USERNAME หรือ LOCUST_TEST_PASSWORD ไม่ได้!")
#         print("   โปรดตรวจสอบ:")
#         print("   - คุณได้สร้างไฟล์ .env และใส่ตัวแปรทั้งสองตัวหรือไม่")
#         print("   - ชื่อตัวแปรใน .env สะกดตรงกับในโค้ดหรือไม่")
#     else:
#         print(f"✅ Username (LOCUST_TEST_USERNAME) โหลดสำเร็จ: {username}")
#         # เราจะไม่ print รหัสผ่านเต็มๆ เพื่อความปลอดภัย
#         print(f"✅ Password (LOCUST_TEST_PASSWORD) โหลดสำเร็จ: {password[:2]}****{password[-2:]} (ตัวอย่าง 4 ตัวอักษรแรก/หลัง)")
#         print(f"✅ Device (LOCUST_TEST_DEVICE) โหลดสำเร็จ: {device}")
        
#     print("=============================================\n")
    
#     # ส่งค่า Credentials ที่ถูกต้องกลับไปใช้งาน
#     return {
#         "username": username,
#         "password": password,
#         "device": device
#     }

# # 3. เรียกใช้ฟังก์ชันเพื่อทดสอบทันที และเก็บค่าไว้ใน Global Variable
# USER_CREDENTIALS = check_env_credentials()

# 🚨 กำหนดค่า Credentials สำหรับการ Login
# (คุณต้องแทนที่ค่าเหล่านี้ด้วย Username/Password ที่ใช้งานได้จริงในระบบ)
USER_CREDENTIALS = {
    "username": os.environ.get("LOCUST_TEST_USERNAME"),
    "password": os.environ.get("LOCUST_TEST_PASSWORD"),
    "device": os.environ.get("LOCUST_TEST_DEVICE", "BACKEND") 
}

class HendrixAPILoadTest(HttpUser):
    """
    User Class สำหรับทดสอบ Load Test ระบบ Hendrix API
    """
    host = "https://dev.notero.co/api" 
    # กำหนดช่วงเวลาหน่วงระหว่าง Requests: 1 ถึง 5 วินาที
    wait_time = between(1, 5) 

    def on_start(self):
        """
        ฟังก์ชันนี้จะทำงานครั้งเดียวเมื่อ User เริ่มต้น (ใช้สำหรับ Login)
        API: POST {{baseUrl}}/auth/login
        """
        print("--- Attempting Login ---")
        # ใช้ Path /auth/login และกำหนด name เพื่อให้รายงานใน Locust UI ชัดเจน
        response = self.client.post(
            "/auth/login",
            json=USER_CREDENTIALS,
            name="/auth/login"
        )
        
        if response.status_code == 200:
            print("Login successful! Session started.")
            # Cookie (Session Token) จะถูกเก็บโดย Locust Client โดยอัตโนมัติ
        else:
            print(f"Login failed! Status: {response.status_code}. Stopping user.")
            # ถ้า Login ไม่สำเร็จ ให้หยุดการทำงานของ User นี้
            self.environment.runner.quit() 


    # ------------------ Task หลักของ User (หลัง Login) ------------------

    @task(3)
    def verify_session(self):
        """
        Task: ตรวจสอบสถานะ Session
        API: GET {{baseUrl}}/auth/verify
        """
        # ตั้งค่า name ให้เป็น Path เต็ม เพื่อให้รายงานถูกต้อง
        self.client.get("/auth/verify", name="/auth/verify")


    @task(5)
    def get_library_song_list(self):
        """
        Task: ดึงรายการเพลงจาก Library (จำลองกิจกรรมหลัก)
        API: GET {{baseUrl}}/library/song/list
        """
        # (5) คือ Weight: Task นี้จะถูกเรียกบ่อยกว่า Task อื่นๆ 5 เท่า
        self.client.get("/library/song/list", name="/library/song/list")


    @task(2)
    def get_user_organization(self):
        """
        Task: ดึงข้อมูลองค์กรของผู้ใช้
        API: GET {{baseUrl}}/user/organization
        """
        self.client.get("/user/organization", name="/user/organization")

    
    @task(1)
    def check_email_existence(self):
        """
        Task: ตรวจสอบว่า Email มีในระบบหรือไม่ (เป็น Task ที่เบา)
        API: POST {{baseUrl}}/auth/check-email
        """
        data = {"email": USER_CREDENTIALS["username"]} # ใช้ username เป็น email ในตัวอย่าง
        self.client.post("/auth/check-email", json=data, name="/auth/check-email")