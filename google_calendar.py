import requests
import os
from datetime import datetime, timezone
import json

class GoogleCalendar:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_CALENDAR_API_KEY")
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        

        if not self.api_key or not self.calendar_id:
            raise ValueError("Google Calendar API key or Calendar ID not found in environment variables")
            
        self.base_url = f"https://www.googleapis.com/calendar/v3/calendars/{self.calendar_id}/events"
        print(f"Initialized Google Calendar with ID: {self.calendar_id}")  # Debug

    def get_upcoming_events(self, max_results=5):
        """ดึงเหตุการณ์ที่กำลังจะมาถึงจาก Google Calendar"""
        if not self.api_key:
            return {"error": "Google Calendar API key not configured"}

        params = {
            "key": self.api_key,
            "singleEvents": True,
            "orderBy": "startTime",
            "maxResults": max_results,
            "timeMin": self._get_now_rfc3339(),
            "timeZone": "Asia/Bangkok"  # ระบุ timezone
        }

        try:
            print(f"Requesting calendar events from: {self.base_url}")  # Debug
            print(f"Request parameters: {json.dumps(params, indent=2)}")  # Debug
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print("Raw API response:", json.dumps(data, indent=2))  # Debug
            
            if 'items' not in data:
                print("No 'items' key in response, may be empty calendar")
                return []
                
            return data.get("items", [])
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f"\nResponse status: {e.response.status_code}\nResponse text: {e.response.text[:200]}"
            print(error_msg)  # Debug
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)  # Debug
            return {"error": error_msg}

    def _get_now_rfc3339(self):
        """สร้าง timestamp ปัจจุบันในรูปแบบ RFC3339"""
        now = datetime.now(timezone.utc)
        return now.isoformat().replace("+00:00", "Z")

# ตัวอย่างการใช้งาน (สำหรับทดสอบ)
if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    
    try:
        calendar = GoogleCalendar()
        print("\nTesting Google Calendar integration...")
        events = calendar.get_upcoming_events(3)
        
        if isinstance(events, dict) and 'error' in events:
            print(f"\nError: {events['error']}")
        else:
            print(f"\nFound {len(events)} events:")
            for i, event in enumerate(events, 1):
                print(f"\nEvent {i}:")
                print(f"  Title: {event.get('summary', 'No title')}")
                print(f"  Start: {event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'N/A'))}")
                print(f"  Organizer: {event.get('organizer', {}).get('displayName', 'N/A')}")
                
    except Exception as e:
        print(f"Initialization error: {str(e)}")