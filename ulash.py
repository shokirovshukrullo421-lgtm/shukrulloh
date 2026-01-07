import psycopg2

# ===== DATABASE GA ULASH =====
def ulash(dbname, password):
    conn = psycopg2.connect(
        dbname=dbname,
        user="postgres",
        password=password,
        host="localhost",
        port="5432"
    )
    return conn

# ===== DATABASE LARNI KO'RISH =====
def databaselarni_korish(user, password):
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = [row[0] for row in cur.fetchall()]
    conn.close()
    return databases

# ===== JADVALLARNI KO'RISH =====
def jadvallarni_korish(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = 'public'
    """)
    return [t[0] for t in cur.fetchall()]

# ===== JADVAL USTUNLARNI KO'RISH =====
def ustunlarni_korish(conn, table_name):
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name=%s
        ORDER BY ordinal_position
    """, (table_name,))
    return cur.fetchall()

# ===== YANGI DATABASE YARATISH =====
def database_yaratish(new_db, user, password):
    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {new_db};")
    conn.close()

# ===== YANGI JADVAL YARATISH =====
def table_yaratish(conn, table_name, columns):
    cur = conn.cursor()
    cols_sql = ", ".join([f"{name} {dtype}" for name, dtype in columns])
    sql = f"""
    CREATE TABLE {table_name} (
        id SERIAL PRIMARY KEY,
        {cols_sql}
    );
    """
    cur.execute(sql)
    conn.commit()

# ===== USTUN KIRITISH =====
def ustunlarni_kiritish():
    columns = []
    print("⚠️  'id' ustuni avtomatik yaratiladi (SERIAL PRIMARY KEY)")

    while True:
        col_name = input("Ustun nomi (chiqish uchun ENTER): ").strip()
        if col_name == "":
            break
        if col_name.lower() == "id":
            print("❌ 'id' ustunini qo‘shish mumkin emas!")
            continue

        print("Type tanlang:")
        print("1. INTEGER")
        print("2. VARCHAR")
        print("3. TEXT")
        print("4. NUMERIC")
        print("5. BOOLEAN")
        type_choice = input("Tanlov: ")

        if type_choice == "1":
            col_type = "INTEGER"
        elif type_choice == "2":
            size = input("VARCHAR uzunligi (masalan 100): ")
            col_type = f"VARCHAR({size})"
        elif type_choice == "3":
            col_type = "TEXT"
        elif type_choice == "4":
            col_type = "NUMERIC"
        elif type_choice == "5":
            col_type = "BOOLEAN"
        else:
            print("❌ Noto‘g‘ri type")
            continue

        columns.append((col_name, col_type))
    return columns

