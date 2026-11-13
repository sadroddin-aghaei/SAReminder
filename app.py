"""SAReminder v2 - offline tasks, reminders, calendar (Jalali + Gregorian), Pomodoro, habits, notes.
(c) Sadroddin Aghaei. All Rights Reserved."""
import sys, json, sqlite3, calendar
from datetime import datetime, date, timedelta
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QTime, QProcess, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QKeySequence, QShortcut, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import *

UR = Qt.ItemDataRole.UserRole; AC = Qt.AlignmentFlag.AlignCenter; INFO = QSystemTrayIcon.MessageIcon.Information
DIR = Path.home() / ".sareminder"; DIR.mkdir(exist_ok=True); DB = DIR / "sareminder.db"
FMT = "%Y-%m-%dT%H:%M"; FA = False; JAL = False; H24 = True
S = dict(dash=("Dashboard", "داشبورد"), tasks=("Tasks", "وظایف"), cal=("Calendar", "تقویم"), pomo=("Focus", "تمرکز"),
 habits=("Habits", "عادت‌ها"), notes=("Notes", "یادداشت‌ها"), settings=("Settings", "تنظیمات"), add=("＋ New task", "＋ وظیفه جدید"),
 edit=("Edit", "ویرایش"), dup=("Duplicate", "کپی"), pin=("Star", "ستاره"), delete=("Delete", "حذف"), done=("Done / Undo", "انجام / بازگشت"),
 search=("Search title, tags, notes…", "جستجو در عنوان، برچسب، یادداشت…"), f=(["All", "Today", "Upcoming", "Overdue", "Starred", "Completed"], ["همه", "امروز", "آینده", "عقب‌افتاده", "ستاره‌دار", "انجام‌شده"]),
 pri=(["Low", "Medium", "High", "Urgent"], ["کم", "متوسط", "زیاد", "فوری"]), title=("Title", "عنوان"), nt=("Notes", "توضیحات"), tags=("Tags (comma separated)", "برچسب‌ها (با کاما)"),
 due=("Has due date", "دارای موعد"), rem=("Remind before", "یادآوری قبل از"), now=("At due time", "سر موعد"), mn=("min", "دقیقه"), rep=("Repeat", "تکرار"),
 rp=(["Never", "Daily", "Weekly", "Monthly"], ["هرگز", "روزانه", "هفتگی", "ماهانه"]), today=("Today", "امروز"), over=("Overdue", "عقب‌افتاده"), comp=("Completed", "انجام‌شده"),
 streak=("Day streak", "روز پیاپی"), up=("Upcoming", "پیش‌رو"), prog=("Today's progress", "پیشرفت امروز"), start=("Start", "شروع"), pause=("Pause", "توقف"), reset=("Reset", "بازنشانی"),
 work=("Focus", "تمرکز"), brk=("Break", "استراحت"), sess=("Sessions today", "جلسه‌های امروز"), nh=("＋ New habit", "＋ عادت جدید"), nn=("＋ New note", "＋ یادداشت جدید"),
 lang=("Language", "زبان"), jal=("Jalali (Persian) calendar", "تقویم جلالی (شمسی)"), h24=("24-hour time", "ساعت ۲۴ ساعته"), auto=("Start with Windows", "اجرا همراه ویندوز"),
 exp=("Export JSON backup", "خروجی پشتیبان JSON"), imp=("Import JSON backup", "ورودی پشتیبان JSON"), folder=("Open data folder", "باز کردن پوشه داده"),
 snz=("Snooze 10 min", "۱۰ دقیقه بعد"), cmp=("Complete", "انجام شد"), dis=("Dismiss", "بستن"), empty=("Enter a title.", "عنوان را وارد کنید."), bad=("Invalid date.", "تاریخ نامعتبر است."),
 addday=("＋ Add task on this day", "＋ افزودن وظیفه در این روز"), toggle=("Done today", "انجام امروز"), tray=("Running in the tray.", "در سینی سیستم در حال اجراست."), nodue=("No tasks", "بدون وظیفه"))
JM = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
MN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def L(k): return S[k][1 if FA else 0]
def D(x):
    s = str(x); return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")) if FA else s
