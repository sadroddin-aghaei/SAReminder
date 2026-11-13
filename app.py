"""SAReminder v3 - TickTick-style offline tasks & reminders with Jalali calendar.
(c) Sadroddin Aghaei. All Rights Reserved."""
import sys, json, sqlite3, calendar, re
from datetime import datetime, date, timedelta
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QTime, QProcess, QUrl, QSize, QRectF, Signal, QPropertyAnimation, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QKeySequence, QShortcut, QDesktopServices, QPainterPath, QPen
from PySide6.QtWidgets import *

UR = Qt.ItemDataRole.UserRole; AC = Qt.AlignmentFlag.AlignCenter; INFO = QSystemTrayIcon.MessageIcon.Information; AA = QPainter.RenderHint.Antialiasing
DIR = Path.home() / ".sareminder"; DIR.mkdir(exist_ok=True); DB = DIR / "sareminder.db"
FMT = "%Y-%m-%dT%H:%M"; FA = JAL = LIGHT = False; H24 = ANIM = SOUND = True; ACC = "#ff3030"
ACCENTS = ["#ff3030", "#ff7a45", "#ffb020", "#3ddc84", "#2dd4bf", "#4c8dff", "#a78bfa", "#f472b6"]
SMART = [("all", "▤"), ("today", "☀"), ("tomorrow", "☾"), ("week", "▦"), ("over", "⚠"), ("star", "★"), ("done", "✔")]
S = dict(dash=("Dashboard", "داشبورد"), cal=("Calendar", "تقویم"), pomo=("Focus", "تمرکز"), habits=("Habits", "عادت‌ها"), notes=("Notes", "یادداشت‌ها"), settings=("Settings", "تنظیمات"),
 sm=(["All", "Today", "Tomorrow", "Next 7 Days", "Overdue", "Starred", "Completed"], ["همه", "امروز", "فردا", "۷ روز آینده", "عقب‌افتاده", "ستاره‌دار", "انجام‌شده"]),
 hl=("LISTS", "لیست‌ها"), ht=("TOOLS", "ابزارها"), newlist=("＋  New list", "＋  لیست جدید"), newlname=("List name", "نام لیست"), dellist=("Delete list", "حذف لیست"),
 quick=("＋  Add a task…  e.g. Call mom tomorrow 18:00 #family !!", "＋  افزودن وظیفه…  مثلاً تماس با مادر فردا ۱۸:۰۰ #خانواده !!"), search=("Search…", "جستجو…"),
 sortl=(["Date", "Priority", "Title", "Newest"], ["تاریخ", "اولویت", "عنوان", "جدیدترین"]), pri=(["Low", "Medium", "High", "Urgent"], ["کم", "متوسط", "زیاد", "فوری"]),
 title=("Title", "عنوان"), nt=("Notes", "توضیحات"), tags=("Tags (comma separated)", "برچسب‌ها (با کاما)"), due=("Has due date", "دارای موعد"), rem=("Remind before", "یادآوری قبل از"),
 now=("At due time", "سر موعد"), mn=("min", "دقیقه"), rep=("Repeat", "تکرار"), rp=(["Never", "Daily", "Weekly", "Monthly"], ["هرگز", "روزانه", "هفتگی", "ماهانه"]),
 pin=("Star", "ستاره"), edit=("Edit", "ویرایش"), dup=("Duplicate", "کپی"), delete=("Delete", "حذف"), moveto=("Move to", "انتقال به"), nolist=("— No list —", "— بدون لیست —"),
 lst=("List", "لیست"), cl=("Checklist", "چک‌لیست"), additem=("Add item…", "افزودن مورد…"), prio=("Priority", "اولویت"), today=("Today", "امروز"), tmr=("Tomorrow", "فردا"),
 over=("Overdue", "عقب‌افتاده"), comp=("Completed", "انجام‌شده"), streak=("Day streak", "روز پیاپی"), up=("Upcoming", "پیش‌رو"), prog=("Today's progress", "پیشرفت امروز"), wk=("Last 7 days", "۷ روز گذشته"),
 start=("Start", "شروع"), pause=("Pause", "توقف"), reset=("Reset", "بازنشانی"), work=("Focus", "تمرکز"), brk=("Break", "استراحت"), sess=("Sessions today", "جلسه‌های امروز"),
 nh=("＋ New habit", "＋ عادت جدید"), nn=("＋ New note", "＋ یادداشت جدید"), toggle=("Done today", "انجام امروز"), setth=("Appearance", "ظاهر"), accent=("Accent color", "رنگ تم"), custom=("Custom…", "دلخواه…"),
 theme=(["Dark (OLED)", "Light"], ["تیره (OLED)", "روشن"]), anim=("Animations", "انیمیشن‌ها"), snd=("Notification sound", "صدای اعلان"), gen=("General", "عمومی"), lang=("Language (restarts the app)", "زبان (برنامه دوباره باز می‌شود)"),
 jal=("Jalali (Persian) calendar", "تقویم جلالی (شمسی)"), h24=("24-hour time", "ساعت ۲۴ ساعته"), auto=("Start with Windows", "اجرا همراه ویندوز"), defrem=("Default reminder (quick add)", "یادآوری پیش‌فرض (افزودن سریع)"),
 data=("Data", "داده‌ها"), exp=("Export JSON backup", "خروجی پشتیبان JSON"), imp=("Import JSON backup", "ورودی پشتیبان JSON"), folder=("Open data folder", "باز کردن پوشه داده"),
 snz=("Snooze 10 min", "۱۰ دقیقه بعد"), cmp=("Complete", "انجام شد"), dis=("Dismiss", "بستن"), empty=("Enter a title.", "عنوان را وارد کنید."), bad=("Invalid date.", "تاریخ نامعتبر است."),
 addday=("＋ Add task on this day", "＋ افزودن وظیفه در این روز"), tray=("Running in the tray.", "در سینی سیستم در حال اجراست."), none=("Nothing here yet", "اینجا هنوز چیزی نیست"), added=("Task added", "وظیفه اضافه شد"),
 add=("＋ New task", "＋ وظیفه جدید"), nodue=("No tasks", "بدون وظیفه"))
JM = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
MN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def L(k): return S[k][1 if FA else 0]
def LS(k): return S[k][int(FA)]
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
def ftime(d): return D(d.strftime("%H:%M" if H24 else "%I:%M %p"))
def fdt(iso): d = datetime.strptime(iso, FMT) if iso else None; return f"{fdate(d.date())}  {ftime(d)}" if d else ""
def rel(iso):
    d = datetime.strptime(iso, FMT); td = date.today()
    return f"{L('today') if d.date() == td else L('tmr') if d.date() == td + timedelta(days=1) else fdate(d.date())} {ftime(d)}"
def nxt(due, rec):
    d = datetime.strptime(due, FMT)
    if rec == 1: d += timedelta(days=1)
    elif rec == 2: d += timedelta(days=7)
    else: d = d.replace(year=d.year + (d.month == 12), month=d.month % 12 + 1, day=min(d.day, 28))
    return d
def parse_quick(txt):
    keep, tags, pri, d, tm = [], [], 1, None, None; td = date.today()
    for w in txt.split():
        lw = w.lower()
        if w.startswith("#") and len(w) > 1: tags.append(w[1:])
        elif set(w) == {"!"} and len(w) <= 3: pri = len(w)
        elif lw in ("today", "امروز"): d = td
        elif lw in ("tomorrow", "tmr", "فردا"): d = td + timedelta(days=1)
        elif re.fullmatch(r"@?\d{1,2}:\d{2}", w) and int(w.lstrip("@").split(":")[0]) < 24 and int(w.split(":")[1]) < 60: tm = tuple(int(x) for x in w.lstrip("@").split(":"))
        else: keep.append(w)
    return " ".join(keep), tags, pri, d, tm
