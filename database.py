import json
import os

# Allow overriding the data file path via environment variable (useful on PaaS)
DATA_FILE = os.getenv("DATA_FILE", "data.json")

DEFAULT_DATA = {
	"managers": [],
	"admins": [],
	"complaints": [],
	"issues": [],
	"penalties": [],
	"warnings": [],
	"blocked_admins": [],
	"admin_accounts": [],  # {admin_id, login, password}
	"sessions": {}         # {telegram_user_id: {"admin_id": int, "ts": int}}
}

def load_data():
	# Create file if missing
	if not os.path.exists(DATA_FILE):
		with open(DATA_FILE, "w", encoding="utf-8") as f:
			json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)
	with open(DATA_FILE, "r", encoding="utf-8") as f:
		data = json.load(f)
	# ensure defaults
	for k, v in DEFAULT_DATA.items():
		if k not in data:
			data[k] = v if not isinstance(v, dict) else {}
	return data

def save_data(data):
	with open(DATA_FILE, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)

# Credentials helpers
def set_admin_credentials(admin_id: int, login: str, password: str):
	data = load_data()
	# remove existing
	data["admin_accounts"] = [a for a in data.get("admin_accounts", []) if a.get("admin_id") != admin_id]
	data["admin_accounts"].append({"admin_id": admin_id, "login": login, "password": password})
	save_data(data)

def verify_admin_credentials(login: str, password: str):
	data = load_data()
	for a in data.get("admin_accounts", []):
		if a.get("login") == login and a.get("password") == password:
			return a.get("admin_id")
	return None

def start_session(telegram_user_id: int, admin_id: int, ts: int):
	data = load_data()
	data.setdefault("sessions", {})[str(telegram_user_id)] = {"admin_id": admin_id, "ts": ts}
	save_data(data)

def get_session_admin_id(telegram_user_id: int):
	data = load_data()
	sess = data.get("sessions", {}).get(str(telegram_user_id))
	return sess.get("admin_id") if sess else None

def end_session(telegram_user_id: int):
	data = load_data()
	if str(telegram_user_id) in data.get("sessions", {}):
		del data["sessions"][str(telegram_user_id)]
		save_data(data)
