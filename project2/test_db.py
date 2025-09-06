import sqlite3

# Подключаемся к базе
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

# Проверяем, какие таблицы есть
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Таблицы в базе:")
for table in tables:
    print("-", table[0])

# Добавим тестовую запись
cursor.execute('''
    INSERT INTO messages (user_id, username, message_type, user_input, ai_response, timestamp)
    VALUES (999, 'test', 'text', 'Тест из Python', 'OK', '2025-04-05 15:00:00')
''')
conn.commit()  # 👈 БЕЗ ЭТОГО ЗАПИСЬ НЕ СОХРАНИТСЯ!

print("✅ Тестовая запись добавлена.")

# Посмотрим записи
cursor.execute("SELECT * FROM messages;")
rows = cursor.fetchall()
print("\nСодержимое таблицы messages:")
for row in rows:
    print(row)

conn.close()