def mix(a, b, t):
    x, y = QColor(a), QColor(b); return QColor(int(x.red() * t + y.red() * (1 - t)), int(x.green() * t + y.green() * (1 - t)), int(x.blue() * t + y.blue() * (1 - t))).name()
def pal(): return dict(BG="#000000", S="#0a0a0a", B="#1f1f1f", T="#ececec", D="#8a8a8a", H="#141414") if not LIGHT else dict(BG="#ffffff", S="#f5f6f8", B="#e4e6ea", T="#1d1d1f", D="#77797f", H="#eceef1")
QSS_T = """*{background:transparent;color:@T;font-family:'Segoe UI','Vazirmatn','Tahoma','Geeza Pro',sans-serif;font-size:14px}
QMainWindow,#root,QStackedWidget>QWidget,QDialog,QMessageBox{background:@BG}
QListWidget{background:@S;border:1px solid @B;border-radius:14px;padding:6px;outline:0}QListWidget::item{padding:9px;border-radius:10px;margin:1px 0}
QListWidget::item:selected{background:@TINT}QListWidget::item:hover{background:@H}
#side{background:@S;border:0;border-right:1px solid @B;border-radius:0;min-width:215px;max-width:215px;padding:10px 8px}#side::item{padding:9px 12px;margin:1px 0}
#side::item:selected{background:@TINT;color:@A;font-weight:600}
QListWidget#tl{background:transparent;border:0;padding:0}QListWidget#tl::item{padding:0;margin:0;border-radius:0;border-bottom:1px solid @B}QListWidget#tl::item:hover{background:@H}QListWidget#tl::item:selected{background:@TINT}
QLineEdit,QComboBox,QSpinBox,QTimeEdit,QPlainTextEdit,QTextEdit{background:@S;border:1px solid @B;border-radius:10px;padding:8px}
QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QTimeEdit:focus,QPlainTextEdit:focus,QTextEdit:focus{border:1px solid @A}
QLineEdit#quick{padding:13px 16px;border-radius:12px;font-size:15px}QComboBox::drop-down{border:0;width:22px}
QComboBox QAbstractItemView{background:@S;border:1px solid @B;selection-background-color:@TINT;color:@T}
QPushButton{background:@H;border:1px solid @B;border-radius:10px;padding:8px 14px}QPushButton:hover{border-color:@A}QPushButton:pressed{background:@TINT}
QPushButton#primary{background:@A;color:#fff;border:0;font-weight:700}QPushButton#primary:hover{background:@AH}
QMenu{background:@S;border:1px solid @B;border-radius:10px;padding:6px}QMenu::item{padding:8px 24px;border-radius:6px}QMenu::item:selected{background:@TINT}
#card{background:@S;border:1px solid @B;border-radius:16px}#big{font-size:32px;font-weight:700}#h1{font-size:26px;font-weight:700}#h2{font-size:16px;font-weight:600;margin-top:10px}#dim{color:@D}
#toast{background:@A;color:#fff;border-radius:20px;padding:0 20px;font-weight:600}
QProgressBar{background:@H;border:0;border-radius:6px;height:10px;text-align:center;color:transparent}QProgressBar::chunk{background:@A;border-radius:6px}
QPushButton#cell{min-height:46px;border-radius:12px;background:@S;border:1px solid @B}QPushButton#cell[today="true"]{border:1px solid @A}
QPushButton#cell[has="true"]{background:@TINT;color:@A;font-weight:700}QPushButton#cell[sel="true"]{background:@A;color:#fff;font-weight:700}
QCheckBox::indicator{width:18px;height:18px;border-radius:5px;border:1px solid @D}QCheckBox::indicator:checked{background:@A;border-color:@A}
QCheckBox#round::indicator{width:20px;height:20px;border-radius:11px;border:2px solid @D}QCheckBox#round[pri="0"]::indicator{border-color:#4c8dff}
QCheckBox#round[pri="2"]::indicator{border-color:#ff7a45}QCheckBox#round[pri="3"]::indicator{border-color:#ff3b3b}QCheckBox#round::indicator:checked{background:@D;border-color:@D}
#foot{color:@D;font-size:12px;border-top:1px solid @B;padding:7px}QScrollBar:vertical{background:transparent;width:8px}QScrollBar::handle:vertical{background:@B;border-radius:4px}"""
def qss():
    p = pal(); p.update(A=ACC, AH=mix(ACC, "#ffffff", .8), TINT=mix(ACC, p["BG"], .15)); s = QSS_T
    for k in sorted(p, key=len, reverse=True): s = s.replace("@" + k, p[k])
    return s
def logo():
    p = QPixmap(256, 256); p.fill(Qt.GlobalColor.transparent); q = QPainter(p); q.setRenderHint(AA); q.setBrush(QColor(ACC)); q.setPen(Qt.PenStyle.NoPen); q.drawRoundedRect(8, 8, 240, 240, 56, 56)
    q.scale(2, 2); q.setBrush(QColor("#fff")); b = QPainterPath(); b.moveTo(32, 88); b.cubicTo(40, 80, 42, 70, 42, 56); b.cubicTo(42, 40, 52, 32, 64, 32); b.cubicTo(76, 32, 86, 40, 86, 56); b.cubicTo(86, 70, 88, 80, 96, 88); b.closeSubpath()
    q.drawPath(b); q.drawEllipse(60, 22, 8, 8); q.drawEllipse(55, 92, 18, 12); q.end(); return QIcon(p)
def dot(c):
    p = QPixmap(14, 14); p.fill(Qt.GlobalColor.transparent); q = QPainter(p); q.setRenderHint(AA); q.setBrush(QColor(c)); q.setPen(Qt.PenStyle.NoPen); q.drawEllipse(2, 2, 10, 10); q.end(); return QIcon(p)
def fade(w, ms=220):
    if not ANIM or w is None: return
    e = QGraphicsOpacityEffect(w); w.setGraphicsEffect(e); a = QPropertyAnimation(e, b"opacity", w); a.setDuration(ms); a.setStartValue(0.0); a.setEndValue(1.0)
    a.setEasingCurve(QEasingCurve.Type.OutCubic); a.finished.connect(lambda: w.setGraphicsEffect(None)); a.start(); w._fa = a
def count_to(lbl, n):
    if not ANIM: return lbl.setText(D(n))
    a = QVariantAnimation(lbl); a.setDuration(450); a.setStartValue(0); a.setEndValue(int(n)); a.valueChanged.connect(lambda v: lbl.setText(D(int(v)))); a.start(); lbl._na = a
SCHEMA = """CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,notes TEXT,priority INTEGER DEFAULT 1,due_at TEXT,
remind_min INTEGER DEFAULT 0,trigger_at TEXT,notified INTEGER DEFAULT 0,done INTEGER DEFAULT 0,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS habit_log(habit_id INTEGER,day TEXT,PRIMARY KEY(habit_id,day));CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,body TEXT,updated TEXT);
CREATE TABLE IF NOT EXISTS lists(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,color TEXT);"""
TKEYS = ("title", "notes", "tags", "priority", "due_at", "remind_min", "trigger_at", "recur", "pinned", "list_id", "checklist")

