import json
import re
import os
import requests
from PIL import Image
from io import BytesIO
from deepface import DeepFace

s = requests.Session()
USN = "Mozilla/5.0 (Linux; Android 13; 21091116UG Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.210 Mobile Safari/537.36 Instagram 314.0.0.20.114 Android (33/13; 440dpi; 1080x2276; Xiaomi/Redmi; 21091116UG; pissarropro; mt6877; en_US; 556277190)"
os.makedirs('image', exist_ok=True)

def clear():
    os.system("clear")

def logon_ig():
    try:
        kuki = open('.kukis.log', 'r').read()
        nama = get_user_name(kuki)
        menu(nama)
    except FileNotFoundError:
        clear()
        coki = input("Masukkan Cookie Anda: ")
        try:
            id = re.search('ds_user_id=(\d+)', str(coki)).group(1)
            lo = s.get(f"https://i.instagram.com/api/v1/users/{id}/info/", headers={"user-agent": USN}, cookies={"cookie": coki})
            x = json.loads(lo.text)["user"]
            nama = x["full_name"]
            user_name = x["username"]
            with open('.username', 'w') as user_file:
                user_file.write(user_name)
            with open('.kukis.log', 'w') as kuki_file:
                kuki_file.write(coki)
            with open('info.json', 'w') as info:
                info.write(json.dumps(x, indent=4))
            print(f"Selamat {nama}, Kamu Berhasil login")
            menu(nama)
        except (ValueError, KeyError, json.decoder.JSONDecodeError, AttributeError):
            exit('[x] Login gagal, silahkan cek akun tumbal anda')
            with open('info.json', 'w') as info:
                info.write(json.dumps(x, indent=4))
        except requests.ConnectionError:
            exit('Tidak ada koneksi internet')

def get_user_name(coki):
    id = re.search('ds_user_id=(\d+)', str(coki)).group(1)
    lo = s.get(f"https://i.instagram.com/api/v1/users/{id}/info/", headers={"user-agent": USN}, cookies={"cookie": coki})
    x = json.loads(lo.text)["user"]
    with open('username_info.json', 'w') as infou:
        infou.write(json.dumps(x, indent=4))
    return x["full_name"]

def download_image(url, filename):
    try:
        response = s.get(url)
        response.raise_for_status()  # Memastikan tidak ada kesalahan saat mengunduh
        img = Image.open(BytesIO(response.content))
        img.save(filename)
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
    except IOError as e:
        print(f"Error saving image: {e}")

def get_follow(usernames):
    for usernam in usernames:
        try:
            url = s.get("https://i.instagram.com/api/v1/users/web_profile_info/?username=%s"%(usernames),headers={"user-agent":USN,"x-ig-app-id":"936619743392459"})
            jsons = url.json()["data"]["user"]
            pengikut = jsons["edge_followed_by"]["count"]
            mengikuti = jsons["edge_follow"]["count"]
            postingan = jsons["edge_owner_to_timeline_media"]["count"]
            with open('follow.json', 'w') as fol:
                fol.write(json.dumps(fol, indent=4))
                fol.close()
            print(url.headers)
        except:
            print(url.headers)
            pengikut = "-"
            mengikuti = "-"
            postingan = "-"
        return pengikut, mengikuti, postingan


def menu(nama):
    clear()
    print(f"Selamat Datang {nama} Di Falcon Eye")
    name = input("Masukkan Nama: ")
    img_ref = input("Masukkan Gambar: ")

    try:
        cookie = open('.kukis.log', 'r').read()
        res = s.get(f'https://www.instagram.com/web/search/topsearch/?count=100000&context=blended&query={name}&rank_token=0.35875757839675004&include_reel=true', cookies={"cookie": cookie}, headers={"user-agent": USN})

        data = json.loads(res.text)
        with open('search.json', 'w') as sj:
            sj.write(json.dumps(data, indent=4))
        print(res.headers)
        total_users = len(data['users'])

        results = []
        count = 0

        for user_data in data['users']:
            if count >= 100:
                break

            user = user_data['user']
            usernames = user['username']
            image_url = user['profile_pic_url']
            fullname = user['full_name']

            temp_image_path = f'image/temp_image_{usernames}.jpg'
            download_image(image_url, temp_image_path)

            pengikut, mengikuti, postingan = get_follow(usernames)

            # Bandingkan gambar
            try:
                result = DeepFace.verify(temp_image_path, img_ref)
                score = result['distance'] if 'distance' in result else 0
                similarity_percentage = max(0, 100 - (score * 100))

                results.append({
                    'Nama': fullname,
                    'Username': usernames,
                    'Image': image_url,
                    'follower': pengikut,
                    'following': mengikuti,
                    'post': postingan,
                    'Kemiripan': f'{similarity_percentage:.2f}%'
                })
            except Exception as e:
                results.append({
                    'Nama': fullname,
                    'Username': usernames,
                    'Image': image_url,
                    'follower': pengikut,
                    'following': mengikuti,
                    'post': postingan,
                    'Kemiripan': '-'
                })

            # Hapus gambar sementara
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            count += 1

        for res in results:
            print(f"""
            Nama: {res['Nama']}
            Username: {res['Username']}
            Image: {res['Image']}
            Pengikut: {res['follower']}
            Mengikuti: {res['following']}
            Post: {res['post']}
            Kemiripan: {res['Kemiripan']}
            """)

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    logon_ig()
