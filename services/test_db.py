from database.models import init_db
from database.db_service import insert_record, query_records, get_summary

init_db()

insert_record("weather_logs", {
    "city": "Chennai",
    "temperature": 34,
    "condition": "Sunny"
})

insert_record("file_logs", {
    "filename": "notes.txt",
    "action": "read"
})

insert_record("reports", {
    "report_name": "weekly_weather",
    "content": "Average temp was 32C"
})

print("\n🌦 Weather Logs:")
print(query_records("weather_logs"))

print("\n📂 File Logs:")
print(query_records("file_logs"))

print("\n📊 Reports:")
print(query_records("reports"))

print("\n📈 Summary:")
print(get_summary("weather_logs"))
