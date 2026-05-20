import requests, os, json
from datetime import datetime

DAYS_TR = ["Pazartesi","Sali","Carsamba","Persembe","Cuma","Cumartesi","Pazar"]
MONTHS_TR = ["","Ocak","Subat","Mart","Nisan","Mayis","Haziran","Temmuz","Agustos","Eylul","Ekim","Kasim","Aralik"]

def get_current_time():
    now = datetime.now()
    day = DAYS_TR[now.weekday()]
    month = MONTHS_TR[now.month]
    return {"time":now.strftime("%H:%M"),"date":f"{day}, {now.day} {month} {now.year}","text":f"Su an saat {now.strftime('%H:%M')}, {day}, {now.day} {month} {now.year}."}

def get_weather(city="Izmir"):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key: return {"success":False,"text":"Hava durumu API anahtari yok.","data":None}
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",params={"q":city,"appid":api_key,"units":"metric","lang":"tr"},timeout=5)
        d = r.json()
        if r.status_code == 200:
            temp=round(d["main"]["temp"]); desc=d["weather"][0]["description"]
            return {"success":True,"text":f"{city}: {temp}C, {desc}","data":{"temp":temp,"description":desc,"city":city}}
        return {"success":False,"text":"Hava durumu alinamadi.","data":None}
    except:
        return {"success":False,"text":"Hava servisi erisилемиyor.","data":None}

def get_calendar_events():
    today = datetime.now().date()
    try:
        with open("calendar.json","r",encoding="utf-8") as f: events = json.load(f)
    except: events = []
    upcoming = []
    for e in events:
        try:
            ed = datetime.strptime(e["date"],"%Y-%m-%d").date()
            diff = (ed - today).days
            if 0 <= diff <= 7: upcoming.append({**e,"days_away":diff,"label":"Bugun" if diff==0 else f"{diff} gun sonra"})
        except: pass
    return upcoming

def add_calendar_event(title, date_str, note=""):
    try:
        with open("calendar.json","r",encoding="utf-8") as f: events = json.load(f)
    except: events = []
    try: datetime.strptime(date_str,"%Y-%m-%d")
    except: return {"success":False,"message":"Tarih formati yanlis."}
    events.append({"title":title,"date":date_str,"note":note,"created_at":datetime.now().isoformat()})
    with open("calendar.json","w",encoding="utf-8") as f: json.dump(events,f,ensure_ascii=False,indent=2)
    return {"success":True,"message":f"'{title}' takvime eklendi."}

def format_calendar_for_sophia(events):
    if not events: return "Onumüzdeki 7 gunde planlanmis etkinlik yok."
    return "Yaklasan etkinliklerin:\n" + "\n".join([f"- {e['label']}: {e['title']}" for e in events])

def detect_intent(text):
    t = text.lower()
    if any(k in t for k in ["hava","sicaklik","yagmur"]): return "weather"
    if any(k in t for k in ["saat kac","saat","tarih","bugun ne","hangi gun"]): return "time"
    if any(k in t for k in ["takvim","etkinlik","randevu","plan"]): return "calendar"
    return "chat"

def build_context_injection(text, city="Izmir"):
    intent = detect_intent(text)
    parts = []
    if intent in ["time","chat"]:
        parts.append(f"[Sistem: {get_current_time()['text']}]")
    if intent == "weather":
        parts.append(f"[Sistem: {get_weather(city)['text']}]")
    if intent == "calendar":
        events = get_calendar_events()
        parts.append(f"[Sistem: {format_calendar_for_sophia(events)}]")
    return "\n".join(parts)
