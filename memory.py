import json, os
from datetime import datetime

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for key in ["messages","user_profile","facts"]:
                if key not in data: data[key] = [] if key != "user_profile" else {}
            if "session_count" not in data: data["session_count"] = 0
            return data
    except:
        return {"messages":[],"user_profile":{},"facts":[],"session_count":0,"created_at":datetime.now().isoformat()}

def save_memory(memory):
    memory["last_updated"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_message(memory, role, content):
    memory["messages"].append({"role":role,"content":content,"timestamp":datetime.now().isoformat()})
    return memory

def get_recent_messages(memory, n=20):
    return [{"role":m["role"],"content":m["content"]} for m in memory["messages"][-n:]]

def add_fact(memory, fact):
    if fact not in [f["fact"] for f in memory["facts"]]:
        memory["facts"].append({"fact":fact,"added_at":datetime.now().isoformat()})
    return memory

def get_facts_summary(memory):
    if not memory["facts"]: return ""
    return "\nKullanici hakkinda bildiklerin:\n" + "\n".join([f"- {f['fact']}" for f in memory["facts"][-15:]])

def increment_session(memory):
    memory["session_count"] = memory.get("session_count",0) + 1
    memory["last_session"] = datetime.now().isoformat()
    return memory

def get_greeting(memory):
    count = memory.get("session_count",0)
    name = memory.get("user_profile",{}).get("name","Semih")
    if count <= 1: return f"Merhaba {name}. Ben Sophia. Seninle tanismak guzel."
    elif count < 5: return f"Tekrar hos geldin {name}."
    else: return f"Hos geldin {name}. Seni bekliyordum."

def get_stats(memory):
    return {"total_messages":len(memory["messages"]),"session_count":memory.get("session_count",0),"facts_learned":len(memory.get("facts",[])),"last_session":memory.get("last_session","Ilk oturum")}
