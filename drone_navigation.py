import airsim
import numpy as np
import cv2
import time
import math

client = airsim.MultirotorClient()
client.confirmConnection()

vehicle_names = ["Drone1", "Drone2"]

# Her drone için yukarı kaçma miktarı (negatif Z yönünde)
yukari_kacis_miktari = {
    "Drone1": -2.5,
    "Drone2": -3.2
}

# 🛫 Her bir drone için kalkış ve başlatma
for name in vehicle_names:
    client.enableApiControl(True, vehicle_name=name)
    client.armDisarm(True, vehicle_name=name)
    client.takeoffAsync(vehicle_name=name).join()
    client.moveToZAsync(-5, 2, vehicle_name=name).join()
    print(f"{name} havalandı")

hedef_x = 30
hedef_y = 40

def get_yaw(name):
    orientation = client.getMultirotorState(vehicle_name=name).kinematics_estimated.orientation
    _, _, yaw = airsim.to_eularian_angles(orientation)
    return yaw

def get_z(name):
    return client.getMultirotorState(vehicle_name=name).kinematics_estimated.position.z_val

def hedefe_uzaklik(name):
    pos = client.getMultirotorState(vehicle_name=name).kinematics_estimated.position
    dx = hedef_x - pos.x_val
    dy = hedef_y - pos.y_val
    return math.sqrt(dx*2 + dy*2)

def hedefe_don_ve_git(name, hiz=1.0, sure=0.5):
    pos = client.getMultirotorState(vehicle_name=name).kinematics_estimated.position
    dx = hedef_x - pos.x_val
    dy = hedef_y - pos.y_val
    uzaklik = math.sqrt(dx*2 + dy*2)
    if uzaklik == 0:
        return
    yaw = math.degrees(math.atan2(dy, dx))
    client.rotateToYawAsync(yaw, vehicle_name=name).join()
    vx = (dx / uzaklik) * hiz
    vy = (dy / uzaklik) * hiz
    client.moveByVelocityAsync(vx, vy, 0, sure, vehicle_name=name)

def get_camera_image(name):
    raw = client.simGetImage("front_center", airsim.ImageType.Scene, vehicle_name=name)
    if raw is None:
        return None
    img1d = np.frombuffer(raw, dtype=np.uint8)
    return cv2.imdecode(img1d, cv2.IMREAD_COLOR)

def get_depth_image(name):
    responses = client.simGetImages([
        airsim.ImageRequest("front_center", airsim.ImageType.DepthPerspective, pixels_as_float=True, compress=False)
    ], vehicle_name=name)
    if not responses or responses[0].image_data_float == []:
        return None
    img1d = np.array(responses[0].image_data_float, dtype=np.float32)
    return img1d.reshape(responses[0].height, responses[0].width)