def g2j(gy, gm, gd):
    gdm = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]; g2 = gy + 1 if gm > 2 else gy
    days = 355666 + 365 * gy + (g2 + 3) // 4 - (g2 + 99) // 100 + (g2 + 399) // 400 + gd + gdm[gm - 1]
    jy = -1595 + 33 * (days // 12053); days %= 12053; jy += 4 * (days // 1461); days %= 1461
    if days > 365: jy += (days - 1) // 365; days = (days - 1) % 365
    return (jy, 1 + days // 31, 1 + days % 31) if days < 186 else (jy, 7 + (days - 186) // 30, 1 + (days - 186) % 30)
def j2g(jy, jm, jd):
    jy += 1595; days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + jd + ((jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186)
    gy = 400 * (days // 146097); days %= 146097
    if days > 36524:
        days -= 1; gy += 100 * (days // 36524); days %= 36524
        if days >= 365: days += 1
    gy += 4 * (days // 1461); days %= 1461
    if days > 365: gy += (days - 1) // 365; days = (days - 1) % 365
    gd = days + 1; sa = [0, 31, 29 if (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]; gm = 0
    while gm < 13 and gd > sa[gm]: gd -= sa[gm]; gm += 1
    return gy, gm, gd
def to_g(y, m, d): return date(*j2g(y, m, d)) if JAL else date(y, m, d)
def from_g(d): return g2j(d.year, d.month, d.day) if JAL else (d.year, d.month, d.day)
def mlen(y, m):
    if not JAL: return calendar.monthrange(y, m)[1]
    return 31 if m <= 6 else 30 if m <= 11 else (30 if g2j(*j2g(y, 12, 30)) == (y, 12, 30) else 29)
def fdate(d): y, m, dd = from_g(d); return D(f"{y}/{m:02d}/{dd:02d}")
def fdt(iso):
    if not iso: return ""
    d = datetime.strptime(iso, FMT); t = d.strftime("%H:%M" if H24 else "%I:%M %p")
    return f"{fdate(d.date())}  {D(t)}"
def nxt(due, rec):
    d = datetime.strptime(due, FMT)
    if rec == 1: d += timedelta(days=1)
    elif rec == 2: d += timedelta(days=7)
    else: d = d.replace(year=d.year + (d.month == 12), month=d.month % 12 + 1, day=min(d.day, 28))
    return d
def logo():
    p = QPixmap(128, 128); p.fill(Qt.GlobalColor.transparent); q = QPainter(p); q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.setBrush(QColor("#ff3030")); q.setPen(Qt.PenStyle.NoPen); q.drawRoundedRect(4, 4, 120, 120, 30, 30)
    q.setPen(QColor("#000")); q.setFont(QFont("Arial", 50, QFont.Weight.Bold)); q.drawText(p.rect(), AC, "SA"); q.end(); return QIcon(p)
QSS = """*{background:transparent;color:#ececec;font-family:'Segoe UI','Vazirmatn','Tahoma','Geeza Pro',sans-serif;font-size:14px}
QMainWindow,#root,QStackedWidget>QWidget{background:#000}#side{background:#0a0a0a;border:0;border-right:1px solid #1a1a1a;min-width:170px;outline:0;padding:10px}
#side::item{padding:12px 14px;border-radius:12px;margin:2px 0}#side::item:hover{background:#141414}#side::item:selected{background:#1c0a0a;color:#ff4040;font-weight:600}
QListWidget{background:#0a0a0a;border:1px solid #1c1c1c;border-radius:14px;padding:6px;outline:0}QListWidget::item{padding:10px;border-radius:10px;margin:1px 0}
QListWidget::item:selected{background:#161616}QListWidget::item:hover{background:#111}
QLineEdit,QComboBox,QSpinBox,QTimeEdit,QPlainTextEdit,QTextEdit{background:#0a0a0a;border:1px solid #222;border-radius:10px;padding:8px}
QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QPlainTextEdit:focus,QTextEdit:focus{border:1px solid #ff3030}QComboBox QAbstractItemView{background:#0a0a0a;border:1px solid #222;selection-background-color:#1c0a0a}
QPushButton{background:#141414;border:1px solid #222;border-radius:10px;padding:8px 14px}QPushButton:hover{border-color:#ff3030}
QPushButton#primary{background:#ff3030;color:#000;border:0;font-weight:700}QPushButton#primary:hover{background:#ff5555}
#card{background:#0a0a0a;border:1px solid #1c1c1c;border-radius:16px}#big{font-size:30px;font-weight:700}#h1{font-size:24px;font-weight:700}#h2{font-size:17px;font-weight:600}#dim{color:#8a8a8a}
#timer{font-size:72px;font-weight:700;color:#ff3030}QProgressBar{background:#141414;border:0;border-radius:6px;height:10px;text-align:center;color:transparent}QProgressBar::chunk{background:#ff3030;border-radius:6px}
QPushButton#cell{min-height:46px;border-radius:12px;background:#0a0a0a;border:1px solid #181818}QPushButton#cell[today="true"]{border:1px solid #ff3030}
QPushButton#cell[has="true"]{background:#1c0a0a;color:#ff5050;font-weight:700}QPushButton#cell[sel="true"]{background:#ff3030;color:#000;font-weight:700}
#foot{color:#777;font-size:12px;border-top:1px solid #151515;padding:7px}QScrollBar:vertical{background:transparent;width:8px}QScrollBar::handle:vertical{background:#222;border-radius:4px}
QCheckBox::indicator{width:18px;height:18px;border-radius:5px;border:1px solid #333}QCheckBox::indicator:checked{background:#ff3030}"""
SCHEMA = """CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,notes TEXT,priority INTEGER DEFAULT 1,due_at TEXT,
remind_min INTEGER DEFAULT 0,trigger_at TEXT,notified INTEGER DEFAULT 0,done INTEGER DEFAULT 0,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS habit_log(habit_id INTEGER,day TEXT,PRIMARY KEY(habit_id,day));CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,body TEXT,updated TEXT);"""

class TaskDialog(QDialog):
    def __init__(s, parent, row=None, day=None):
        super().__init__(parent); s.setWindowTitle("SAReminder"); s.setMinimumWidth(460); v = QFormLayout(s)
        s.t = QLineEdit(); s.n = QPlainTextEdit(); s.n.setFixedHeight(70); s.tg = QLineEdit(); s.p = QComboBox(); s.p.addItems(S["pri"][int(FA)]); s.p.setCurrentIndex(1)
        s.has = QCheckBox(L("due")); s.y = QSpinBox(); s.y.setRange(1300, 1600) if JAL else s.y.setRange(1900, 2200); s.m = QSpinBox(); s.m.setRange(1, 12); s.d = QSpinBox(); s.d.setRange(1, 31)
        s.tm = QTimeEdit(QTime.currentTime().addSecs(3600)); s.tm.setDisplayFormat("HH:mm" if H24 else "hh:mm AP")
        s.r = QComboBox(); s.r.addItem(L("now"), 0); [s.r.addItem(f"{D(m)} {L('mn')}", m) for m in (5, 15, 30, 60, 120, 1440)]
        s.rp = QComboBox(); s.rp.addItems(S["rp"][int(FA)]); s.pin = QCheckBox(L("pin"))
        row_d = QHBoxLayout(); [row_d.addWidget(w) for w in (s.y, s.m, s.d, s.tm)]
        for k, w in (("title", s.t), ("nt", s.n), ("tags", s.tg)): v.addRow(L(k), w)
        v.addRow("", s.has); v.addRow(L("due"), row_d); v.addRow(L("rem"), s.r); v.addRow(L("rep"), s.rp); v.addRow("", s.pin); v.addRow("", QLabel(""))
        pr = QComboBox(); v.addRow("Priority" if not FA else "اولویت", s.p)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); bb.accepted.connect(s.ok); bb.rejected.connect(s.reject); v.addRow(bb)
        base = datetime.now() + timedelta(hours=1)
        if row:
            s.t.setText(row["title"]); s.n.setPlainText(row["notes"] or ""); s.tg.setText(row["tags"] or ""); s.p.setCurrentIndex(row["priority"]); s.pin.setChecked(bool(row["pinned"]))
            s.rp.setCurrentIndex(row["recur"] or 0); s.r.setCurrentIndex(max(0, s.r.findData(row["remind_min"]))); s.has.setChecked(bool(row["due_at"]))
            if row["due_at"]: base = datetime.strptime(row["due_at"], FMT)
        elif day: base = datetime.combine(day, base.time()); s.has.setChecked(True)
        y, m, d = from_g(base.date()); s.y.setValue(y); s.m.setValue(m); s.d.setValue(d); s.tm.setTime(QTime(base.hour, base.minute))
    def ok(s):
        if not s.t.text().strip(): return QMessageBox.warning(s, "SAReminder", L("empty"))
        if s.has.isChecked():
            try: to_g(s.y.value(), s.m.value(), s.d.value())
            except ValueError: return QMessageBox.warning(s, "SAReminder", L("bad"))
        s.accept()
    def data(s):
        due = trig = None; m = s.r.currentData()
        if s.has.isChecked():
            g = to_g(s.y.value(), s.m.value(), s.d.value()); dt = datetime.combine(g, s.tm.time().toPython()); due = dt.strftime(FMT); trig = (dt - timedelta(minutes=m)).strftime(FMT)
        return dict(title=s.t.text().strip(), notes=s.n.toPlainText(), tags=s.tg.text().strip(), priority=s.p.currentIndex(), due_at=due, remind_min=m, trigger_at=trig, recur=s.rp.currentIndex(), pinned=int(s.pin.isChecked()))

class CalView(QWidget):
    picked = Signal(object)
    def __init__(s):
        super().__init__(); s.marks = set(); s.sel = date.today(); s.cur = from_g(s.sel)[:2]; v = QVBoxLayout(s); h = QHBoxLayout(); v.addLayout(h)
        s.head = QLabel(); s.head.setObjectName("h1"); pv = QPushButton("‹"); nx = QPushButton("›"); td = QPushButton(L("today"))
        pv.clicked.connect(lambda: s.step(-1)); nx.clicked.connect(lambda: s.step(1)); td.clicked.connect(s.go_today)
        h.addWidget(s.head, 1); [h.addWidget(b) for b in (pv, td, nx)]; s.grid = QGridLayout(); v.addLayout(s.grid); s.build()
    def step(s, k):
        y, m = s.cur; m += k; y += (m - 1) // 12; m = (m - 1) % 12 + 1; s.cur = (y, m); s.build()
    def go_today(s): s.sel = date.today(); s.cur = from_g(s.sel)[:2]; s.build(); s.picked.emit(s.sel)
    def build(s):
        while s.grid.count(): s.grid.takeAt(0).widget().deleteLater()
        y, m = s.cur; s.head.setText(D(f"{JM[m-1]} {y}") if JAL and FA else f"{MN[m-1]} {y}" if not FA else D(f"{y}/{m:02d}"))
        st = 5 if JAL else 0; en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]; fa = ["د", "س", "چ", "پ", "ج", "ش", "ی"]
        for i in range(7):
            l = QLabel((fa if FA else en)[(st + i) % 7]); l.setAlignment(AC); l.setObjectName("dim"); s.grid.addWidget(l, 0, i)
        off = (to_g(y, m, 1).weekday() - st) % 7
        for d in range(1, mlen(y, m) + 1):
            g = to_g(y, m, d); b = QPushButton(D(d)); b.setObjectName("cell")
            for k, val in (("sel", g == s.sel), ("today", g == date.today()), ("has", g.isoformat() in s.marks)): b.setProperty(k, "true" if val else "false")
            b.clicked.connect(lambda _, g=g: s.pick(g)); s.grid.addWidget(b, 1 + (off + d - 1) // 7, (off + d - 1) % 7)
    def pick(s, g): s.sel = g; s.build(); s.picked.emit(g)

class Main(QMainWindow):
    def __init__(s, hidden=False):
        global FA, JAL, H24
        super().__init__(); s.setWindowTitle("SAReminder"); s.setWindowIcon(logo()); s.resize(1180, 760); s.quitting = False; s.popups = []; s.hidden = hidden
        s.db = sqlite3.connect(DB); s.db.row_factory = sqlite3.Row; s.db.executescript(SCHEMA)
        cols = {r[1] for r in s.db.execute("PRAGMA table_info(tasks)")}
        for c, d in (("tags", "TEXT DEFAULT ''"), ("pinned", "INTEGER DEFAULT 0"), ("recur", "INTEGER DEFAULT 0"), ("done_at", "TEXT")):
            if c not in cols: s.db.execute(f"ALTER TABLE tasks ADD COLUMN {c} {d}")
        FA = s.get("lang", "en") == "fa"; JAL = s.get("jal", "1" if FA else "0") == "1"; H24 = s.get("h24", "1") == "1"
        root = QWidget(); root.setObjectName("root"); s.setCentralWidget(root); out = QVBoxLayout(root); out.setContentsMargins(0, 0, 0, 0); out.setSpacing(0)
        body = QHBoxLayout(); body.setSpacing(0); out.addLayout(body, 1)
        s.side = QListWidget(); s.side.setObjectName("side")
        for ic, k in (("▦", "dash"), ("☑", "tasks"), ("▤", "cal"), ("◔", "pomo"), ("♨", "habits"), ("✎", "notes"), ("⚙", "settings")): s.side.addItem(f"{ic}   {L(k)}")
        s.pages = QStackedWidget(); body.addWidget(s.side); body.addWidget(s.pages, 1); s.side.currentRowChanged.connect(s.pages.setCurrentIndex)
        for f in (s.p_dash, s.p_tasks, s.p_cal, s.p_pomo, s.p_habits, s.p_notes, s.p_set): s.pages.addWidget(f())
        ft = QLabel("© Copyright © Sadroddin Aghaei. All Rights Reserved."); ft.setObjectName("foot"); ft.setAlignment(AC); out.addWidget(ft)
        s.tray = QSystemTrayIcon(logo(), s); mn = QMenu(); mn.addAction("SAReminder", s.showNormal); mn.addAction("＋ " + L("add")[2:], s.new_task); mn.addAction("Quit", s.quit)
        s.tray.setContextMenu(mn); s.tray.activated.connect(lambda _: s.showNormal()); s.tray.show()
        for i in range(7): QShortcut(QKeySequence(f"Ctrl+{i+1}"), s, activated=lambda i=i: s.side.setCurrentRow(i))
        QShortcut(QKeySequence("Ctrl+N"), s, activated=s.new_task); QShortcut(QKeySequence("Ctrl+F"), s, activated=lambda: (s.side.setCurrentRow(1), s.q.setFocus()))
        s.side.setCurrentRow(0); s.refresh(); s.timer = QTimer(s); s.timer.timeout.connect(s.check); s.timer.start(20000); s.check()
    def get(s, k, d=None): r = s.db.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone(); return r["v"] if r else d
    def put(s, k, v): s.db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (k, str(v))); s.db.commit()
    def now(s): return datetime.now().strftime(FMT)
    def card(s, key, color="#ececec"):
        f = QFrame(); f.setObjectName("card"); v = QVBoxLayout(f); a = QLabel(L(key)); a.setObjectName("dim"); b = QLabel("0"); b.setObjectName("big"); b.setStyleSheet(f"color:{color}")
        v.addWidget(a); v.addWidget(b); f.val = b; return f
    # ---- pages
    def p_dash(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); h = QLabel(L("dash")); h.setObjectName("h1"); v.addWidget(h); r = QHBoxLayout(); v.addLayout(r)
        s.c = {k: s.card(k, col) for k, col in (("today", "#ececec"), ("over", "#ff3030"), ("comp", "#3ddc84"), ("streak", "#ffb020"))}; [r.addWidget(c) for c in s.c.values()]
        a = QLabel(L("prog")); a.setObjectName("h2"); s.bar = QProgressBar(); s.bar.setRange(0, 100); u = QLabel(L("up")); u.setObjectName("h2"); s.upl = QListWidget()
        [v.addWidget(x) for x in (a, s.bar, u, s.upl)]; return w
    def p_tasks(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); r = QHBoxLayout(); v.addLayout(r)
        ab = QPushButton(L("add")); ab.setObjectName("primary"); ab.clicked.connect(s.new_task); s.q = QLineEdit(); s.q.setPlaceholderText(L("search")); s.q.textChanged.connect(s.refresh)
        s.flt = QComboBox(); s.flt.addItems(S["f"][int(FA)]); s.flt.currentIndexChanged.connect(s.refresh); [r.addWidget(x) for x in (ab,)]; r.addWidget(s.q, 1); r.addWidget(s.flt)
        s.list = QListWidget(); s.list.itemDoubleClicked.connect(lambda _: s.edit()); v.addWidget(s.list); r2 = QHBoxLayout(); v.addLayout(r2)
        for k, f in (("done", s.toggle), ("edit", s.edit), ("dup", s.dup), ("pin", s.star), ("delete", s.remove)): b = QPushButton(L(k)); b.clicked.connect(f); r2.addWidget(b)
        return w
    def p_cal(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); s.cv = CalView(); s.cv.picked.connect(s.day); v.addWidget(s.cv, 3)
        s.dayl = QListWidget(); v.addWidget(s.dayl, 2); b = QPushButton(L("addday")); b.clicked.connect(lambda: s.new_task(s.cv.sel)); v.addWidget(b); return w
    def p_pomo(s):
        w = QWidget(); v = QVBoxLayout(w); v.setAlignment(AC); s.pm = "work"; s.left = 25 * 60; s.pt = QTimer(s); s.pt.timeout.connect(s.tick)
        s.ml = QLabel(L("work")); s.ml.setObjectName("h2"); s.ml.setAlignment(AC); s.tl = QLabel("25:00"); s.tl.setObjectName("timer"); s.tl.setAlignment(AC)
        s.wk = QSpinBox(); s.wk.setRange(1, 180); s.wk.setValue(25); s.bk = QSpinBox(); s.bk.setRange(1, 60); s.bk.setValue(5); r = QHBoxLayout()
        sb = QPushButton(L("start")); sb.setObjectName("primary"); pb = QPushButton(L("pause")); rb = QPushButton(L("reset"))
        sb.clicked.connect(lambda: s.pt.start(1000)); pb.clicked.connect(s.pt.stop); rb.clicked.connect(s.preset); [r.addWidget(x) for x in (sb, pb, rb)]
        s.sl = QLabel(); s.sl.setObjectName("dim"); s.sl.setAlignment(AC); r2 = QHBoxLayout(); r2.addWidget(QLabel(L("work"))); r2.addWidget(s.wk); r2.addWidget(QLabel(L("brk"))); r2.addWidget(s.bk)
        [v.addWidget(x) for x in (s.ml, s.tl)]; v.addLayout(r); v.addLayout(r2); v.addWidget(s.sl); s.preset(); return w
    def preset(s): s.pt.stop(); s.pm = "work"; s.left = s.wk.value() * 60; s.ml.setText(L("work")); s.tick(0)
    def tick(s, d=1):
        s.left -= d
        if s.left <= 0:
            if s.pm == "work": k = "pomo_" + date.today().isoformat(); s.put(k, int(s.get(k, 0)) + 1)
            s.pm = "brk" if s.pm == "work" else "work"; s.left = (s.bk.value() if s.pm == "brk" else s.wk.value()) * 60; s.ml.setText(L(s.pm)); s.tray.showMessage("SAReminder", L(s.pm), INFO, 6000)
        s.tl.setText(D(f"{s.left//60:02d}:{s.left%60:02d}")); s.sl.setText(f"{L('sess')}: {D(s.get('pomo_' + date.today().isoformat(), 0))}")
    def p_habits(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); r = QHBoxLayout(); v.addLayout(r); s.hl = QListWidget(); v.addWidget(s.hl)
        for k, f in (("nh", s.new_habit), ("toggle", s.hab_toggle), ("delete", s.hab_del)): b = QPushButton(L(k)); b.clicked.connect(f); r.addWidget(b)
        s.hab(); return w
    def streak_of(s, days):
        d = date.today(); n = 0
        if d.isoformat() not in days: d -= timedelta(days=1)
        while d.isoformat() in days: n += 1; d -= timedelta(days=1)
        return n
    def hab(s):
        s.hl.clear()
        for h in s.db.execute("SELECT * FROM habits"):
            days = {r[0] for r in s.db.execute("SELECT day FROM habit_log WHERE habit_id=?", (h["id"],))}; ok = date.today().isoformat() in days
            it = QListWidgetItem(f"{'✔' if ok else '○'}  {h['name']}    🔥 {D(s.streak_of(days))}"); it.setData(UR, h["id"]); s.hl.addItem(it)
    def new_habit(s):
        n, ok = QInputDialog.getText(s, "SAReminder", L("nh"))
        if ok and n.strip(): s.db.execute("INSERT INTO habits(name) VALUES(?)", (n.strip(),)); s.db.commit(); s.hab()
    def hab_toggle(s):
        i = s.hl.currentItem()
        if not i: return
        h, t = i.data(UR), date.today().isoformat()
        if s.db.execute("SELECT 1 FROM habit_log WHERE habit_id=? AND day=?", (h, t)).fetchone(): s.db.execute("DELETE FROM habit_log WHERE habit_id=? AND day=?", (h, t))
        else: s.db.execute("INSERT INTO habit_log VALUES(?,?)", (h, t))
        s.db.commit(); s.hab(); s.refresh()
    def hab_del(s):
        i = s.hl.currentItem()
        if i: s.db.execute("DELETE FROM habits WHERE id=?", (i.data(UR),)); s.db.execute("DELETE FROM habit_log WHERE habit_id=?", (i.data(UR),)); s.db.commit(); s.hab()
    def p_notes(s):
        w = QWidget(); v = QHBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); lv = QVBoxLayout(); v.addLayout(lv, 1); s.nl = QListWidget(); lv.addWidget(s.nl)
        for k, f in (("nn", s.new_note), ("delete", s.del_note)): b = QPushButton(L(k)); b.clicked.connect(f); lv.addWidget(b)
        s.ne = QTextEdit(); v.addWidget(s.ne, 2); s.cur = None; s.nl.currentItemChanged.connect(s.open_note); s.ne.textChanged.connect(s.save_note); s.notes(); return w
    def notes(s, sel=None):
        s.nl.blockSignals(True); s.nl.clear()
        for r in s.db.execute("SELECT id,title FROM notes ORDER BY updated DESC"):
            it = QListWidgetItem(r["title"] or "—"); it.setData(UR, r["id"]); s.nl.addItem(it)
            if r["id"] == sel: s.nl.setCurrentItem(it)
        s.nl.blockSignals(False)
    def new_note(s): c = s.db.execute("INSERT INTO notes(title,body,updated) VALUES('','',?)", (s.now(),)); s.db.commit(); s.notes(c.lastrowid); s.cur = c.lastrowid; s.ne.blockSignals(True); s.ne.clear(); s.ne.blockSignals(False); s.ne.setFocus()
    def open_note(s, it, _=None):
        s.cur = it.data(UR) if it else None; r = s.db.execute("SELECT body FROM notes WHERE id=?", (s.cur,)).fetchone(); s.ne.blockSignals(True); s.ne.setPlainText(r["body"] if r else ""); s.ne.blockSignals(False)
    def save_note(s):
        if s.cur: b = s.ne.toPlainText(); s.db.execute("UPDATE notes SET title=?,body=?,updated=? WHERE id=?", (b.strip().split("\n")[0][:40], b, s.now(), s.cur)); s.db.commit(); i = s.nl.currentItem(); i and i.setText(b.strip().split("\n")[0][:40] or "—")
    def del_note(s):
        if s.cur: s.db.execute("DELETE FROM notes WHERE id=?", (s.cur,)); s.db.commit(); s.cur = None; s.ne.clear(); s.notes()
    def p_set(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(28, 24, 28, 16); v.setAlignment(Qt.AlignmentFlag.AlignTop); v.addWidget(QLabel(L("lang")))
        c = QComboBox(); c.addItem("English", "en"); c.addItem("فارسی", "fa"); c.setCurrentIndex(int(FA)); c.activated.connect(lambda i: s.change("lang", c.itemData(i))); v.addWidget(c)
        for k, key, val in (("jal", "jal", JAL), ("h24", "h24", H24)):
            cb = QCheckBox(L(k)); cb.setChecked(val); cb.toggled.connect(lambda on, key=key: s.change(key, "1" if on else "0")); v.addWidget(cb)
        a = QCheckBox(L("auto")); a.setEnabled(sys.platform == "win32" and getattr(sys, "frozen", False)); a.toggled.connect(s.autostart); v.addWidget(a)
        for k, f in (("exp", s.export), ("imp", s.imp), ("folder", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(DIR))))): b = QPushButton(L(k)); b.clicked.connect(f); v.addWidget(b)
        return w
    def change(s, k, v):
        s.put(k, v)
        if k == "lang" and s.get("jal") is None: s.put("jal", "1" if v == "fa" else "0")
        QProcess.startDetached(sys.executable, sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv); s.quit()
    def autostart(s, on):
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if on: winreg.SetValueEx(k, "SAReminder", 0, winreg.REG_SZ, f'"{sys.executable}" --hidden')
        else:
            try: winreg.DeleteValue(k, "SAReminder")
            except FileNotFoundError: pass
    # ---- tasks
    def save(s, d, id=None):
        if id: s.db.execute("UPDATE tasks SET title=:title,notes=:notes,tags=:tags,priority=:priority,due_at=:due_at,remind_min=:remind_min,trigger_at=:trigger_at,recur=:recur,pinned=:pinned,notified=0,updated_at=CURRENT_TIMESTAMP WHERE id=:id", {**d, "id": id})
        else: s.db.execute("INSERT INTO tasks(title,notes,tags,priority,due_at,remind_min,trigger_at,recur,pinned) VALUES(:title,:notes,:tags,:priority,:due_at,:remind_min,:trigger_at,:recur,:pinned)", d)
        s.db.commit(); s.refresh(); s.check()
    def new_task(s, day=None):
        dl = TaskDialog(s, day=day if isinstance(day, date) else None)
        if dl.exec(): s.save(dl.data())
    def sel(s): i = s.list.currentItem(); return s.db.execute("SELECT * FROM tasks WHERE id=?", (i.data(UR),)).fetchone() if i else None
    def edit(s):
        r = s.sel()
        if r:
            dl = TaskDialog(s, r)
            if dl.exec(): s.save(dl.data(), r["id"])
    def dup(s):
        r = s.sel()
        if r: d = {k: r[k] for k in ("title", "notes", "tags", "priority", "due_at", "remind_min", "trigger_at", "recur", "pinned")}; d["title"] += " (2)"; s.save(d)
    def star(s):
        r = s.sel()
        if r: s.db.execute("UPDATE tasks SET pinned=1-pinned WHERE id=?", (r["id"],)); s.db.commit(); s.refresh()
    def remove(s):
        r = s.sel()
        if r: s.db.execute("DELETE FROM tasks WHERE id=?", (r["id"],)); s.db.commit(); s.refresh()
    def toggle(s):
        r = s.sel()
        if r: s.set_done(r["id"], not r["done"])
    def set_done(s, i, on=True):
        r = s.db.execute("SELECT * FROM tasks WHERE id=?", (i,)).fetchone()
        if not r: return
        s.db.execute("UPDATE tasks SET done=?,done_at=? WHERE id=?", (int(on), s.now() if on else None, i))
        if on and r["recur"] and r["due_at"]:
            d = nxt(r["due_at"], r["recur"]); s.db.execute("INSERT INTO tasks(title,notes,tags,priority,due_at,remind_min,trigger_at,recur,pinned) VALUES(?,?,?,?,?,?,?,?,?)",
                (r["title"], r["notes"], r["tags"], r["priority"], d.strftime(FMT), r["remind_min"], (d - timedelta(minutes=r["remind_min"])).strftime(FMT), r["recur"], r["pinned"]))
        s.db.commit(); s.refresh()
    def refresh(s, *_):
        n = s.now(); f = s.flt.currentIndex(); like = f"%{s.q.text()}%"
        w = "(title LIKE ? OR tags LIKE ? OR notes LIKE ?) AND " + ["1=1", "due_at LIKE ? AND done=0", "due_at>? AND done=0", "due_at<? AND done=0", "pinned=1 AND done=0", "done=1"][f]
        a = [like] * 3 + ([n[:10] + "%"] if f == 1 else [n] if f in (2, 3) else [])
        s.list.clear(); col = ["#8a8a8a", "#ececec", "#ffb020", "#ff3030"]
        for r in s.db.execute(f"SELECT * FROM tasks WHERE {w} ORDER BY done,pinned DESC,priority DESC,due_at", a):
            tg = "  " + " ".join("#" + x.strip() for x in r["tags"].split(",") if x.strip()) if r["tags"] else ""
            it = QListWidgetItem(f"{'✔' if r['done'] else '★' if r['pinned'] else '○'}  {r['title']}   {fdt(r['due_at'])}{'  ⟳' if r['recur'] else ''}{tg}"); it.setData(UR, r["id"])
            it.setForeground(QColor("#555" if r["done"] else "#ff3030" if r["due_at"] and r["due_at"] < n else col[r["priority"]])); s.list.addItem(it)
        t = n[:10]; q = lambda sql, *p: s.db.execute(sql, p).fetchone()[0]
        td, dn = q("SELECT COUNT(*) FROM tasks WHERE due_at LIKE ? AND done=0", t + "%"), q("SELECT COUNT(*) FROM tasks WHERE done_at LIKE ?", t + "%")
        s.c["today"].val.setText(D(td)); s.c["over"].val.setText(D(q("SELECT COUNT(*) FROM tasks WHERE due_at<? AND done=0", n))); s.c["comp"].val.setText(D(q("SELECT COUNT(*) FROM tasks WHERE done=1")))
        s.c["streak"].val.setText(D(s.streak_of({r[0] for r in s.db.execute("SELECT DISTINCT substr(done_at,1,10) FROM tasks WHERE done_at IS NOT NULL")})))
        s.bar.setValue(int(100 * dn / (td + dn)) if td + dn else 0); s.upl.clear()
        for r in s.db.execute("SELECT * FROM tasks WHERE done=0 AND due_at>=? ORDER BY due_at LIMIT 8", (n,)): s.upl.addItem(f"{fdt(r['due_at'])}   {r['title']}")
        s.cv.marks = {r[0] for r in s.db.execute("SELECT DISTINCT substr(due_at,1,10) FROM tasks WHERE due_at IS NOT NULL AND done=0")}; s.cv.build(); s.day(s.cv.sel)
    def day(s, g):
        s.dayl.clear()
        for r in s.db.execute("SELECT * FROM tasks WHERE due_at LIKE ? ORDER BY due_at", (g.isoformat() + "%",)): s.dayl.addItem(f"{fdt(r['due_at'])}   {r['title']}")
        if not s.dayl.count(): s.dayl.addItem(L("nodue"))
    def check(s):
        for r in s.db.execute("SELECT * FROM tasks WHERE done=0 AND notified=0 AND trigger_at IS NOT NULL AND trigger_at<=?", (s.now(),)).fetchall():
            s.db.execute("UPDATE tasks SET notified=1 WHERE id=?", (r["id"],)); s.db.commit(); s.tray.showMessage("SAReminder", r["title"], INFO, 10000)
            b = QMessageBox(s); b.setWindowTitle("SAReminder"); b.setText(r["title"]); b.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            sn = b.addButton(L("snz"), QMessageBox.ButtonRole.ActionRole); ok = b.addButton(L("cmp"), QMessageBox.ButtonRole.AcceptRole); b.addButton(L("dis"), QMessageBox.ButtonRole.RejectRole)
            b.buttonClicked.connect(lambda btn, i=r["id"], sn=sn, ok=ok: s.act(btn, sn, ok, i)); b.show(); s.popups.append(b)
    def act(s, btn, sn, ok, i):
        if btn is sn: s.db.execute("UPDATE tasks SET trigger_at=?,notified=0 WHERE id=?", ((datetime.now() + timedelta(minutes=10)).strftime(FMT), i)); s.db.commit(); s.refresh()
        elif btn is ok: s.set_done(i)
    def export(s):
        p, _ = QFileDialog.getSaveFileName(s, "", "sareminder-backup.json", "JSON (*.json)")
        if p: Path(p).write_text(json.dumps({t: [dict(r) for r in s.db.execute(f"SELECT * FROM {t}")] for t in ("tasks", "habits", "habit_log", "notes")}, ensure_ascii=False, indent=1), "utf-8")
    def imp(s):
        p, _ = QFileDialog.getOpenFileName(s, "", "", "JSON (*.json)")
        if not p: return
        try:
            data = json.loads(Path(p).read_text("utf-8")); data = data if isinstance(data, dict) else {"tasks": data}
            for t, rows in data.items():
                if t not in ("tasks", "habits", "habit_log", "notes"): continue
                cols = [r[1] for r in s.db.execute(f"PRAGMA table_info({t})")]
                for r in rows:
                    ks = [k for k in r if k in cols and k != "id"]; s.db.execute(f"INSERT OR IGNORE INTO {t}({','.join(ks)}) VALUES({','.join('?'*len(ks))})", [r[k] for k in ks])
            s.db.commit(); s.refresh(); s.hab(); s.notes()
        except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as e: QMessageBox.critical(s, "SAReminder", str(e))
    def closeEvent(s, e):
        if s.quitting: return e.accept()
        e.ignore(); s.hide(); s.tray.showMessage("SAReminder", L("tray"), INFO, 2500)
    def quit(s): s.quitting = True; QApplication.quit()

if __name__ == "__main__":
    a = QApplication(sys.argv); a.setStyleSheet(QSS); a.setQuitOnLastWindowClosed(False); w = Main("--hidden" in sys.argv)
    if FA: a.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    if not w.hidden: w.show()
    sys.exit(a.exec())