# ===== JADVALGA MA'LUMOT QO'SHISH =====
def jadvalga_malumot_qoshish(conn, table_name):
    cur = conn.cursor()

    # Ustunlarni olish
    cur.execute("""
        SELECT column_name, data_type, is_identity
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cur.fetchall()

    insert_columns = []
    values = []

    print("\n📝 Jadvalga ma’lumot kiriting (bo‘sh qoldirsangiz NULL bo‘ladi):")

    for col_name, col_type, is_identity in columns:
        # id yoki auto-ustunlarni o'tkazib yuboramiz
        if col_name.lower() == "id" or is_identity == "YES":
            continue

        while True:
            value = input(f"{col_name} ({col_type}): ").strip()

            if value == "":
                values.append(None)
                break

            try:
                if col_type in ("integer", "numeric"):
                    values.append(int(value))
                elif col_type == "boolean":
                    values.append(value.lower() in ("true", "1", "yes", "t"))
                else:
                    values.append(value)
                break
            except ValueError:
                print(f"❌ {col_type} turiga mos qiymat kiriting!")

        insert_columns.append(col_name)

    if not insert_columns:
        print("❌ Kiritiladigan ustun yo‘q.")
        return

    placeholders = ", ".join(["%s"] * len(values))
    cols = ", ".join(insert_columns)

    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    cur.execute(sql, values)
    conn.commit()

    print("✅ Ma’lumot muvaffaqiyatli qo‘shildi!")
# ===== MA'LUMOTLARNI KO'RISH =====
def jadval_malumotlarini_korish(conn, table_name, limit=10):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cur.fetchall()
    if not rows:
        print("❌ Jadval bo'sh.")
        return
    for row in rows:
        print(row)
def jadvaldan_qidirish(conn, table_name):
    cur = conn.cursor()

    # 1️⃣ Jadval ustunlarini olish
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cur.fetchall()

    if not columns:
        print("❌ Jadvalda ustun topilmadi.")
        return

    print("\n🔎 Qidirish uchun ustunni tanlang:")
    for i, (col, col_type) in enumerate(columns, start=1):
        print(f"{i}. {col} ({col_type})")

    # 2️⃣ Ustun tanlash
    while True:
        try:
            idx = int(input("Ustun raqamini kiriting: "))
            if 1 <= idx <= len(columns):
                break
            print("❌ Noto‘g‘ri raqam.")
        except ValueError:
            print("❌ Son kiriting.")

    search_column, col_type = columns[idx - 1]

    # 3️⃣ Qidiriladigan qiymat
    value = input(f"🔍 {search_column} bo‘yicha qidiriladigan qiymat: ").strip()
    if not value:
        print("❌ Qiymat kiritilmadi.")
        return

    # 4️⃣ SQL (type ga qarab)
    if col_type in ("integer", "bigint", "numeric", "smallint"):
        sql = f"SELECT * FROM {table_name} WHERE {search_column} = %s"
        params = (value,)
    else:
        sql = f"SELECT * FROM {table_name} WHERE {search_column} ILIKE %s"
        params = (f"%{value}%",)

    cur.execute(sql, params)
    rows = cur.fetchall()

    # 5️⃣ Natijani chiqarish
    if not rows:
        print("❌ Mos ma’lumot topilmadi.")
        return

    print("\n✅ Topilgan natijalar:\n")

    headers = [desc[0] for desc in cur.description]
    print(" | ".join(headers))
    print("-" * (len(headers) * 15))

    for row in rows:
        print(" | ".join(str(v) if v is not None else "NULL" for v in row))
def jadvaldan_ochirish(conn, table_name):
    cur = conn.cursor()

    # 1️⃣ Jadval ustunlarini olish
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cur.fetchall()

    if not columns:
        print("❌ Jadval ustunlari topilmadi.")
        return

    print("\n🗑 O‘chirish uchun ustunni tanlang:")
    for i, (col, col_type) in enumerate(columns, start=1):
        print(f"{i}. {col} ({col_type})")

    # 2️⃣ Ustun tanlash
    while True:
        try:
            idx = int(input("Ustun raqamini kiriting: "))
            if 1 <= idx <= len(columns):
                break
            print("❌ Noto‘g‘ri raqam.")
        except ValueError:
            print("❌ Son kiriting.")

    delete_column, col_type = columns[idx - 1]

    # 3️⃣ Qiymat kiritish
    value = input(f"🧹 {delete_column} bo‘yicha o‘chiriladigan qiymat: ").strip()
    if not value:
        print("❌ Qiymat kiritilmadi.")
        return

    # 4️⃣ Avval mavjudligini tekshiramiz
    if col_type in ("integer", "bigint", "numeric", "smallint"):
        check_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {delete_column} = %s"
        params = (value,)
    else:
        check_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {delete_column} ILIKE %s"
        params = (value,)

    cur.execute(check_sql, params)
    count = cur.fetchone()[0]

    if count == 0:
        print("❌ Bunday qiymat topilmadi. O‘chirish amalga oshirilmadi.")
        return

    # 5️⃣ Tasdiqlash (xavfsizlik uchun)
    confirm = input(f"⚠ {count} ta qator o‘chiriladi. Davom etasizmi?\n1.ha:\n2.yo‘q:\n ").lower()
    if confirm not in ("ha", "yes", "1"):
        print("❎ O‘chirish bekor qilindi.")
        return

    # 6️⃣ DELETE
    delete_sql = check_sql.replace("COUNT(*)", "*").replace("SELECT *", "DELETE")
    delete_sql = f"DELETE FROM {table_name} WHERE {delete_column} {'=' if col_type in ('integer','bigint','numeric','smallint') else 'ILIKE'} %s"

    cur.execute(delete_sql, params)
    conn.commit()

    print(f"✅ {count} ta qator muvaffaqiyatli o‘chirildi.")
def jadvalni_yangilash(conn, table_name):
    cur = conn.cursor()

    # id dan tashqari ustunlarni olish
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
          AND column_name <> 'id'
        ORDER BY ordinal_position
    """, (table_name,))
    columns = cur.fetchall()

    if not columns:
        print("❌ Yangilanadigan ustun topilmadi.")
        return

    # -------- USTUN TANLASH (UPDATE) --------
    print("\n✏️ Qaysi ustunni yangilamoqchisiz?")
    for i, (col, col_type) in enumerate(columns, 1):
        print(f"{i}. {col} ({col_type})")

    while True:
        choice = input("Raqamni kiriting (0 = chiqish): ").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(columns)):
            print("❌ Noto‘g‘ri tanlov.")
            continue
        update_col, update_type = columns[int(choice) - 1]
        break

    # -------- WHERE USTUN --------
    print("\n🔎 Qaysi ustun bo‘yicha qator topilsin?")
    for i, (col, col_type) in enumerate(columns, 1):
        print(f"{i}. {col} ({col_type})")

    while True:
        choice = input("Raqamni kiriting (0 = chiqish): ").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(columns)):
            print("❌ Noto‘g‘ri tanlov.")
            continue
        where_col, where_type = columns[int(choice) - 1]
        break

    # -------- ESKI QIYMAT --------
    while True:
        old_value = input(f"{where_col} eski qiymati: ").strip()
        if old_value == "":
            print("❌ Qiymat bo‘sh bo‘lishi mumkin emas.")
            continue
        break

    # -------- YANGI QIYMAT --------
    while True:
        new_value = input(f"{update_col} yangi qiymati: ").strip()
        if new_value == "":
            print("❌ Qiymat bo‘sh bo‘lishi mumkin emas.")
            continue

        try:
            if update_type in ("integer", "numeric"):
                new_value = int(new_value)
            elif update_type == "boolean":
                new_value = new_value.lower() in ("true", "1", "yes", "t")
            break
        except ValueError:
            print(f"❌ {update_type} turiga mos qiymat kiriting!")

    # -------- TYPE MOSLASH --------
    try:
        if where_type in ("integer", "numeric"):
            old_value = int(old_value)
            condition = "="
        else:
            condition = "ILIKE"
    except ValueError:
        print("❌ Qidiruv qiymati noto‘g‘ri turda.")
        return

    # -------- UPDATE --------
    sql = f"""
        UPDATE {table_name}
        SET {update_col} = %s
        WHERE {where_col} {condition} %s
    """

    try:
        cur.execute(sql, (new_value, old_value))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Xatolik yuz berdi:", e)
        return

    if cur.rowcount == 0:
        print("⚠️ Mos keladigan qator topilmadi.")
    else:
        print(f"✅ {cur.rowcount} ta qator muvaffaqiyatli yangilandi.")
