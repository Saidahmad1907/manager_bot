import csv
from database import load_data

def export_activity_csv(filename="activity_export.csv"):
    data = load_data()
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Turi", "Admin ID", "Manager ID", "Matn", "Vaqt", "Qo‘shimcha"])
        for i in data.get('issues', []):
            writer.writerow(["Muammo", i['admin_id'], i.get('manager_id', ''), i['text'], i['timestamp'], i.get('status', '')])
        for c in data.get('complaints', []):
            writer.writerow(["Shikoyat", c['admin_id'], '', c['text'], '', ''])
        for p in data.get('penalties', []):
            writer.writerow(["Jarima", p['admin_id'], p.get('manager_id', ''), p['reason'], p['timestamp'], ''])
        for w in data.get('warnings', []):
            writer.writerow(["Ogohlantirish", w['admin_id'], '', w['text'], w['timestamp'], ''])
    return filename
