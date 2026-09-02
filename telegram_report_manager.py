import re
# (place this import near the top with your other imports)

EMAIL_REGEX = re.compile(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")

def validate_email(addr: str) -> bool:
    return bool(EMAIL_REGEX.fullmatch(addr))


def load_emails(boxes):
    """Load saved emails from DB into the provided entry boxes list."""
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT address FROM emails ORDER BY id")
    emails = [x[0] for x in cur.fetchall()]
    conn.close()

    # boxes is a list of tk.Entry widgets
    for i, box in enumerate(boxes):
        box.delete(0, tk.END)
        if i < len(emails):
            box.insert(0, emails[i])


def save_emails(boxes):
    """Save up to 6 emails from provided entry boxes into the DB (with validation)."""
    addresses = [
        box.get().strip()
        for box in boxes
        if box.get().strip()
    ]

    # Validate addresses
    for addr in addresses:
        if not validate_email(addr):
            messagebox.showwarning(
                "فرمت ایمیل نامعتبر",
                f"آدرس ایمیل نامعتبر: {addr}"
            )
            return

    # Keep only first 6
    addresses = addresses[:6]

    with db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM emails")
        # Use INSERT OR IGNORE so duplicates won't crash (there is UNIQUE constraint)
        for address in addresses:
            cur.execute(
                "INSERT OR IGNORE INTO emails(address) VALUES (?)",
                (address,)
            )
        conn.commit()

        # Count how many we have now
        cur.execute("SELECT COUNT(*) FROM emails")
        count = cur.fetchone()[0]

    refresh_email_list()

    messagebox.showinfo(
        "ذخیره شد",
        f"{count} ایمیل مقصد ذخیره شد."
    )


def get_report_text():
    target_id = id_entry.get().strip()
    link = link_entry.get().strip()
    category = category_box.get().strip()
    description = description_text.get(
        "1.0",
        tk.END
    ).strip()

    return f"""سلام پشتیبانی تلگرام،

مایلم محتوایی که ممکن است قوانین تلگرام را نقض کند گزارش دهم.

نوع گزارش: {category or "مشخص نشده"}

ID هدف:
{target_id or "ارائه نشده"}

لینک:
{link or "ارائه نشده"}

توضیحات:
{description or "توضیح اضافی ارائه نشده."}

لطفاً محتوا را بررسی و در صورت تایید تخلف، اقدام لازم را انجام دهید.

با تشکر.
"""


def save_report():
    target_id = id_entry.get().strip()
    link = link_entry.get().strip()
    category = category_box.get().strip()
    description = description_text.get(
        "1.0",
        tk.END
    ).strip()

    selected_email = email_choice.get().strip()

    if not category:
        messagebox.showwarning(
            "خطا",
            "نوع گزارش را انتخاب کنید."
        )
        return

    if not target_id and not link:
        messagebox.showwarning(
            "خطا",
            "حداقل ID یا لینک را وارد کنید."
        )
        return

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reports
            (
                target_id,
                link,
                category,
                description,
                email,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            target_id,
            link,
            category,
            description,
            selected_email,
            created_at
        ))
        conn.commit()

    generate_report()

    messagebox.showinfo(
        "ثبت شد",
        "گزارش در SQLite ذخیره شد."
    )


# In email_settings(), create boxes list and pass it to load_emails and save_emails.
# Replace the email_settings function's relevant parts with this snippet:

def email_settings():
    window = tk.Toplevel(root)
    window.title("تنظیم ۶ ایمیل")
    window.geometry("600x450")

    tk.Label(
        window,
        text="ایمیل‌های مقصد",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    boxes = []

    for i in range(6):
        frame = tk.Frame(window)
        frame.pack(fill="x", padx=25, pady=5)

        tk.Label(
            frame,
            text=f"ایمیل {i + 1}:",
            width=10
        ).pack(side="left")

        entry = tk.Entry(
            frame,
            width=55
        )
        entry.pack(side="left")

        boxes.append(entry)

    # Set globals only if you still want them elsewhere; otherwise you can avoid globals
    global email1, email2, email3, email4, email5, email6
    email1, email2, email3, email4, email5, email6 = boxes

    # Load existing addresses into the boxes
    load_emails(boxes)

    tk.Button(
        window,
        text="ذخیره ایمیل‌ها",
        width=25,
        command=lambda: save_emails(boxes)
    ).pack(pady=20)