def jadvalni_ochirish(conn, table_name):
    cur = conn.cursor()
    confirm = input(f"⚠️ '{table_name}' jadvalini o‘chirilsinmi? (ha/yo‘q): ").lower()
    if confirm != "ha":
        print("❌ Jadval o‘chirish bekor qilindi.")
        return
    try:
        cur.execute(f"DROP TABLE {table_name} CASCADE")
        conn.commit()
        print(f"✅ '{table_name}' jadvali muvaffaqiyatli o‘chirildi!")
    except Exception as e:
        print("❌ Xatolik:", e)
def jadval_nomini_ozgartirish(conn, old_name):
    new_name = input(f"📝 '{old_name}' jadvalining yangi nomi: ").strip()
    if not new_name:
        print("❌ Noto‘g‘ri nom.")
        return
    cur = conn.cursor()
    try:
        cur.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        conn.commit()
        print(f"✅ Jadval nomi '{old_name}' → '{new_name}' ga o‘zgartirildi!")
    except Exception as e:
        print("❌ Xatolik:", e)
def ustun_qoshish(conn, table_name):
    cur = conn.cursor()
    col_name = input("🆕 Qo‘shiladigan ustun nomi: ").strip()
    if not col_name:
        print("❌ Ustun nomi kiritilmadi.")
        return
    print("Type tanlang:\n1. INTEGER\n2. VARCHAR\n3. TEXT\n4. NUMERIC\n5. BOOLEAN")
    type_choice = input("Tanlov: ")
    if type_choice == "1":
        col_type = "INTEGER"
    elif type_choice == "2":
        size = input("VARCHAR uzunligi: ")
        col_type = f"VARCHAR({size})"
    elif type_choice == "3":
        col_type = "TEXT"
    elif type_choice == "4":
        col_type = "NUMERIC"
    elif type_choice == "5":
        col_type = "BOOLEAN"
    else:
        print("❌ Noto‘g‘ri type")
        return

    try:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
        conn.commit()
        print(f"✅ '{col_name}' ustuni muvaffaqiyatli qo‘shildi!")
    except Exception as e:
        print("❌ Xatolik:", e)
