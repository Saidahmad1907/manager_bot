import os

def _parse_ids(env_value: str):
	try:
		return [int(x.strip()) for x in env_value.split(',') if x.strip()]
	except Exception:
		return []

# Prefer environment variables on servers; fallback is placeholder (do not commit real token)
TOKEN = os.getenv("BOT_TOKEN", "CHANGE_ME")

_mgr_env = os.getenv("MANAGER_IDS")
MANAGER_IDS = _parse_ids(_mgr_env) if _mgr_env else [5948727144]

_adm_env = os.getenv("ADMIN_IDS")
ADMIN_IDS = _parse_ids(_adm_env) if _adm_env else [5904612316]

# Note: in production, set BOT_TOKEN and MANAGER_IDS via environment (systemd env file)