class Bars(QWidget):
    def __init__(s): super().__init__(); s.data = []; s.k = 1.0; s.setMinimumHeight(150)
    def set(s, data):
        s.data = data
        if not ANIM: s.k = 1.0; return s.update()
        a = QVariantAnimation(s); a.setDuration(650); a.setStartValue(0.0); a.setEndValue(1.0); a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.valueChanged.connect(lambda v: (setattr(s, "k", v), s.update())); a.start(); s._a = a
    def paintEvent(s, e):
        p = QPainter(s); p.setRenderHint(AA); P = pal(); w, h = s.width(), s.height(); n = len(s.data) or 1; mx = max([v for _, v in s.data] + [1]); bw = w / n
        for i, (lab, v) in enumerate(s.data):
            bh = (h - 44) * v / mx * s.k; x = i * bw + bw * .2; p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(ACC) if v else QColor(P["H"]))
            p.drawRoundedRect(QRectF(x, h - 24 - max(bh, 4), bw * .6, max(bh, 4)), 6, 6); p.setPen(QColor(P["D"])); p.drawText(QRectF(i * bw, h - 22, bw, 20), AC, lab)
            if v: p.setPen(QColor(P["T"])); p.drawText(QRectF(i * bw, h - 44 - bh, bw, 18), AC, D(v))

class Ring(QWidget):
    def __init__(s): super().__init__(); s.f = 1.0; s.text = "25:00"; s.setMinimumSize(300, 300)
    def set(s, f, text):
        s.text = text
        if not ANIM: s.f = f; return s.update()
        a = QVariantAnimation(s); a.setDuration(900); a.setStartValue(s.f); a.setEndValue(f); a.valueChanged.connect(lambda v: (setattr(s, "f", v), s.update())); a.start(); s._a = a
    def paintEvent(s, e):
        p = QPainter(s); p.setRenderHint(AA); P = pal(); side = min(s.width(), s.height()) - 30; r = QRectF((s.width() - side) / 2, (s.height() - side) / 2, side, side)
        pen = QPen(QColor(P["H"]), 14); pen.setCapStyle(Qt.PenCapStyle.RoundCap); p.setPen(pen); p.drawEllipse(r); pen.setColor(QColor(ACC)); p.setPen(pen); p.drawArc(r, 90 * 16, int(-360 * 16 * s.f))
        p.setPen(QColor(P["T"])); p.setFont(QFont("Segoe UI", 46, QFont.Weight.Bold)); p.drawText(r, AC, s.text)

class TaskDialog(QDialog):
    def __init__(s, parent, row=None, day=None, list_id=None):
        super().__init__(parent); s.setWindowTitle("SAReminder"); s.setMinimumWidth(480); v = QFormLayout(s)
        s.t = QLineEdit(); s.n = QPlainTextEdit(); s.n.setFixedHeight(64); s.tg = QLineEdit(); s.p = QComboBox(); s.p.addItems(LS("pri")); s.p.setCurrentIndex(1)
        s.lc = QComboBox(); s.lc.addItem(L("nolist"), None); [s.lc.addItem(n, i) for i, (n, c) in parent.lists.items()]
        s.has = QCheckBox(L("due")); s.y = QSpinBox(); s.y.setRange(1300, 1600) if JAL else s.y.setRange(1900, 2200); s.m = QSpinBox(); s.m.setRange(1, 12); s.d = QSpinBox(); s.d.setRange(1, 31)
        s.tm = QTimeEdit(); s.tm.setDisplayFormat("HH:mm" if H24 else "hh:mm AP"); s.r = QComboBox(); s.r.addItem(L("now"), 0); [s.r.addItem(f"{D(m)} {L('mn')}", m) for m in (5, 15, 30, 60, 120, 1440)]
        s.rp = QComboBox(); s.rp.addItems(LS("rp")); s.pin = QCheckBox(L("pin")); rd = QHBoxLayout(); [rd.addWidget(w) for w in (s.y, s.m, s.d, s.tm)]
        s.cl = QListWidget(); s.cl.setFixedHeight(110); s.ci = QLineEdit(); s.ci.setPlaceholderText(L("additem")); s.ci.returnPressed.connect(lambda: (s.item(s.ci.text(), False), s.ci.clear()))
        rm = QPushButton("－"); rm.setFixedWidth(40); rm.clicked.connect(lambda: s.cl.takeItem(s.cl.currentRow())); cr = QHBoxLayout(); cr.addWidget(s.ci); cr.addWidget(rm)
        for k, w in (("title", s.t), ("nt", s.n), ("tags", s.tg), ("prio", s.p), ("lst", s.lc)): v.addRow(L(k), w)
        v.addRow("", s.has); v.addRow(L("due"), rd); v.addRow(L("rem"), s.r); v.addRow(L("rep"), s.rp); v.addRow(L("cl"), s.cl); v.addRow("", cr); v.addRow("", s.pin)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); bb.accepted.connect(s.ok); bb.rejected.connect(s.reject); v.addRow(bb)
        base = datetime.now() + timedelta(hours=1)
        if list_id: s.lc.setCurrentIndex(max(0, s.lc.findData(list_id)))
        if row:
            s.t.setText(row["title"]); s.n.setPlainText(row["notes"] or ""); s.tg.setText(row["tags"] or ""); s.p.setCurrentIndex(row["priority"]); s.pin.setChecked(bool(row["pinned"]))
            s.rp.setCurrentIndex(row["recur"] or 0); s.r.setCurrentIndex(max(0, s.r.findData(row["remind_min"]))); s.has.setChecked(bool(row["due_at"])); s.lc.setCurrentIndex(max(0, s.lc.findData(row["list_id"])))
            for t, dn in json.loads(row["checklist"] or "[]"): s.item(t, dn)
            if row["due_at"]: base = datetime.strptime(row["due_at"], FMT)
        elif day: base = datetime.combine(day, base.time()); s.has.setChecked(True)
        y, m, d = from_g(base.date()); s.y.setValue(y); s.m.setValue(m); s.d.setValue(d); s.tm.setTime(QTime(base.hour, base.minute))
    def item(s, t, done):
        if not t.strip(): return
        it = QListWidgetItem(t.strip()); it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable); it.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked); s.cl.addItem(it)
    def showEvent(s, e):
        super().showEvent(e)
        if ANIM: s.setWindowOpacity(0); a = QPropertyAnimation(s, b"windowOpacity", s); a.setDuration(200); a.setStartValue(0.0); a.setEndValue(1.0); a.start(); s._a = a
    def ok(s):
        if not s.t.text().strip(): return QMessageBox.warning(s, "SAReminder", L("empty"))
        if s.has.isChecked():
            try: to_g(s.y.value(), s.m.value(), s.d.value())
            except ValueError: return QMessageBox.warning(s, "SAReminder", L("bad"))
        s.accept()
    def data(s):
        due = trig = None; m = s.r.currentData()
        if s.has.isChecked():
            dt = datetime.combine(to_g(s.y.value(), s.m.value(), s.d.value()), s.tm.time().toPython()); due = dt.strftime(FMT); trig = (dt - timedelta(minutes=m)).strftime(FMT)
        cl = [[s.cl.item(i).text(), s.cl.item(i).checkState() == Qt.CheckState.Checked] for i in range(s.cl.count())]
        return dict(title=s.t.text().strip(), notes=s.n.toPlainText(), tags=s.tg.text().strip(), priority=s.p.currentIndex(), due_at=due, remind_min=m, trigger_at=trig,
                    recur=s.rp.currentIndex(), pinned=int(s.pin.isChecked()), list_id=s.lc.currentData(), checklist=json.dumps(cl, ensure_ascii=False))

