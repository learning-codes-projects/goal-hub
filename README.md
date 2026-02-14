# 🐍 DJANGO STARTER APP

## 🚀 Launch project

Run `setup.sh` to start the project:

- Make it executable:
  - `sudo chmod 777 ./setup.sh`
- Run it in a **separate terminal** (do **not** use the VS Code integrated terminal):
  - `./setup.sh`

> ✅ Tip: Keep this terminal running while you work.

---

# 🗄️ Using SQLite in Visual Studio Code (VS Code)

This guide shows how to **open a SQLite database** (`.db`, `.sqlite`, `.sqlite3`, Django’s `db.sqlite3`) and **run queries** directly in VS Code.

---

## ✅ Recommended: “SQLite” extension (alexcvzz)

### 1) 📦 Install
1. Open **VS Code**
2. Go to **Extensions**  
   - macOS: `Cmd + Shift + X`  
   - Win/Linux: `Ctrl + Shift + X`
3. Search for: **SQLite**
4. Install: **SQLite** *(by alexcvzz)*

> ⚠️ There are multiple “SQLite” extensions. Choose the one that includes commands like **Open Database** and **Run Query**.

---

## 2) 🔓 Open your database
1. Open the Command Palette:  
   - macOS: `Cmd + Shift + P`  
   - Win/Linux: `Ctrl + Shift + P`
2. Run: **SQLite: Open Database**
3. Select your database file:
   - ✅ Django default: `db.sqlite3`
   - Other: `my_database.sqlite3`

Once opened, you should see a database explorer/tree with:
- 📁 tables
- 👁️ views
- 🧱 indexes
- ▶️ query execution + results panel

---

## 3) ▶️ Run queries

### Method A: Using a `.sql` file (recommended)
1. Create a file like: `queries.sql`
2. Write your query:

```sql
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;