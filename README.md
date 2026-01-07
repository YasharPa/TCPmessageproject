# TCP Message Project - מערכת הודעות מבוססת TCP
פרויקט זה מדגים מימוש של מערכת תקשורת מסוג שרת-לקוח (Client-Server) מעל פרוטוקול TCP/IP, המאפשרת העברת הודעות טקסטואליות בזמן אמת.

המערכת בנויה להתמודד עם חיבורים נכנסים מרובים ולנהל תעבורת מידע אמינה בין הצדדים.

## 🛠 טכנולוגיות וכלים

הפרויקט נכתב בשפת **Python** ועושה שימוש בספריות הליבה (Standard Library) ללא צורך בהתקנות חיצוניות כבדות. הטכנולוגיות המרכזיות כוללות:

* **Python 3:** שפת הפיתוח.
* **Socket API:** ספריית `socket` המשמשת ליצירת נקודות קצה (Endpoints) לתקשורת, ניהול ה-Handshake של TCP, ושליחת/קבלת בייטים של מידע.
* **Threading (Multi-threading):** ספריית `threading` משמשת (בצד השרת) לניהול מספר לקוחות במקביל. כל לקוח שמתחבר מקבל "תהליכון" (Thread) ייעודי המאזין להודעות ממנו, מה שמונע חסימה של השרת הראשי.
* **TCP Protocol:** שימוש בפרוטוקול Transmission Control Protocol להבטחת אמינות, סדר ושלמות הנתונים המועברים.

## 📋 תכולת הפרויקט ומבנה הקוד

הפרויקט מחולק לשני רכיבים עיקריים:

### 1. צד השרת (`server.py`)
השרת הוא "המוח" של המערכת. תפקידיו העיקריים:
* **האזנה (Binding & Listening):** פתיחת Socket והמתנה לחיבורים נכנסים בכתובת IP ופורט מוגדרים.
* **ניהול לקוחות:** קבלת חיבורי לקוחות (Accept) ושיוך כל חיבור ל-Thread נפרד.
* **עיבוד הודעות:** קבלת הודעות מהלקוחות, פענוחן (Decoding) והדפסתן (או הפצתן לשאר הלקוחות, בהתאם ללוגיקה הפנימית).

### 2. צד הלקוח (`client.py`)
הלקוח הוא ממשק המשתמש. תפקידיו העיקריים:
* **יצירת קשר:** ייזום חיבור TCP מול השרת.
* **ממשק קלט:** קבלת טקסט מהמשתמש דרך הטרמינל.
* **שליחת נתונים:** קידוד ההודעות (Encoding) ושליחתן לשרת.

## 🚀 הוראות התקנה והרצה

מכיוון שהפרויקט מתבסס על ספריות מובנות של Python, תהליך ההתקנה פשוט ומהיר.

### דרישות מוקדמות
* Python גרסה 3.6 ומעלה.

### שלב 1: הורדת הפרויקט
שכפלו את המאגר למחשב שלכם:
```bash
git clone [https://github.com/YasharPa/TCPmessageproject.git](https://github.com/YasharPa/TCPmessageproject.git)
cd TCPmessageproject
```

### שלב 2: הגדרות רשת (Network Configuration)
כברירת מחדל, הפרויקט מוגדר לעבוד בסביבה מקומית (`localhost` / `127.0.0.1`), כך שגם השרת וגם הלקוח רצים על אותו המחשב.

**אם ברצונכם להריץ את השרת והלקוח על מחשבים שונים באותה רשת (LAN):**

 1. **איתור כתובת ה-IP של השרת:**
    * פתחו את שורת הפקודה במחשב השרת.
    * ב-Windows הריצו: `ipconfig`
    * ב-Linux/Mac הריצו: `ifconfig`
    * העתיקו את כתובת ה-IPv4 (למשל: `192.168.1.15`).

2.  **עדכון קובץ השרת (`server.py`):**
    * פתחו את הקובץ בעורך טקסט.
    * ודאו שהמשתנה האחראי על הכתובת (לרוב `HOST` או `server_ip`) מוגדר ל-`'0.0.0.0'` (כדי להאזין לכל הכתובות) או לכתובת ה-IP הספציפית של המחשב.

3.  **עדכון קובץ הלקוח (`client.py`):**
    * במחשב בו ירוץ הלקוח, פתחו את הקובץ ושנו את משתנה כתובת היעד (לרוב `HOST` או `SERVER_IP`) לכתובת ה-IP שמצאתם בסעיף 1.

שמרו את השינויים בקבצים.

### שלב 3: הפעלת השרת (Running the Server)
השרת חייב לפעול ראשון כדי להאזין לבקשות התחברות.

1. פתחו חלון טרמינל (Terminal/CMD).
2. נווטו לתיקיית הפרויקט:
   ```bash
   cd TCPmessageproject
   ```

   ### שלב 3: הפעלת השרת (Running the Server)
השרת חייב לפעול ראשון כדי להאזין לבקשות התחברות.

1. פתחו חלון טרמינל (Terminal/CMD).
2. נווטו לתיקיית הפרויקט (`cd TCPmessageproject`).
3. הריצו את הפקודה:

```bash
python server.py
```
*(הערה: במערכות מסוימות יש להשתמש ב-`python3`)*

**אימות:** הטרמינל יציג אינדיקציה שהשרת מאזין (**Listening**). **אין לסגור חלון זה.**

### שלב 4: הפעלת הלקוח (Running the Client)
ניתן להפעיל לקוח אחד או יותר במקביל.

1. פתחו חלון טרמינל **חדש ונפרד** (אל תשתמשו בחלון של השרת).
2. נווטו לתיקיית הפרויקט.
3. הריצו את הפקודה:

```bash
python client.py
```

**שימוש:**
* לאחר החיבור, ניתן להקליד הודעות בטרמינל וללחוץ `Enter` לשליחה.
* ההודעות יתקבלו ויוצגו בחלון השרת (או אצל לקוחות אחרים, בהתאם ללוגיקה בקוד).
* כדי לחבר משתמשים נוספים, פתחו טרמינלים נוספים וחזרו על שלב 4.

---

## 🔧 פתרון תקלות נפוצות

* **Connection Refused:** שגיאה זו מעידה לרוב שהשרת אינו רץ, או שהלקוח מנסה להתחבר לפורט/כתובת שגויים. ודאו ששלב 3 בוצע בהצלחה.
* **Address already in use:** הפורט תפוס. אם סגרתם את השרת וניסיתם להפעיל מיד מחדש, המתינו מספר שניות או שנו את מספר הפורט בקוד (בשני הקבצים).
* **Firewall:** בעבודה בין מחשבים שונים, ודאו שחומת האש אינה חוסמת את הפורט הנבחר.