class CalView(QWidget):
    picked = Signal(object)
    def __init__(s):
        super().__init__(); s.marks = set(); s.sel = date.today(); s.cur = from_g(s.sel)[:2]; v = QVBoxLayout(s); h = QHBoxLayout(); v.addLayout(h)
        s.head = QLabel(); s.head.setObjectName("h1"); pv = QPushButton("‹"); nx = QPushButton("›"); td = QPushButton(L("today"))
        pv.clicked.connect(lambda: s.step(-1)); nx.clicked.connect(lambda: s.step(1)); td.clicked.connect(s.go_today)
        h.addWidget(s.head, 1); [h.addWidget(b) for b in (pv, td, nx)]; s.grid = QGridLayout(); v.addLayout(s.grid); s.build()
    def step(s, k): y, m = s.cur; m += k; y += (m - 1) // 12; m = (m - 1) % 12 + 1; s.cur = (y, m); s.build(); fade(s.grid.parentWidget() and s, 160)
    def go_today(s): s.sel = date.today(); s.cur = from_g(s.sel)[:2]; s.build(); s.picked.emit(s.sel)
    def build(s):
        while s.grid.count(): s.grid.takeAt(0).widget().deleteLater()
        y, m = s.cur; s.head.setText(D(f"{JM[m-1]} {y}") if JAL and FA else f"{MN[m-1]} {y}" if not FA else D(f"{y}/{m:02d}"))
        st = 5 if JAL else 0; en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]; fa = ["د", "س", "چ", "پ", "ج", "ش", "ی"]
        for i in range(7): l = QLabel((fa if FA else en)[(st + i) % 7]); l.setAlignment(AC); l.setObjectName("dim"); s.grid.addWidget(l, 0, i)
        off = (to_g(y, m, 1).weekday() - st) % 7
        for d in range(1, mlen(y, m) + 1):
            g = to_g(y, m, d); b = QPushButton(D(d)); b.setObjectName("cell")
            for k, val in (("sel", g == s.sel), ("today", g == date.today()), ("has", g.isoformat() in s.marks)): b.setProperty(k, "true" if val else "false")
            b.clicked.connect(lambda _, g=g: s.pick(g)); s.grid.addWidget(b, 1 + (off + d - 1) // 7, (off + d - 1) % 7)
    def pick(s, g): s.sel = g; s.build(); s.picked.emit(g)

class TaskRow(QWidget):
    def __init__(s, m, r):
        super().__init__(); s.m = m; s.id = r["id"]; h = QHBoxLayout(s); h.setContentsMargins(12, 8, 12, 8); h.setSpacing(12)
        s.cb = QCheckBox(); s.cb.setObjectName("round"); s.cb.setProperty("pri", str(r["priority"])); s.cb.setChecked(bool(r["done"])); s.cb.clicked.connect(s.click)
        v = QVBoxLayout(); v.setSpacing(2); t = QLabel(r["title"]); f = t.font(); f.setPointSize(11); f.setStrikeOut(bool(r["done"])); t.setFont(f)
        if r["done"]: t.setStyleSheet(f"color:{pal()['D']}")
        v.addWidget(t); mt = m.meta(r)
        if mt: ml = QLabel(mt); ml.setStyleSheet("font-size:12px"); v.addWidget(ml)
        h.addWidget(s.cb); h.addLayout(v, 1)
        if r["pinned"]: st = QLabel("★"); st.setStyleSheet(f"color:{ACC};font-size:16px"); h.addWidget(st)
    def click(s, on):
        m, i = s.m, s.id
        if not ANIM: return m.set_done(i, on)
        e = QGraphicsOpacityEffect(s); s.setGraphicsEffect(e); a = QPropertyAnimation(e, b"opacity", s); a.setDuration(350); a.setStartValue(1.0); a.setEndValue(0.0)
        a.finished.connect(lambda: QTimer.singleShot(0, lambda: m.set_done(i, on))); a.start(); s._a = a

class Main(QMainWindow):
    def __init__(s, hidden=False):
        global FA, JAL, H24, ACC, LIGHT, ANIM, SOUND
        super().__init__(); s.setWindowTitle("SAReminder"); s.resize(1220, 780); s.quitting = False; s.popups = []; s.hidden = hidden; s.tkey = "f:today"
        s.db = sqlite3.connect(DB); s.db.row_factory = sqlite3.Row; s.db.executescript(SCHEMA)
        cols = {r[1] for r in s.db.execute("PRAGMA table_info(tasks)")}
        for c, d in (("tags", "TEXT DEFAULT ''"), ("pinned", "INTEGER DEFAULT 0"), ("recur", "INTEGER DEFAULT 0"), ("done_at", "TEXT"), ("list_id", "INTEGER"), ("checklist", "TEXT DEFAULT '[]'")):
            if c not in cols: s.db.execute(f"ALTER TABLE tasks ADD COLUMN {c} {d}")
        FA = s.get("lang", "en") == "fa"; JAL = s.get("jal", "1" if FA else "0") == "1"; H24 = s.get("h24", "1") == "1"; ACC = s.get("accent", ACC)
        LIGHT = s.get("light", "0") == "1"; ANIM = s.get("anim", "1") == "1"; SOUND = s.get("snd", "1") == "1"; s.setWindowIcon(logo()); s.load_lists()
        root = QWidget(); root.setObjectName("root"); s.setCentralWidget(root); out = QVBoxLayout(root); out.setContentsMargins(0, 0, 0, 0); out.setSpacing(0)
        body = QHBoxLayout(); body.setSpacing(0); out.addLayout(body, 1); s.side = QListWidget(); s.side.setObjectName("side"); s.pages = QStackedWidget(); body.addWidget(s.side); body.addWidget(s.pages, 1)
        for f in (s.p_tasks, s.p_dash, s.p_cal, s.p_pomo, s.p_habits, s.p_notes, s.p_set): s.pages.addWidget(f())
        ft = QLabel("© Copyright © Sadroddin Aghaei. All Rights Reserved."); ft.setObjectName("foot"); ft.setAlignment(AC); out.addWidget(ft)
        s.tray = QSystemTrayIcon(logo(), s); mn = QMenu(); mn.addAction("SAReminder", s.showNormal); mn.addAction(L("add"), s.new_task); mn.addAction("Quit", s.quit)
        s.tray.setContextMenu(mn); s.tray.activated.connect(lambda _: s.showNormal()); s.tray.show()
        s.side.currentItemChanged.connect(s.nav); s.side.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); s.side.customContextMenuRequested.connect(s.side_menu)
        for i, k in enumerate(("f:today", "p:dash", "p:cal", "p:pomo", "p:habits", "p:notes", "p:settings")): QShortcut(QKeySequence(f"Ctrl+{i+1}"), s, activated=lambda k=k: s.goto(k))
        QShortcut(QKeySequence("Ctrl+N"), s, activated=s.new_task); QShortcut(QKeySequence("Ctrl+F"), s, activated=lambda: (s.goto("f:all"), s.q.setFocus()))
        QShortcut(QKeySequence("Delete"), s.list, activated=s.remove, context=Qt.ShortcutContext.WidgetShortcut)
        s.build_side("f:today"); s.timer = QTimer(s); s.timer.timeout.connect(s.check); s.timer.start(20000); s.check()
    def get(s, k, d=None): r = s.db.execute("SELECT v FROM settings WHERE k=?", (k,)).fetchone(); return r["v"] if r else d
    def put(s, k, v): s.db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (k, str(v))); s.db.commit()
    def now(s): return datetime.now().strftime(FMT)
    def load_lists(s): s.lists = {r["id"]: (r["name"], r["color"]) for r in s.db.execute("SELECT * FROM lists")}
    # ---- sidebar / navigation
    def build_side(s, keep):
        s.side.blockSignals(True); s.side.clear(); P = pal(); target = None
        def add(txt, key, hdr=False, ic=None):
            it = QListWidgetItem(txt); it.setData(UR, key); it.setData(UR + 1, txt)
            if ic: it.setIcon(ic)
            if hdr: it.setFlags(Qt.ItemFlag.NoItemFlags); it.setForeground(QColor(P["D"])); f = it.font(); f.setPointSize(9); f.setBold(True); it.setFont(f)
            s.side.addItem(it); return it
        for (k, ic), n in zip(SMART, LS("sm")): add(f"{ic}  {n}", "f:" + k)
        add(L("hl"), "h", True)
        for i, (n, c) in s.lists.items(): add(n, f"l:{i}", ic=dot(c))
        add(L("newlist"), "newlist")
        add(L("ht"), "h2", True)
        for ic, k in (("▦", "dash"), ("▤", "cal"), ("◔", "pomo"), ("♨", "habits"), ("✎", "notes"), ("⚙", "settings")): add(f"{ic}  {L(k)}", "p:" + k)
        s.side.blockSignals(False)
        for i in range(s.side.count()):
            if s.side.item(i).data(UR) == keep: s.side.setCurrentRow(i); break
    def goto(s, key):
        for i in range(s.side.count()):
            if s.side.item(i).data(UR) == key: s.side.setCurrentRow(i); return
    def nav(s, cur, prev):
        if not cur: return
        k = cur.data(UR)
        if k == "newlist":
            s.side.blockSignals(True); prev and s.side.setCurrentItem(prev); s.side.blockSignals(False); return QTimer.singleShot(0, s.new_list)
        if k.startswith("p:"): s.pages.setCurrentIndex({"dash": 1, "cal": 2, "pomo": 3, "habits": 4, "notes": 5, "settings": 6}[k[2:]])
        else: s.tkey = k; s.pages.setCurrentIndex(0); s.refresh()
        fade(s.pages.currentWidget(), 220)
    def new_list(s):
        n, ok = QInputDialog.getText(s, "SAReminder", L("newlname"))
        if ok and n.strip():
            c = ACCENTS[len(s.lists) % len(ACCENTS)]; i = s.db.execute("INSERT INTO lists(name,color) VALUES(?,?)", (n.strip(), c)).lastrowid; s.db.commit(); s.load_lists(); s.build_side(f"l:{i}")
        else: s.goto(s.tkey)
    def side_menu(s, pos):
        it = s.side.itemAt(pos)
        if it and it.data(UR).startswith("l:"):
            m = QMenu(s); m.addAction(L("dellist"), lambda: s.del_list(int(it.data(UR)[2:]))); m.exec(s.side.mapToGlobal(pos))
    def del_list(s, i):
        s.db.execute("UPDATE tasks SET list_id=NULL WHERE list_id=?", (i,)); s.db.execute("DELETE FROM lists WHERE id=?", (i,)); s.db.commit(); s.load_lists(); s.build_side("f:all")
    # ---- pages
    def card(s, key, color):
        f = QFrame(); f.setObjectName("card"); v = QVBoxLayout(f); a = QLabel(L(key)); a.setObjectName("dim"); b = QLabel("0"); b.setObjectName("big"); v.addWidget(a); v.addWidget(b); f.val = b; f.col = color; return f
    def p_dash(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(32, 24, 32, 16); h = QLabel(L("dash")); h.setObjectName("h1"); v.addWidget(h); r = QHBoxLayout(); v.addLayout(r)
        s.c = {k: s.card(k, col) for k, col in (("today", None), ("over", "#ff4d4f"), ("comp", "#3ddc84"), ("streak", "#ffb020"))}; [r.addWidget(c) for c in s.c.values()]
        a = QLabel(L("prog")); a.setObjectName("h2"); s.bar = QProgressBar(); s.bar.setRange(0, 100); b = QLabel(L("wk")); b.setObjectName("h2"); s.bars = Bars(); u = QLabel(L("up")); u.setObjectName("h2"); s.upl = QListWidget()
        [v.addWidget(x) for x in (a, s.bar, b, s.bars, u)]; v.addWidget(s.upl, 1); return w
    def p_tasks(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(32, 24, 32, 12); h = QHBoxLayout(); v.addLayout(h); s.ttl = QLabel(); s.ttl.setObjectName("h1")
        s.q = QLineEdit(); s.q.setPlaceholderText(L("search")); s.q.setFixedWidth(200); s.q.textChanged.connect(s.refresh)
        s.sort = QComboBox(); s.sort.addItems(LS("sortl")); s.sort.currentIndexChanged.connect(s.refresh); nb = QPushButton("＋"); nb.setObjectName("primary"); nb.setFixedWidth(46); nb.clicked.connect(s.new_task)
        h.addWidget(s.ttl, 1); [h.addWidget(x) for x in (s.q, s.sort, nb)]
        s.qa = QLineEdit(); s.qa.setObjectName("quick"); s.qa.setPlaceholderText(L("quick")); s.qa.returnPressed.connect(s.quick_add); v.addWidget(s.qa)
        s.list = QListWidget(); s.list.setObjectName("tl"); s.list.itemDoubleClicked.connect(lambda _: s.edit()); s.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        s.list.customContextMenuRequested.connect(s.task_menu); v.addWidget(s.list, 1); return w
    def p_cal(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(32, 24, 32, 16); s.cv = CalView(); s.cv.picked.connect(s.day); v.addWidget(s.cv, 3)
        s.dayl = QListWidget(); v.addWidget(s.dayl, 2); b = QPushButton(L("addday")); b.clicked.connect(lambda: s.new_task(s.cv.sel)); v.addWidget(b); return w
    def p_pomo(s):
        w = QWidget(); v = QVBoxLayout(w); v.setAlignment(AC); s.pm = "work"; s.left = 25 * 60; s.pt = QTimer(s); s.pt.timeout.connect(s.tick); s.ring = Ring()
        s.ml = QLabel(L("work")); s.ml.setObjectName("h2"); s.ml.setAlignment(AC); s.wk = QSpinBox(); s.wk.setRange(1, 180); s.wk.setValue(25); s.bk = QSpinBox(); s.bk.setRange(1, 60); s.bk.setValue(5)
        r = QHBoxLayout(); sb = QPushButton(L("start")); sb.setObjectName("primary"); pb = QPushButton(L("pause")); rb = QPushButton(L("reset")); sb.clicked.connect(lambda: s.pt.start(1000)); pb.clicked.connect(s.pt.stop); rb.clicked.connect(s.preset)
        [r.addWidget(x) for x in (sb, pb, rb)]; s.sl = QLabel(); s.sl.setObjectName("dim"); s.sl.setAlignment(AC); r2 = QHBoxLayout(); r2.addStretch(); [r2.addWidget(x) for x in (QLabel(L("work")), s.wk, QLabel(L("brk")), s.bk)]; r2.addStretch()
        v.addWidget(s.ml); v.addWidget(s.ring, 1); v.addLayout(r); v.addLayout(r2); v.addWidget(s.sl); s.preset(); return w
    def preset(s): s.pt.stop(); s.pm = "work"; s.left = s.wk.value() * 60; s.ml.setText(L("work")); s.tick(0)
    def tick(s, d=1):
        s.left -= d; tot = (s.bk.value() if s.pm == "brk" else s.wk.value()) * 60
        if s.left <= 0:
            if s.pm == "work": k = "pomo_" + date.today().isoformat(); s.put(k, int(s.get(k, 0)) + 1)
            s.pm = "brk" if s.pm == "work" else "work"; tot = s.left = (s.bk.value() if s.pm == "brk" else s.wk.value()) * 60; s.ml.setText(L(s.pm)); s.tray.showMessage("SAReminder", L(s.pm), INFO, 6000); s.beep()
        s.ring.set(s.left / tot, D(f"{s.left//60:02d}:{s.left%60:02d}")); s.sl.setText(f"{L('sess')}: {D(s.get('pomo_' + date.today().isoformat(), 0))}")
    def beep(s): SOUND and QApplication.beep()
    def p_habits(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(32, 24, 32, 16); r = QHBoxLayout(); v.addLayout(r); s.hl = QListWidget(); v.addWidget(s.hl)
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
            days = {r[0] for r in s.db.execute("SELECT day FROM habit_log WHERE habit_id=?", (h["id"],))}; wk = " ".join("●" if (date.today() - timedelta(days=i)).isoformat() in days else "○" for i in range(6, -1, -1))
            it = QListWidgetItem(f"{h['name']}      {wk}      🔥 {D(s.streak_of(days))}"); it.setData(UR, h["id"]); s.hl.addItem(it)
    def new_habit(s):
        n, ok = QInputDialog.getText(s, "SAReminder", L("nh"))
        if ok and n.strip(): s.db.execute("INSERT INTO habits(name) VALUES(?)", (n.strip(),)); s.db.commit(); s.hab()
    def hab_toggle(s):
        i = s.hl.currentItem()
        if not i: return
        h, t = i.data(UR), date.today().isoformat()
        if s.db.execute("SELECT 1 FROM habit_log WHERE habit_id=? AND day=?", (h, t)).fetchone(): s.db.execute("DELETE FROM habit_log WHERE habit_id=? AND day=?", (h, t))
        else: s.db.execute("INSERT INTO habit_log VALUES(?,?)", (h, t))
        s.db.commit(); s.hab()
    def hab_del(s):
        i = s.hl.currentItem()
        if i: s.db.execute("DELETE FROM habits WHERE id=?", (i.data(UR),)); s.db.execute("DELETE FROM habit_log WHERE habit_id=?", (i.data(UR),)); s.db.commit(); s.hab()
    def p_notes(s):
        w = QWidget(); v = QHBoxLayout(w); v.setContentsMargins(32, 24, 32, 16); lv = QVBoxLayout(); v.addLayout(lv, 1); s.nl = QListWidget(); lv.addWidget(s.nl)
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
        if s.cur: b = s.ne.toPlainText(); t = b.strip().split("\n")[0][:40]; s.db.execute("UPDATE notes SET title=?,body=?,updated=? WHERE id=?", (t, b, s.now(), s.cur)); s.db.commit(); i = s.nl.currentItem(); i and i.setText(t or "—")
    def del_note(s):
        if s.cur: s.db.execute("DELETE FROM notes WHERE id=?", (s.cur,)); s.db.commit(); s.cur = None; s.ne.clear(); s.notes()
    def p_set(s):
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(32, 24, 32, 16); v.setAlignment(Qt.AlignmentFlag.AlignTop)
        def sec(k): l = QLabel(L(k)); l.setObjectName("h2"); v.addWidget(l)
        def cbx(k, key, val, en=True): c = QCheckBox(L(k)); c.setChecked(val); c.setEnabled(en); c.toggled.connect(lambda on: s.opt(key, "1" if on else "0")); v.addWidget(c); return c
        sec("setth"); r = QHBoxLayout(); v.addLayout(r); r.addWidget(QLabel(L("accent")))
        for c in ACCENTS:
            b = QPushButton(); b.setFixedSize(30, 30); b.setStyleSheet(f"QPushButton{{background:{c};border-radius:15px;border:2px solid transparent}}QPushButton:hover{{border-color:#888}}"); b.clicked.connect(lambda _, c=c: s.set_accent(c)); r.addWidget(b)
        cb = QPushButton(L("custom")); cb.clicked.connect(lambda: (lambda c: c.isValid() and s.set_accent(c.name()))(QColorDialog.getColor(QColor(ACC), s))); r.addWidget(cb); r.addStretch()
        th = QComboBox(); th.addItems(LS("theme")); th.setCurrentIndex(int(LIGHT)); th.activated.connect(lambda i: s.opt("light", str(i))); v.addWidget(th); cbx("anim", "anim", ANIM)
        sec("gen"); v.addWidget(QLabel(L("lang"))); c = QComboBox(); c.addItem("English", "en"); c.addItem("فارسی", "fa"); c.setCurrentIndex(int(FA)); c.activated.connect(lambda i: s.change_lang(c.itemData(i))); v.addWidget(c)
        cbx("jal", "jal", JAL); cbx("h24", "h24", H24); cbx("snd", "snd", SOUND); a = cbx("auto", "auto", False, sys.platform == "win32" and getattr(sys, "frozen", False))
        v.addWidget(QLabel(L("defrem"))); dr = QComboBox(); dr.addItem(L("now"), 0); [dr.addItem(f"{D(m)} {L('mn')}", m) for m in (5, 15, 30, 60)]; dr.setCurrentIndex(max(0, dr.findData(int(s.get("defrem", 0)))))
        dr.activated.connect(lambda i: s.put("defrem", dr.itemData(i))); v.addWidget(dr); sec("data")
        for k, f in (("exp", s.export), ("imp", s.imp), ("folder", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(DIR))))): b = QPushButton(L(k)); b.clicked.connect(f); v.addWidget(b)
        return w
    def set_accent(s, c): global ACC; ACC = c; s.put("accent", c); s.restyle()
    def opt(s, k, v):
        global LIGHT, ANIM, SOUND, JAL, H24
        if k == "auto": return s.autostart(v == "1")
        s.put(k, v)
        if k == "light": LIGHT = v == "1"
        elif k == "anim": ANIM = v == "1"
        elif k == "snd": SOUND = v == "1"
        elif k == "jal": JAL = v == "1"; s.cv.cur = from_g(s.cv.sel)[:2]
        elif k == "h24": H24 = v == "1"
        s.restyle()
    def restyle(s):
        QApplication.instance().setStyleSheet(qss()); ic = logo(); s.setWindowIcon(ic); s.tray.setIcon(ic); s.refresh(); s.cv.build(); s.hab()
        s.ring.update(); s.bars.update(); s.build_side(s.side.currentItem().data(UR) if s.side.currentItem() else "f:today")
    def change_lang(s, v):
        s.put("lang", v)
        if s.get("jal") is None: s.put("jal", "1" if v == "fa" else "0")
        QProcess.startDetached(sys.executable, sys.argv[1:] if getattr(sys, "frozen", False) else sys.argv); s.quit()
    def autostart(s, on):
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if on: winreg.SetValueEx(k, "SAReminder", 0, winreg.REG_SZ, f'"{sys.executable}" --hidden')
        else:
            try: winreg.DeleteValue(k, "SAReminder")
            except FileNotFoundError: pass
    # ---- tasks
    def toast(s, msg):
        t = QLabel(msg, s); t.setObjectName("toast"); t.setStyleSheet(f"background:{ACC};color:#fff;border-radius:20px;padding:0 22px;font-weight:600"); t.setAlignment(AC); t.adjustSize(); t.resize(t.width() + 44, 40)
        t.move((s.width() - t.width()) // 2, s.height() - 110); t.show(); t.raise_(); fade(t, 200); QTimer.singleShot(1800, lambda: s.toast_out(t))
    def toast_out(s, t):
        if not ANIM: return t.deleteLater()
        e = QGraphicsOpacityEffect(t); t.setGraphicsEffect(e); a = QPropertyAnimation(e, b"opacity", t); a.setDuration(300); a.setStartValue(1.0); a.setEndValue(0.0); a.finished.connect(t.deleteLater); a.start(); t._a = a
    def meta(s, r):
        P = pal(); n = s.now(); x = []
        if r["due_at"]:
            col = "#ff4d4f" if r["due_at"] < n and not r["done"] else ACC if r["due_at"][:10] == n[:10] else P["D"]; x.append(f"<span style='color:{col}'>{rel(r['due_at'])}</span>")
        if r["list_id"] in s.lists: nm, c = s.lists[r["list_id"]]; x.append(f"<span style='color:{c}'>● {nm}</span>")
        for g in (r["tags"] or "").split(","):
            if g.strip(): x.append(f"<span style='color:{P['D']}'>#{g.strip()}</span>")
        cl = json.loads(r["checklist"] or "[]")
        if cl: x.append(f"<span style='color:{P['D']}'>☑ {D(sum(1 for _, d in cl if d))}/{D(len(cl))}</span>")
        if r["recur"]: x.append(f"<span style='color:{P['D']}'>⟳</span>")
        if r["notes"]: x.append(f"<span style='color:{P['D']}'>≡</span>")
        return "&nbsp;&nbsp;".join(x)
    def save(s, d, id=None):
        d = {k: d.get(k) for k in TKEYS} | {"checklist": d.get("checklist") or "[]"}
        if id: s.db.execute("UPDATE tasks SET title=:title,notes=:notes,tags=:tags,priority=:priority,due_at=:due_at,remind_min=:remind_min,trigger_at=:trigger_at,recur=:recur,pinned=:pinned,list_id=:list_id,checklist=:checklist,notified=0,updated_at=CURRENT_TIMESTAMP WHERE id=:id", {**d, "id": id})
        else: s.db.execute("INSERT INTO tasks(title,notes,tags,priority,due_at,remind_min,trigger_at,recur,pinned,list_id,checklist) VALUES(:title,:notes,:tags,:priority,:due_at,:remind_min,:trigger_at,:recur,:pinned,:list_id,:checklist)", d)
        s.db.commit(); s.refresh(); s.check()
    def quick_add(s):
        t, tags, pri, d, tm = parse_quick(s.qa.text())
        if not t: return QMessageBox.warning(s, "SAReminder", L("empty"))
        now = datetime.now(); m = int(s.get("defrem", 0))
        if d is None and s.tkey == "f:today": d = date.today()
        if d is None and s.tkey == "f:tomorrow": d = date.today() + timedelta(days=1)
        due = trig = None
        if d is not None:
            dt = datetime.combine(d, QTime(*tm).toPython()) if tm else datetime.combine(d, (now + timedelta(hours=1)).time().replace(second=0, microsecond=0)) if d == date.today() else datetime.combine(d, QTime(9, 0).toPython())
            if d == date.today() and not tm and dt.date() != d: dt = datetime.combine(d, QTime(23, 59).toPython())
            due = dt.strftime(FMT); trig = (dt - timedelta(minutes=m)).strftime(FMT)
        s.save(dict(title=t, tags=",".join(tags), priority=pri, due_at=due, remind_min=m, trigger_at=trig, recur=0, pinned=0, list_id=int(s.tkey[2:]) if s.tkey.startswith("l:") else None))
        s.qa.clear(); s.toast(L("added"))
    def new_task(s, day=None):
        dl = TaskDialog(s, day=day if isinstance(day, date) else None, list_id=int(s.tkey[2:]) if s.tkey.startswith("l:") else None)
        if dl.exec(): s.save(dl.data()); s.toast(L("added"))
    def sel(s): i = s.list.currentItem(); return s.db.execute("SELECT * FROM tasks WHERE id=?", (i.data(UR),)).fetchone() if i and i.data(UR) else None
    def edit(s):
        r = s.sel()
        if r:
            dl = TaskDialog(s, r)
            if dl.exec(): s.save(dl.data(), r["id"])
    def dup(s):
        r = s.sel()
        if r: d = {k: r[k] for k in TKEYS}; d["title"] += " (2)"; s.save(d)
    def star(s):
        r = s.sel()
        if r: s.db.execute("UPDATE tasks SET pinned=1-pinned WHERE id=?", (r["id"],)); s.db.commit(); s.refresh()
    def remove(s):
        r = s.sel()
        if r: s.db.execute("DELETE FROM tasks WHERE id=?", (r["id"],)); s.db.commit(); s.refresh()
    def move(s, lid):
        r = s.sel()
        if r: s.db.execute("UPDATE tasks SET list_id=? WHERE id=?", (lid, r["id"])); s.db.commit(); s.refresh()
    def task_menu(s, pos):
        it = s.list.itemAt(pos)
        if not it or not it.data(UR): return
        s.list.setCurrentItem(it); m = QMenu(s); m.addAction(L("edit"), s.edit); m.addAction(L("dup"), s.dup); m.addAction(L("pin"), s.star); mv = m.addMenu(L("moveto")); mv.addAction(L("nolist"), lambda: s.move(None))
        for i, (n, c) in s.lists.items(): mv.addAction(dot(c), n, lambda i=i: s.move(i))
        m.addSeparator(); m.addAction(L("delete"), s.remove); m.exec(s.list.mapToGlobal(pos))
    def set_done(s, i, on=True):
        r = s.db.execute("SELECT * FROM tasks WHERE id=?", (i,)).fetchone()
        if not r: return
        s.db.execute("UPDATE tasks SET done=?,done_at=? WHERE id=?", (int(on), s.now() if on else None, i))
        if on and r["recur"] and r["due_at"]:
            d = nxt(r["due_at"], r["recur"]); s.db.execute("INSERT INTO tasks(title,notes,tags,priority,due_at,remind_min,trigger_at,recur,pinned,list_id,checklist) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (r["title"], r["notes"], r["tags"], r["priority"], d.strftime(FMT), r["remind_min"], (d - timedelta(minutes=r["remind_min"])).strftime(FMT), r["recur"], r["pinned"], r["list_id"], r["checklist"]))
        s.db.commit(); s.refresh()
    def where(s):
        n = s.now(); t = date.today(); nx = (t + timedelta(days=1)).isoformat(); k = s.tkey
        if k.startswith("l:"): return "list_id=? AND done=0", [int(k[2:])]
        return {"f:all": ("done=0", []), "f:today": ("done=0 AND due_at<?", [nx + "T00:00"]), "f:tomorrow": ("done=0 AND due_at LIKE ?", [nx + "%"]),
                "f:week": ("done=0 AND due_at>=? AND due_at<?", [t.isoformat(), (t + timedelta(days=8)).isoformat()]), "f:over": ("done=0 AND due_at<?", [n]),
                "f:star": ("pinned=1 AND done=0", []), "f:done": ("done=1", [])}.get(k, ("done=0", []))
    def refresh(s, *_):
        like = f"%{s.q.text()}%"; w, a = s.where(); order = ["pinned DESC,due_at IS NULL,due_at", "priority DESC,due_at", "title COLLATE NOCASE", "id DESC"][s.sort.currentIndex()]
        rows = s.db.execute(f"SELECT * FROM tasks WHERE (title LIKE ? OR tags LIKE ? OR notes LIKE ?) AND {w} ORDER BY done,{order}", [like] * 3 + a).fetchall()
        s.list.clear()
        if s.tkey.startswith("l:"): nm = s.lists.get(int(s.tkey[2:]), ("",))[0]
        else: nm = LS("sm")[[k for k, _ in SMART].index(s.tkey[2:])] if s.tkey[2:] in dict(SMART) else ""
        s.ttl.setText(f"{nm}   {D(len(rows))}")
        for r in rows:
            it = QListWidgetItem(); it.setData(UR, r["id"]); row = TaskRow(s, r); it.setSizeHint(QSize(0, max(54, row.sizeHint().height() + 6))); s.list.addItem(it); s.list.setItemWidget(it, row)
        if not rows: it = QListWidgetItem(L("none")); it.setFlags(Qt.ItemFlag.NoItemFlags); it.setTextAlignment(AC); it.setSizeHint(QSize(0, 120)); s.list.addItem(it)
        n = s.now(); t = n[:10]; nx = (date.today() + timedelta(days=1)).isoformat(); q = lambda sql, *p: s.db.execute(sql, p).fetchone()[0]
        cnt = {"f:all": q("SELECT COUNT(*) FROM tasks WHERE done=0"), "f:today": q("SELECT COUNT(*) FROM tasks WHERE done=0 AND due_at<?", nx + "T00:00"), "f:tomorrow": q("SELECT COUNT(*) FROM tasks WHERE done=0 AND due_at LIKE ?", nx + "%"),
               "f:week": q("SELECT COUNT(*) FROM tasks WHERE done=0 AND due_at>=? AND due_at<?", t, (date.today() + timedelta(days=8)).isoformat()), "f:over": q("SELECT COUNT(*) FROM tasks WHERE done=0 AND due_at<?", n), "f:star": q("SELECT COUNT(*) FROM tasks WHERE pinned=1 AND done=0")}
        for i in range(s.side.count()):
            it = s.side.item(i); k = it.data(UR)
            if k in cnt and it.data(UR + 1): it.setText(it.data(UR + 1) + (f"     {D(cnt[k])}" if cnt[k] else ""))
        s.tray.setToolTip(f"SAReminder — {L('today')}: {D(cnt['f:today'])}")
        td, dn = q("SELECT COUNT(*) FROM tasks WHERE due_at LIKE ? AND done=0", t + "%"), q("SELECT COUNT(*) FROM tasks WHERE done_at LIKE ?", t + "%")
        vals = {"today": td, "over": cnt["f:over"], "comp": q("SELECT COUNT(*) FROM tasks WHERE done=1"), "streak": s.streak_of({r[0] for r in s.db.execute("SELECT DISTINCT substr(done_at,1,10) FROM tasks WHERE done_at IS NOT NULL")})}
        for k, c in s.c.items(): count_to(c.val, vals[k]); c.val.setStyleSheet(f"color:{c.col or ACC}")
        tgt = int(100 * dn / (td + dn)) if td + dn else 0
        if ANIM: an = QPropertyAnimation(s.bar, b"value", s); an.setDuration(500); an.setStartValue(s.bar.value()); an.setEndValue(tgt); an.start(); s.bar._a = an
        else: s.bar.setValue(tgt)
        days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]; s.bars.set([(D(from_g(d)[2]), q("SELECT COUNT(*) FROM tasks WHERE done_at LIKE ?", d.isoformat() + "%")) for d in days]); s.upl.clear()
        for r in s.db.execute("SELECT * FROM tasks WHERE done=0 AND due_at>=? ORDER BY due_at LIMIT 8", (n,)): s.upl.addItem(f"{rel(r['due_at'])}     {r['title']}")
        s.cv.marks = {r[0] for r in s.db.execute("SELECT DISTINCT substr(due_at,1,10) FROM tasks WHERE due_at IS NOT NULL AND done=0")}; s.cv.build(); s.day(s.cv.sel)
    def day(s, g):
        s.dayl.clear()
        for r in s.db.execute("SELECT * FROM tasks WHERE due_at LIKE ? ORDER BY due_at", (g.isoformat() + "%",)): s.dayl.addItem(f"{rel(r['due_at'])}     {r['title']}")
        if not s.dayl.count(): s.dayl.addItem(L("nodue"))
    def check(s):
        for r in s.db.execute("SELECT * FROM tasks WHERE done=0 AND notified=0 AND trigger_at IS NOT NULL AND trigger_at<=?", (s.now(),)).fetchall():
            s.db.execute("UPDATE tasks SET notified=1 WHERE id=?", (r["id"],)); s.db.commit(); s.tray.showMessage("SAReminder", r["title"], INFO, 10000); s.beep()
            b = QMessageBox(s); b.setWindowTitle("SAReminder"); b.setText(r["title"]); b.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            sn = b.addButton(L("snz"), QMessageBox.ButtonRole.ActionRole); ok = b.addButton(L("cmp"), QMessageBox.ButtonRole.AcceptRole); b.addButton(L("dis"), QMessageBox.ButtonRole.RejectRole)
            b.buttonClicked.connect(lambda btn, i=r["id"], sn=sn, ok=ok: s.act(btn, sn, ok, i)); b.show(); s.popups.append(b)
    def act(s, btn, sn, ok, i):
        if btn is sn: s.db.execute("UPDATE tasks SET trigger_at=?,notified=0 WHERE id=?", ((datetime.now() + timedelta(minutes=10)).strftime(FMT), i)); s.db.commit(); s.refresh()
        elif btn is ok: s.set_done(i)
    T4 = ("tasks", "habits", "habit_log", "notes", "lists")
    def export(s):
        p, _ = QFileDialog.getSaveFileName(s, "", "sareminder-backup.json", "JSON (*.json)")
        if p: Path(p).write_text(json.dumps({t: [dict(r) for r in s.db.execute(f"SELECT * FROM {t}")] for t in s.T4}, ensure_ascii=False, indent=1), "utf-8")
    def imp(s):
        p, _ = QFileDialog.getOpenFileName(s, "", "", "JSON (*.json)")
        if not p: return
        try:
            data = json.loads(Path(p).read_text("utf-8")); data = data if isinstance(data, dict) else {"tasks": data}
            for t, rows in data.items():
                if t not in s.T4: continue
                cols = [r[1] for r in s.db.execute(f"PRAGMA table_info({t})")]
                for r in rows: ks = [k for k in r if k in cols and k != "id"]; s.db.execute(f"INSERT OR IGNORE INTO {t}({','.join(ks)}) VALUES({','.join('?'*len(ks))})", [r[k] for k in ks])
            s.db.commit(); s.load_lists(); s.build_side("f:today"); s.hab(); s.notes()
        except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as e: QMessageBox.critical(s, "SAReminder", str(e))
    def closeEvent(s, e):
        if s.quitting: return e.accept()
        e.ignore(); s.hide(); s.tray.showMessage("SAReminder", L("tray"), INFO, 2500)
    def quit(s): s.quitting = True; QApplication.quit()

if __name__ == "__main__":
    a = QApplication(sys.argv); a.setQuitOnLastWindowClosed(False); w = Main("--hidden" in sys.argv); a.setStyleSheet(qss())
    if FA: a.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    if not w.hidden:
        w.show()
        if ANIM: w.setWindowOpacity(0); an = QPropertyAnimation(w, b"windowOpacity", w); an.setDuration(350); an.setStartValue(0.0); an.setEndValue(1.0); an.start(); w._a = an
    sys.exit(a.exec())