def ustun_nomini_ozgartirish(conn, table_name):
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s AND column_name <> 'id'
    """, (table_name,))
    columns = [c[0] for c in cur.fetchall()]
    if not columns:
        print("❌ O‘zgartiriladigan ustun yo‘q.")
        return

    print("📌 Ustunlar:", ", ".join(columns))
    old_name = input("📝 Qaysi ustun nomini o‘zgartirmoqchisiz: ").strip()
    if old_name not in columns:
        print("❌ Bunday ustun mavjud emas.")
        return

    new_name = input(f"🆕 '{old_name}' ning yangi nomi: ").strip()
    if not new_name:
        print("❌ Noto‘g‘ri nom.")
        return

    try:
        cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}")
        conn.commit()
        print(f"✅ Ustun nomi '{old_name}' → '{new_name}' ga o‘zgartirildi!")
    except Exception as e:
        print("❌ Xatolik:", e)
def jadval_boglanishlarini_korish(conn, table_name):
    cur = conn.cursor()

    cur.execute("""
        SELECT
            tc.constraint_name,
            tc.table_name AS from_table,
            kcu.column_name AS from_column,
            ccu.table_name AS to_table,
            ccu.column_name AS to_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND (tc.table_name = %s OR ccu.table_name = %s)
        ORDER BY tc.table_name;
    """, (table_name, table_name))

    rows = cur.fetchall()

    if not rows:
        print("🔍 Bu jadval boshqa jadvallar bilan bog‘lanmagan.")
        return

    print("\n🔗 Jadval bog‘lanishlari:")
    print("-" * 50)

    for _, from_table, from_col, to_table, to_col in rows:
        # FK ustuni unique bo‘lsa → 1–1, bo‘lmasa → 1–N
        cur.execute("""
            SELECT COUNT(*) = COUNT(DISTINCT {col})
            FROM {table}
        """.format(col=from_col, table=from_table))

        is_unique = cur.fetchone()[0]
        relation = "1–1" if is_unique else "1–N"

        print(f"{from_table}.{from_col} → {to_table}.{to_col}   ({relation})")
def jadvallarni_ulash(conn):
    cur = conn.cursor()

    print("\n🔗 Bog‘lanish turini tanlang:")
    print("1. One-to-One (1 ↔ 1)")
    print("2. One-to-Many (1 ↔ N)")
    print("3. Many-to-Many (N ↔ N)")

    choice = input("Tanlov (1/2/3): ").strip()

    if choice not in ("1", "2", "3"):
        print("❌ Noto‘g‘ri tanlov")
        return

    table1 = input("1-jadval nomi: ").strip()
    column1 = input(f"{table1} dagi ustun nomi: ").strip()

    table2 = input("2-jadval nomi: ").strip()
    column2 = input(f"{table2} dagi ustun nomi: ").strip()

    try:
        if choice == "1":
            # ONE TO ONE
            fk_name = f"fk_{table2}_{table1}"

            cur.execute(f"""
                ALTER TABLE {table2}
                ADD CONSTRAINT {fk_name}
                FOREIGN KEY ({column2})
                REFERENCES {table1}({column1})
                UNIQUE
            """)

            conn.commit()
            print(f"✅ One-to-One bog‘landi: {table1}.{column1} ↔ {table2}.{column2}")

        elif choice == "2":
            # ONE TO MANY
            fk_name = f"fk_{table2}_{table1}"

            cur.execute(f"""
                ALTER TABLE {table2}
                ADD CONSTRAINT {fk_name}
                FOREIGN KEY ({column2})
                REFERENCES {table1}({column1})
            """)

            conn.commit()
            print(f"✅ One-to-Many bog‘landi: {table1}.{column1} → {table2}.{column2}")

        elif choice == "3":
            # MANY TO MANY
            junction = input("Bog‘lovchi jadval nomi (masalan: table1_table2): ").strip()

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {junction} (
                    {table1}_{column1} INTEGER REFERENCES {table1}({column1}),
                    {table2}_{column2} INTEGER REFERENCES {table2}({column2}),
                    PRIMARY KEY ({table1}_{column1}, {table2}_{column2})
                )
            """)

            conn.commit()
            print(f"✅ Many-to-Many yaratildi: {junction}")

    except Exception as e:
        conn.rollback()
        print("❌ Xato yuz berdi:")
        print(e)