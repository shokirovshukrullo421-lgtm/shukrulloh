from ulash import (
    ulash,
    databaselarni_korish,
    jadvallarni_korish,
    jadvalga_malumot_qoshish,
    jadval_malumotlarini_korish,
    ustunlarni_korish,
    table_yaratish,
    database_yaratish,
    ustunlarni_kiritish,
    jadvaldan_qidirish,
    jadvaldan_ochirish,
    jadvalni_yangilash,
    jadval_nomini_ozgartirish,
    jadvalni_ochirish,
    ustun_nomini_ozgartirish,
    ustun_qoshish,
    jadval_boglanishlarini_korish,
    jadvallarni_ulash
)

def tanlash_menu(matn, variantlar):
    print("\n" + matn)
    for i, v in enumerate(variantlar, start=1):
        print(f"{i}. {v}")
    print("0. Orqaga")
    while True:
        try:
            choice = int(input("Tanlov: "))
            if choice == 0:
                return None
            if 1 <= choice <= len(variantlar):
                return variantlar[choice - 1]
            print("❌ Noto‘g‘ri tanlov.")
        except ValueError:
            print("❌ Faqat raqam kiriting!")

def main():
    print("🚀 PostgreSQL CLI Manager")

    # ===== DATABASE TANLASH / YARATISH =====
    while True:
        action = tanlash_menu(
            "Asosiy menyu:",
            ["Mavjud databaseni tanlash", "Yangi database yaratish"]
        )
        if action is None:
            print("👋 Dastur tugadi.")
            return

        databases = databaselarni_korish(user="postgres", password="admin1112")

        if action == "Mavjud databaseni tanlash":
            if not databases:
                print("❌ Hozircha database yo‘q.")
                continue
            selected_db = tanlash_menu("📦 Mavjud databaselar:", databases)
            if selected_db:
                break

        elif action == "Yangi database yaratish":
            new_db = input("🆕 Yangi database nomi: ").strip()
            if new_db in databases:
                print("❌ Bunday database allaqachon mavjud!")
                continue
            database_yaratish(new_db, "postgres", "admin1112")
            print(f"✅ '{new_db}' database yaratildi!")
            selected_db = new_db
            break

    # ===== DATABASEGA ULANISH =====
    conn = ulash(selected_db, "admin1112")
    print(f"\n✅ '{selected_db}' bazasiga ulanildi")

    # ===== DATABASE ICHIDA ISHLASH =====
    while True:
        db_action = tanlash_menu(
            f"📦 '{selected_db}' bazasi:",
            ["Jadval tanlash", "Yangi jadval yaratish", "jadvallarni_ulash"]
        )
        if db_action is None:
            break

        tables = jadvallarni_korish(conn)

        # ===== JADVAL TANLASH =====
        if db_action == "Jadval tanlash":
            if not tables:
                print("❌ Bazada hali jadval yo‘q.")
                continue

            selected_table = tanlash_menu("📋 Jadvallar:", tables)
            if not selected_table:
                continue

            while True:
                table_action = tanlash_menu(
                    f"📄 '{selected_table}' jadvali:",
                    ["Ustunlarni ko‘rish", "Ma’lumotlarni ko‘rish", "Ma’lumot qo‘shish", "Jadvaldan qidirish", "Jadvaldan o‘chirish", "Jadvalni yangilash", "Jadval nomini o‘zgartirish", "Ustun nomini o‘zgartirish", "Ustun qo‘shish", "Jadvalni o‘chirish", "Jadval bog‘lanishlarini ko‘rish"]
                )
                if table_action is None:
                    break

                if table_action == "Ustunlarni ko‘rish":
                    columns = ustunlarni_korish(conn, selected_table)
                    print("\n📌 Jadval ustunlari:")
                    for name, dtype in columns:
                        print(f"- {name} ({dtype})")

                elif table_action == "Ma’lumotlarni ko‘rish":
                    jadval_malumotlarini_korish(conn, selected_table, limit=10)

                elif table_action == "Ma’lumot qo‘shish":
                    jadvalga_malumot_qoshish(conn, selected_table)
                elif table_action == "Jadvaldan qidirish":
                    jadvaldan_qidirish(conn, selected_table)
                elif table_action == "Jadvaldan o‘chirish":
                    jadvaldan_ochirish(conn, selected_table)
                elif table_action == jadvalni_yangilash:
                    jadvalni_yangilash(conn, selected_table)
                elif table_action == "Jadval nomini o‘zgartirish":
                    jadval_nomini_ozgartirish(conn, selected_table)
                elif table_action == "Ustun nomini o‘zgartirish":
                    ustun_nomini_ozgartirish(conn, selected_table)
                elif table_action == "Ustun qo‘shish":
                    ustun_qoshish(conn, selected_table)
                elif table_action == "Jadvalni o‘chirish":
                    jadvalni_ochirish(conn, selected_table)
                    print(f"✅ '{selected_table}' jadvali o‘chirildi!")
                    break
                elif table_action == "Jadval bog‘lanishlarini ko‘rish":
                    jadval_boglanishlarini_korish(conn, selected_table)
                    

        # ===== YANGI JADVAL YARATISH =====
        elif db_action == "Yangi jadval yaratish":
            table_name = input("🆕 Yangi jadval nomi: ").strip()
            if table_name in tables:
                print("❌ Bunday jadval allaqachon mavjud!")
                continue

            print("📌 Jadval ustunlarini kiriting:")
            columns = ustunlarni_kiritish()
            if not columns:
                print("❌ Hech qanday ustun kiritilmadi!")
                continue

            table_yaratish(conn, table_name, columns)
            print(f"✅ '{table_name}' jadvali yaratildi!")
        elif db_action == "jadvallarni_ulash":
            jadvallarni_ulash(conn)

    conn.close()
    print("🔒 Ulanish yopildi. Dastur yakunlandi.")

main()