def engel_var_mi_depth(name, threshold_metre=2.0):
    depth = get_depth_image(name)
    if depth is None:
        print("Derinlik verisi alınamadı!")
        return False
    h, w = depth.shape
    orta_bolge = depth[h//3:h*2//3, w//3:w*2//3]
    yakin_nokta_sayisi = np.sum(orta_bolge < threshold_metre)
    oran = yakin_nokta_sayisi / orta_bolge.size
    print(f"Derinlik oranı < {threshold_metre}m: %{oran*100:.1f} ➤ {'🚨 TEHLİKE!' if oran > 0.15 else '✔ Güvenli'}")
    return oran > 0.15

def engel_puanlari(img):
    h, w, _ = img.shape
    orta = img[h//3:h*4//5, w//3:w*2//3]
    alt = img[h*4//5:h, w//3:w*2//3]
    sag = img[h//3:h*4//5, w*2//3:]
    sol = img[h//3:h*4//5, :w//3]

    gri_orta = cv2.cvtColor(orta, cv2.COLOR_BGR2GRAY)
    gri_alt = cv2.cvtColor(alt, cv2.COLOR_BGR2GRAY)
    gri_sag = cv2.cvtColor(sag, cv2.COLOR_BGR2GRAY)
    gri_sol = cv2.cvtColor(sol, cv2.COLOR_BGR2GRAY)

    def dinamik_esik(gri):
        ort = np.mean(gri)
        return 255 - max(ort, 80)

    _, maske_orta = cv2.threshold(gri_orta, dinamik_esik(gri_orta), 255, cv2.THRESH_BINARY_INV)
    _, maske_sag = cv2.threshold(gri_sag, dinamik_esik(gri_sag), 255, cv2.THRESH_BINARY_INV)
    _, maske_sol = cv2.threshold(gri_sol, dinamik_esik(gri_sol), 255, cv2.THRESH_BINARY_INV)

    kenarlar = cv2.Canny(gri_alt, 50, 150)

    puan_orta = cv2.countNonZero(maske_orta)
    puan_sag = cv2.countNonZero(maske_sag)
    puan_sol = cv2.countNonZero(maske_sol)
    kaya_puani = cv2.countNonZero(kenarlar)

    return puan_orta, puan_sag, puan_sol, kaya_puani

def uygun_yon_bul(name):
    print("Çevre taranıyor...")
    en_az_engel = float("inf")
    en_iyi_yaw = None
    mevcut_yaw = math.degrees(get_yaw(name))

    for aci in range(-60, 61, 30):
        hedef_yaw = mevcut_yaw + aci
        client.rotateToYawAsync(hedef_yaw, vehicle_name=name).join()
        time.sleep(0.3)

        img = get_camera_image(name)
        if img is None:
            continue

        puan_orta, _, _, _ = engel_puanlari(img)
        print(f"Açı {aci:+}° → Engel puanı: {puan_orta}")

        if puan_orta < en_az_engel:
            en_az_engel = puan_orta
            en_iyi_yaw = hedef_yaw

    return en_iyi_yaw, en_az_engel

# 🔁 ANA DÖNGÜ
inenler = set()

while len(inenler) < len(vehicle_names):
    for name in vehicle_names:
        if name in inenler:
            continue

        uzaklik = hedefe_uzaklik(name)
        print(f"{name} Hedefe uzaklık: {uzaklik:.2f} metre")

        if uzaklik < 2.0:
            print(f"{name} Hedefe ulaşıldı → İniş başlatılıyor!")
            client.hoverAsync(vehicle_name=name).join()
            time.sleep(1)
            client.landAsync(vehicle_name=name).join()
            time.sleep(1)
            client.armDisarm(False, vehicle_name=name)
            client.enableApiControl(False, vehicle_name=name)
            print(f"{name} ✅ İniş tamamlandı ve sistem kapatıldı.")
            inenler.add(name)
            continue

        img = get_camera_image(name)
        if img is None:
            print(f"{name} Kamera alınamadı")
            continue

        puan_orta, puan_sag, puan_sol, kaya_puani = engel_puanlari(img)
        derinlik_engel = engel_var_mi_depth(name, threshold_metre=2.0)

        if kaya_puani > 3500:
            print(f"{name}  Kaya algılandı → Yukarı kaçınılıyor!")
            client.moveByVelocityAsync(0, 0, yukari_kacis_miktari[name], 1, vehicle_name=name).join()
            continue

        if derinlik_engel:
            print(f"{name} 🚩 Derinlikte ciddi engel var → Yukarı çıkılıyor!")
            client.moveByVelocityAsync(0, 0, yukari_kacis_miktari[name], 1, vehicle_name=name).join()
            continue

        if puan_orta > 8000:
            print(f"{name}  Görsel yoğunluk yüksek → Yön aranıyor...")
            en_iyi_yaw, en_iyi_puan = uygun_yon_bul(name)

            if en_iyi_puan < 8000:
                print(f"{name} ✅ Yeni yön: {en_iyi_yaw:.1f}°")
                client.rotateToYawAsync(en_iyi_yaw, vehicle_name=name).join()
            else:
                z = get_z(name)
                if z > -20:
                    print(f"{name}  Yukarı çıkılıyor (yön yok)")
                    client.moveByVelocityAsync(0, 0, yukari_kacis_miktari[name], 1, vehicle_name=name).join()
                elif z < -3:
                    print(f"{name} Aşağı iniliyor (yön yok)")
                    client.moveByVelocityAsync(0, 0, 2, 1, vehicle_name=name).join()
                else:
                    print(f"{name} Bekleniyor")
                time.sleep(1)
        else:
            print(f"{name}  Hedef yönünde ilerleniyor")
            hedefe_don_ve_git(name, hiz=1.0, sure=0.5)

    time.sleep(0.1)