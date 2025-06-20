from flask import Flask, render_template
from trello_integration import TrelloIntegration
from google_calendar import GoogleCalendar
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ฟังก์ชันสำหรับจัดรูปแบบวันที่
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    """จัดรูปแบบวันที่สำหรับ Jinja2 template"""
    if not value:
        return ""
    try:
        if isinstance(value, str):
            if 'T' in value:  # ISO format with time
                dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
                return dt.strftime(format)
            else:  # Date only
                dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime('%d/%m/%Y')
        elif isinstance(value, dict):
            # กรณีข้อมูลจาก Google Calendar ที่มีทั้ง date และ dateTime
            if 'dateTime' in value:
                dt = datetime.strptime(value['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
                return dt.strftime(format)
            elif 'date' in value:
                dt = datetime.strptime(value['date'], '%Y-%m-%d')
                return dt.strftime('%d/%m/%Y')
        return value
    except ValueError as e:
        print(f"Date formatting error: {e}")
        return "Invalid date"

# โหลดค่าจากไฟล์ .env
load_dotenv()

app = Flask(__name__)
app.jinja_env.filters['format_datetime'] = format_datetime

@app.route('/')
def show_combined_data():
    """Route หลักสำหรับแสดงข้อมูลรวมจาก Trello และ Google Calendar"""
    try:
        # ดึงข้อมูลจาก Trello
        trello_data = {
            'board_name': 'Trello Board',
            'lists': []
        }
        
        try:
            trello = TrelloIntegration()
            boards = trello.get_boards()
            
            if boards:
                board = boards[0]
                trello_data['board_name'] = board['name']
                lists = trello.get_lists(board['id'])
                
                for lst in lists:
                    cards = trello.get_cards(lst['id'])
                    formatted_cards = []
                    for card in cards:
                        formatted_card = {
                            'id': card['id'],
                            'name': card['name'],
                            'desc': card.get('desc', ''),
                            'due': card.get('due', ''),
                            'url': card.get('url', '#')
                        }
                        formatted_cards.append(formatted_card)
                    
                    trello_data['lists'].append({
                        'id': lst['id'],
                        'name': lst['name'],
                        'cards': formatted_cards
                    })
        except Exception as trello_error:
            print(f"Trello Error: {trello_error}")
            trello_data['error'] = "Unable to connect to Trello service"

        # ดึงข้อมูลจาก Google Calendar
        calendar_events = []
        try:
            calendar = GoogleCalendar()
            events = calendar.get_upcoming_events(10)  # ดึง 10 เหตุการณ์ล่าสุด
            
            # ตรวจสอบว่า events เป็น list หรือ dictionary ที่มี error
            if isinstance(events, list):
                for event in events:
                    start = event.get('start', {})
                    end = event.get('end', {})
                    
                    # จัดการ organizer
                    organizer = event.get('organizer', {})
                    if isinstance(organizer, dict):
                        organizer_email = organizer.get('email', 'Unknown')
                        organizer_name = organizer_email.split('@')[0].replace('.', ' ').title()
                    else:
                        organizer_name = 'Unknown'
                    
                    calendar_events.append({
                        'id': event.get('id', ''),
                        'summary': event.get('summary', 'Untitled Event'),
                        'start': start,
                        'end': end,
                        'description': event.get('description', ''),
                        'location': event.get('location', 'No location specified'),
                        'organizer': organizer_name
                    })
            elif isinstance(events, dict) and 'error' in events:
                calendar_events = {'error': events['error']}
                
        except Exception as calendar_error:
            print(f"Calendar Error: {calendar_error}")
            calendar_events = {'error': str(calendar_error)}

        return render_template('index.html',
                           trello_data=trello_data,
                           calendar_events=calendar_events)
    
    except Exception as e:
        print(f"Application Error: {e}")
        return render_template('index.html',
                           trello_data={'error': 'System error'},
                           calendar_events={'error': 'System error'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)