from ulash import ulash

def login():
    conn = ulash("asd", "admin1112")  # ulash funksiyasini chaqiramiz
    cursor = conn.cursor()

    username = input("Login: ")
    password = input("Parol: ")

    cursor.execute(
        "SELECT id FROM users WHERE username=%s AND password_hash=%s",
        (username, password)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        print("✅ Tizimga muvaffaqiyatli kirdingiz!")
        return user[0]
    else:
        print("❌ Login yoki parol noto‘g‘ri.")
        return None


def register():
    conn = ulash("asd", "admin1112")
    cursor = conn.cursor()

    username = input("Yangi login: ")
    email = input("Email: ")
    password = input("Parol: ")

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        print("✅ Ro‘yxatdan o‘tish muvaffaqiyatli!")
    except:
        conn.rollback()
        print("❌ Bunday login yoki email mavjud.")
    finally:
        cursor.close()
        conn.close()
        

def view_tweets(user_id):
    conn = ulash("asd", "admin1112")
    cursor = conn.cursor()

    # Hamma tweetlarni user va content bilan olish
    cursor.execute("""
        SELECT t.id, u.id, u.username, t.content
        FROM tweets t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """)
    tweets = cursor.fetchall()

    if not tweets:
        print("❌ Hali tweetlar mavjud emas.")
        cursor.close()
        conn.close()
        return

    index = 0
    while True:
        tweet = tweets[index]
        tweet_id, author_id, author_name, content = tweet

        print("\n==============================")
        print(f"Tweet #{tweet_id} | @{author_name}")
        print(f"{content}")
        print("==============================")

        print("\nAmallar:")
        print("1. Like / Unlike")
        print("2. Follow / Unfollow")
        print("3. Keyingi tweet")
        print("4. Oldingi tweet")
        print("5. Chiqish")

        choice = input("Tanlov: ")

        # =========================
        # Like / Unlike
        # =========================
        if choice == "1":
            try:
                cursor.execute(
                    "INSERT INTO likes (user_id, tweet_id) VALUES (%s, %s)",
                    (user_id, tweet_id)
                )
                conn.commit()
                print("❤️ Like boshlandi!")
            except:
                conn.rollback()
                # Agar like allaqachon bo'lsa, unlike qilamiz
                cursor.execute(
                    "DELETE FROM likes WHERE user_id=%s AND tweet_id=%s",
                    (user_id, tweet_id)
                )
                conn.commit()
                print("💔 Like bekor qilindi!")

        # =========================
        # Follow / Unfollow
        # =========================
        elif choice == "2":
            if user_id == author_id:
                print("❌ O'zingizga follow bo'lmaysiz.")
            else:
                try:
                    cursor.execute(
                        "INSERT INTO follows (follower_id, following_id) VALUES (%s, %s)",
                        (user_id, author_id)
                    )
                    conn.commit()
                    print("✅ Follow qilindi!")
                except:
                    conn.rollback()
                    # Agar allaqachon follow bo'lsa, unfollow qilamiz
                    cursor.execute(
                        "DELETE FROM follows WHERE follower_id=%s AND following_id=%s",
                        (user_id, author_id)
                    )
                    conn.commit()
                    print("❌ Follow bekor qilindi!")

        # =========================
        # Keyingi tweet
        # =========================
        elif choice == "3":
            if index < len(tweets) - 1:
                index += 1
            else:
                print("❌ Bu oxirgi tweet.")

        # =========================
        # Oldingi tweet
        # =========================
        elif choice == "4":
            if index > 0:
                index -= 1
            else:
                print("❌ Bu birinchi tweet.")

        # =========================
        # Chiqish
        # =========================
        elif choice == "5":
            break

        else:
            print("❌ Noto‘g‘ri tanlov")

    cursor.close()
    conn.close()

def write_tweet(user_id):
    conn = ulash("asd", "admin1112")
    cursor = conn.cursor()

    print("\n=== Yangi Tweet yozish ===")
    content = input("Tweet matni (280 ta belgi bilan cheklangan): ")

    if len(content) > 280:
        print("❌ Tweet juda uzun. 280 ta belgidan oshmasligi kerak.")
        cursor.close()
        conn.close()
        return

    try:
        cursor.execute(
            "INSERT INTO tweets (user_id, content) VALUES (%s, %s)",
            (user_id, content)
        )
        conn.commit()
        print("✅ Tweet muvaffaqiyatli qo‘shildi!")
    except Exception as e:
        conn.rollback()
        print("❌ Tweet qo‘shishda xatolik yuz berdi:", e)
    finally:
        cursor.close()
        conn.close()
def profile(user_id):
    conn = ulash("asd", "admin1112")
    cursor = conn.cursor()

    # Foydalanuvchi username-ni olish
    cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        print("❌ Foydalanuvchi topilmadi.")
        cursor.close()
        conn.close()
        return
    username = user[0]

    print(f"\n=== Profilim @{username} ===")

    # =========================
    # Followers ro'yxati
    # =========================
    cursor.execute("""
        SELECT u.username
        FROM follows f
        JOIN users u ON f.follower_id = u.id
        WHERE f.following_id=%s
    """, (user_id,))
    followers = cursor.fetchall()
    print(f"\nFollowers ({len(followers)}):")
    if followers:
        for follower in followers:
            print(f" - {follower[0]}")
    else:
        print(" Hali followers yo‘q.")

    # =========================
    # Following ro'yxati
    # =========================
    cursor.execute("""
        SELECT u.username
        FROM follows f
        JOIN users u ON f.following_id = u.id
        WHERE f.follower_id=%s
    """, (user_id,))
    following = cursor.fetchall()
    print(f"\nFollowing ({len(following)}):")
    if following:
        for followee in following:
            print(f" - {followee[0]}")
    else:
        print(" Hali following yo‘q.")

    # =========================
    # O'z tweetlari va like'lar
    # =========================
    cursor.execute("""
        SELECT t.id, t.content, COUNT(l.user_id) AS like_count
        FROM tweets t
        LEFT JOIN likes l ON t.id = l.tweet_id
        WHERE t.user_id=%s
        GROUP BY t.id
        ORDER BY t.created_at DESC
    """, (user_id,))
    tweets = cursor.fetchall()

    if not tweets:
        print("\nHali tweetlar mavjud emas.")
    else:
        print("\nSizning tweetlaringiz va like'lar:")
        for tweet in tweets:
            tweet_id, content, like_count = tweet
            print(f"{tweet_id}. {content} | Likes: {like_count}")

            # Kimlar like qilganini olish
            cursor.execute("""
                SELECT u.username
                FROM likes l
                JOIN users u ON l.user_id = u.id
                WHERE l.tweet_id=%s
            """, (tweet_id,))
            likers = cursor.fetchall()
            if likers:
                liker_names = ", ".join([l[0] for l in likers])
                print(f"   👍 Like qilganlar: {liker_names}")

    # =========================
    # Tweet o'chirish
    # =========================
    while True:
        print("\nAmallar:")
        print("1. Tweet o'chirish")
        print("2. Chiqish")

        choice = input("Tanlov: ")
        if choice == "1":
            tweet_id_del = input("O'chirmoqchi bo'lgan tweet ID: ")
            try:
                cursor.execute(
                    "DELETE FROM tweets WHERE id=%s AND user_id=%s",
                    (tweet_id_del, user_id)
                )
                if cursor.rowcount == 0:
                    print("❌ Tweet topilmadi yoki sizga tegishli emas.")
                else:
                    conn.commit()
                    print("✅ Tweet muvaffaqiyatli o'chirildi!")
            except Exception as e:
                conn.rollback()
                print("❌ Xatolik yuz berdi:", e)
        elif choice == "2":
            break
        else:
            print("❌ Noto‘g‘ri tanlov")

    cursor.close()
    conn.close()
