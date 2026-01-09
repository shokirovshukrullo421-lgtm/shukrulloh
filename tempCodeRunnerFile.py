from f_yalar import login, register

print("=== Twitter CLI ===")

user_id = None
while not user_id:
    print("\n1. Login\n2. Ro‘yxatdan o‘tish")
    choice = input("Tanlov: ")
    if choice == "1":
        user_id = login()
    elif choice == "2":
        register()
        user_id = login()  # registerdan keyin login qilamiz
    else:
        print("❌ Noto‘g‘ri tanlov")