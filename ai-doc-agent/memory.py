import sqlite3

def save_interaction(question, answer):
    conn = sqlite3.connect("history.db")
    conn.execute("INSERT INTO log (q, a) VALUES (?, ?)", (question, answer))
    conn.commit()