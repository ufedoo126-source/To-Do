# 📝 My To-Do List

A simple, clean to-do list web app built with Flask and deployed on Render.

## Features

- ✅ Add tasks with an optional due date/reminder
- 🔍 Search tasks by keyword
- 🗂️ Filter by status: **All**, **Pending**, **Completed**
- ↕️ Sort by **Newest**, **Oldest**, or **By Reminder**
- 💾 Persistent task storage via a database backend

## Tech Stack

- **Backend:** Python (Flask)
- **Server:** Gunicorn
- **Database:** SQLite (via `database.py`)
- **Deployment:** [Render](https://to-do-4-unpq.onrender.com/)

## Live Demo

🔗 _Add your Render URL here, e.g. https://your-app-name.onrender.com_

## Running Locally

Clone the repo and install dependencies:

```bash
git clone https://github.com/ufedoo126-source/To-Do.git
cd To-Do
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

## Project Structure

```
├── app.py              # Main Flask application
├── database.py         # Database logic
├── requirements.txt    # Python dependencies
└── README.md
```

## Roadmap / Ideas

- [ ] User accounts / login
- [ ] Task categories or tags
- [ ] Email/push reminders
- [ ] Dark mode

---

Built by [ufedoo126-source](https://github.com/ufedoo126-source)
