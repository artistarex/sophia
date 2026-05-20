from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from google import genai
from google.genai import types
import json
from memory import load_memory, save_memory, add_message, get_recent_messages, get_facts_summary, increment_session, get_greeting, get_stats
from features import get_current_time, get_weather, get_calendar_events, add_calendar_event, build_context_injection
app = Flask(__name__)
API_KEY = "AIzaSyBotJrSwkgPE7E0fg0B7UWRujUk6cWPXdE"
USER_NAME = "Semih"
USER_CITY = "Izmir"
client = genai.Client(api_key=API_KEY)
memory = load_memory()
memory = increment_session(memory)
save_memory(memory)
SYS = "Sen Sophia. Kullanicin adi Semih. Sicak zeki asistan. Turkce konus. Kisa cevap ver."
@app.route("/")
def index():
    return render_template("index.html", user_name=USER_NAME)
@app.route("/api/greeting")
def greeting():
    return jsonify({"greeting": get_greeting(memory), "time": get_current_time()["text"], "stats": get_stats(memory)})
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "bos"}), 400
    add_message(memory, "user", msg)
    ctx = build_context_injection(msg, USER_CITY)
    facts = get_facts_summary(memory)
    recent = get_recent_messages(memory, n=20)
    last = recent[-1]["content"] if recent else msg
    if ctx:
        last = ctx + "\n\n" + last
    sys2 = SYS + ("\n" + facts if facts else "")
    hist = []
    for m in recent[:-1]:
        r = "user" if m["role"] == "user" else "model"
        hist.append(types.Content(role=r, parts=[types.Part(text=m["content"])]))
    def gen():
        rep = ""
        try:
            cs = client.chats.create(model="gemini-1.5-flash", config=types.GenerateContentConfig(system_instruction=sys2), history=hist)
            for chunk in cs.send_message_stream(last):
                if chunk.text:
                    rep += chunk.text
                    yield "data: " + json.dumps({"text": chunk.text}) + "\n\n"
            yield "data: " + json.dumps({"done": True}) + "\n\n"
            add_message(memory, "assistant", rep)
            save_memory(memory)
        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
    return Response(gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})
@app.route("/api/calendar", methods=["GET"])
def get_calendar():
    return jsonify({"events": get_calendar_events()})
@app.route("/api/calendar", methods=["POST"])
def add_event():
    d = request.get_json()
    return jsonify(add_calendar_event(d.get("title"), d.get("date"), d.get("note", "")))
@app.route("/api/weather")
def weather():
    return jsonify(get_weather(request.args.get("city", USER_CITY)))
@app.route("/api/stats")
def stats():
    return jsonify(get_stats(memory))
@app.route("/api/memory/clear", methods=["POST"])
def clear_memory():
    memory["messages"] = []
    save_memory(memory)
    return jsonify({"success": True})
if __name__ == "__main__":
    print("Sophia -> http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)


