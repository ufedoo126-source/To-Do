from flask import Flask, request, redirect
from datetime import datetime
from database import init_db, get_connection

app = Flask(__name__)
init_db()  # creates tasks.db and the table, if they don't exist yet

@app.route("/", methods=["GET", "POST"])
def home():
    message = request.args.get("msg", "")
    conn = get_connection()

    if request.method == "POST":
        new_task = request.form.get("task")
        reminder_time = request.form.get("reminder")
        if new_task:
            conn.execute(
                "INSERT INTO tasks (text, reminder, completed, created) VALUES (?, ?, 0, ?)",
                (new_task, reminder_time, datetime.now().isoformat())
            )
            conn.commit()
        conn.close()
        return redirect("/?msg=Task added successfully")

    search_query = request.args.get("search", "").lower()
    status_filter = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "newest")

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search_query:
        query += " AND LOWER(text) LIKE ?"
        params.append(f"%{search_query}%")
    if status_filter == "completed":
        query += " AND completed = 1"
    elif status_filter == "pending":
        query += " AND completed = 0"

    if sort_by == "newest":
        query += " ORDER BY created DESC"
    elif sort_by == "oldest":
        query += " ORDER BY created ASC"
    elif sort_by == "reminder":
        query += " ORDER BY reminder ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    now = datetime.now()
    task_list_html = ""

    for task in rows:
        is_overdue = False
        if task["reminder"] and not task["completed"]:
            try:
                reminder_dt = datetime.strptime(task["reminder"], "%Y-%m-%dT%H:%M")
                if reminder_dt < now:
                    is_overdue = True
            except ValueError:
                pass

        reminder_display = f"⏰ {task['reminder']}" if task["reminder"] else ""
        text_style = "text-decoration: line-through; color: #999;" if task["completed"] else ""
        li_style = "border-left: 5px solid #e74c3c;" if is_overdue else "border-left: 5px solid transparent;"

        task_list_html += f"""
        <li style="{li_style}">
            <div style="display:flex; align-items:center; gap:12px;">
                <form method="POST" action="/toggle/{task['id']}" style="display:inline">
                    <input type="checkbox" class="task-check" onchange="this.form.submit()" {"checked" if task["completed"] else ""}>
                </form>
                <div>
                    <strong style="{text_style}">{task['text']}</strong>
                    <div style="font-size: 0.85em; color: #888;">{reminder_display} {"⚠️ Overdue" if is_overdue else ""}</div>
                </div>
            </div>
            <div style="display:flex; gap:6px;">
                <a href="/edit/{task['id']}"><button type="button" class="icon-btn">✏️</button></a>
                <form method="POST" action="/delete/{task['id']}" style="display:inline">
                    <button type="submit" class="icon-btn">🗑️</button>
                </form>
            </div>
        </li>
        """

    if not rows:
        task_list_html = '<div class="empty-state">📝 No tasks yet — click above to add one!</div>'

    def sort_link(value, label):
        active = "active" if sort_by == value else ""
        return f'<a href="/?filter={status_filter}&search={search_query}&sort={value}" class="{active}">{label}</a>'

    def filter_link(value, label):
        active = "active" if status_filter == value else ""
        return f'<a href="/?filter={value}&search={search_query}&sort={sort_by}" class="{active}">{label}</a>'

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 50px auto;
                    background: linear-gradient(135deg, #f0f4f8, #e2e8f0); padding: 25px; }}
            .card {{ background: white; padding: 25px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); }}
            h1 {{ color: #2d3748; font-size: 1.6em; margin-top: 0; }}
            .message {{ background: #d1fae5; color: #065f46; padding: 10px 14px; border-radius: 8px;
                        margin-bottom: 15px; font-size: 0.9em; }}
            form.main-form {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }}
            input[type=text], input[type=datetime-local] {{ flex: 1; padding: 10px; min-width: 120px;
                border: 1px solid #cbd5e0; border-radius: 8px; }}
            button {{ padding: 10px 16px; background: #6366f1; color: white; border: none;
                      border-radius: 8px; cursor: pointer; font-weight: 600; }}
            button:hover {{ background: #4f46e5; }}
            .icon-btn {{ background: #f1f5f9; font-size: 1.1em; padding: 8px 10px; border-radius: 8px; }}
            .icon-btn:hover {{ background: #e2e8f0; }}
            li {{ background: #fafafa; padding: 14px; margin-bottom: 10px; border-radius: 10px;
                  display: flex; justify-content: space-between; align-items: center; list-style: none;
                  box-shadow: 0 2px 6px rgba(0,0,0,0.04); }}
            .task-check {{ width: 18px; height: 18px; }}
            .filters, .sorting {{ display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }}
            .filters a, .sorting a {{ text-decoration: none; padding: 6px 14px; background: #edf2f7;
                border-radius: 20px; color: #4a5568; font-size: 0.85em; }}
            .filters a.active, .sorting a.active {{ background: #6366f1; color: white; }}
            .empty-state {{ text-align: center; color: #a0aec0; padding: 30px 10px; font-size: 0.95em; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📋 My To-Do List</h1>
            {f'<div class="message">✅ {message}</div>' if message else ''}
            <form method="POST" class="main-form">
                <input type="text" name="task" placeholder="Enter a task">
                <input type="datetime-local" name="reminder">
                <button type="submit">Add</button>
            </form>
            <form method="GET" class="main-form">
                <input type="text" name="search" placeholder="Search tasks..." value="{search_query}">
                <input type="hidden" name="filter" value="{status_filter}">
                <input type="hidden" name="sort" value="{sort_by}">
                <button type="submit">🔍</button>
            </form>
            <div class="filters">
                {filter_link("all", "All")}
                {filter_link("pending", "Pending")}
                {filter_link("completed", "Completed")}
            </div>
            <div class="sorting">
                {sort_link("newest", "Newest")}
                {sort_link("oldest", "Oldest")}
                {sort_link("reminder", "By Reminder")}
            </div>
            <ul style="padding: 0;">{task_list_html}</ul>
        </div>
    </body>
    </html>
    """

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    conn = get_connection()
    task = conn.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task:
        new_status = 0 if task["completed"] else 1
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        msg = "Task marked complete" if new_status else "Task marked pending"
    conn.close()
    return redirect(f"/?msg={msg}")

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    conn = get_connection()

    if request.method == "POST":
        text = request.form.get("task")
        reminder = request.form.get("reminder")
        conn.execute("UPDATE tasks SET text = ?, reminder = ? WHERE id = ?", (text, reminder, task_id))
        conn.commit()
        conn.close()
        return redirect("/?msg=Task updated successfully")

    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    if not task:
        return redirect("/")

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 500px; margin: 50px auto;
                    background: #e2e8f0; padding: 25px; }}
            .card {{ background: white; padding: 25px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); }}
            form {{ display: flex; flex-direction: column; gap: 12px; }}
            input {{ padding: 10px; border: 1px solid #cbd5e0; border-radius: 8px; }}
            button {{ padding: 10px; background: #6366f1; color: white; border: none;
                      border-radius: 8px; cursor: pointer; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>✏️ Edit Task</h1>
            <form method="POST">
                <input type="text" name="task" value="{task['text']}">
                <input type="datetime-local" name="reminder" value="{task['reminder']}">
                <button type="submit">Save</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/?msg=Task deleted successfully")

if __name__ == "__main__":
    app.run(debug=True)