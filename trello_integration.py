import os
import requests

class TrelloIntegration:
    def __init__(self, api_key=None, api_token=None):
        """เริ่มต้นการเชื่อมต่อกับ Trello API"""
        # รับค่าจากตัวแปรสภาพแวดล้อมหากไม่ระบุตรงๆ
        self.api_key = api_key or os.getenv('TRELLO_API_KEY')
        self.api_token = api_token or os.getenv('TRELLO_API_TOKEN')
        
        if not self.api_key or not self.api_token:
            raise ValueError("จำเป็นต้องมี API Key และ Token")
        
        self.base_url = "https://api.trello.com/1"
    
    def get_boards(self):
        """ดึงข้อมูลบอร์ดทั้งหมดจาก Trello"""
        try:
            url = f"{self.base_url}/members/me/boards"
            params = {
                'key': self.api_key,
                'token': self.api_token,
                'fields': 'name,id,url'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            print(f"[Trello] ดึงข้อมูลบอร์ดสำเร็จ>>>>>>>>>>>: {(response.json())} บอร์ด")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[Trello Error] เกิดข้อผิดพลาดขณะดึงบอร์ด: {e}")
            return []
    
    def get_lists(self, board_id):
        """ดึงรายการทั้งหมดในบอร์ด"""
        try:
            url = f"{self.base_url}/boards/{board_id}/lists"
            params = {
                'key': self.api_key,
                'token': self.api_token,
                'fields': 'name,id'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[Trello Error] เกิดข้อผิดพลาดขณะดึงรายการ: {e}")
            return []
    
    def get_cards(self, list_id):
        """ดึงการ์ดทั้งหมดในรายการ"""
        try:
            url = f"{self.base_url}/lists/{list_id}/cards"
            params = {
                'key': self.api_key,
                'token': self.api_token,
                'fields': 'name,desc,due,url',
                'members': 'true'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # จัดรูปแบบข้อมูลให้อ่านง่าย
            cards = response.json()
            for card in cards:
                card['short_desc'] = (card['desc'][:50] + '...') if card.get('desc') else 'ไม่มีคำอธิบาย'
                card['due_date'] = card['due'][:10] if card.get('due') else 'ไม่มีกำหนดส่ง'
            
            return cards
        except requests.exceptions.RequestException as e:
            print(f"[Trello Error] เกิดข้อผิดพลาดขณะดึงการ์ด: {e}")
            return []