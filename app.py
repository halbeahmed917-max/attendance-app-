from flask import Flask, render_template_string, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)

# انشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY, name TEXT, fingerprint_id TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY, employee_id INTEGER, timestamp TEXT,
                  FOREIGN KEY(employee_id) REFERENCES employees(id))''')
    conn.commit()
    conn.close()

init_db()

HTML_HOME = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><title>نظام الحضور</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial; text-align:center; padding:50px; background:#f0f0f0;}
a{display:block; margin:20px; padding:15px; background:#4CAF50; color:white; 
text-decoration:none; border-radius:10px; font-size:20px;}
</style>
</head>
<body>
<h1>نظام حضور الطلاب بالبصمة</h1>
<a href="/register">1. تسجيل موظف جديد</a>
<a href="/checkin">2. تسجيل الحضور بالبصمة</a>
</body></html>
"""

HTML_REGISTER = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><title>تسجيل موظف</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial; padding:20px; background:#f0f0f0;}
input, button{width:100%; padding:12px; margin:10px 0; border-radius:5px; border:1px solid #ccc;}
button{background:#4CAF50; color:white; border:none;}
</style>
</head>
<body>
<h2>تسجيل موظف جديد</h2>
<form method="POST">
<input type="text" name="name" placeholder="اسم الموظف" required>
<input type="text" name="fingerprint_id" placeholder="رقم البصمة" required>
<button type="submit">تسجيل</button>
</form>
<a href="/">العودة للرئيسية</a>
</body></html>
"""

HTML_CHECKIN = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><title>تسجيل الحضور</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial; padding:20px; background:#f0f0f0; text-align:center;}
input, button{width:80%; padding:15px; margin:10px 0; border-radius:5px; border:1px solid #ccc; font-size:18px;}
button{background:#2196F3; color:white; border:none;}
#result{margin-top:20px; font-size:20px; font-weight:bold;}
</style>
</head>
<body>
<h2>تسجيل الحضور بالبصمة</h2>
<input type="text" id="fingerprint" placeholder="ضع اصبعك على الجهاز">
<button onclick="checkin()">تسجيل حضور</button>
<div id="result"></div>
<a href="/">العودة للرئيسية</a>
<script>
function checkin(){
  let fid = document.getElementById('fingerprint').value;
  fetch('/api/checkin', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({fingerprint_id: fid})
  }).then(r=>r.json()).then(data=>{
    document.getElementById('result').innerHTML = data.message;
    document.getElementById('result').style.color = data.status == 'success'? 'green' : 'red';
  });
}
</script>
</body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_HOME)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        fid = request.form['fingerprint_id']
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO employees (name, fingerprint_id) VALUES (?,?)", (name, fid))
            conn.commit()
            msg = f"تم تسجيل {name} بنجاح"
        except:
            msg = "رقم البصمة مستخدم من قبل"
        conn.close()
        return msg + '<br><a href="/register">تسجيل اخر</a>'
    return render_template_string(HTML_REGISTER)

@app.route('/checkin')
def checkin_page():
    return render_template_string(HTML_CHECKIN)

@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    data = request.json
    fid = data['fingerprint_id']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM employees WHERE fingerprint_id=?", (fid,))
    emp = c.fetchone()
    if emp:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO attendance (employee_id, timestamp) VALUES (?,?)", (emp[0], time))
        conn.commit()
        conn.close()
        return jsonify({"status":"success", "message":f"مرحبا {emp[1]} - تم تسجيل حضورك الساعة {time}"})
    conn.close()
    return jsonify({"status":"error", "message":"البصمة غير مسجلة"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)