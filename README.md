# 🎯 AirSim ile Görüntü İşleme Destekli Otonom Drone Uçuşu

Bu proje, Unreal Engine üzerinde çalışan Microsoft AirSim ortamında, birden fazla drone’un yalnızca kamera görüntüsü ve derinlik verisiyle otonom olarak engellerden kaçınarak hedefe ilerlemesini sağlar.

📍 Proje, Marmara Üniversitesi Bilgisayar Programcılığı bölümü 2024-2025 bitirme projesidir.  
👥 Ekip: Berk Efe Polat, Minel Baştor, Melike Can, Serra Çınay Tezer  
🎓 Danışman: Öğr. Gör. Ercan Erkalkan

---

## 🚀 Projenin Amacı

Simülasyon ortamında, derinlik haritası ve RGB kamera görüntüsü üzerinden engel algılayarak hareket eden, otonom kontrol algoritmalarına sahip birden fazla drone sisteminin geliştirilmesi.

Drone'lar, başlangıçta aynı anda havalanır, çevredeki engelleri analiz ederek yön ve hızlarını dinamik olarak ayarlar, hedefe ulaştıklarında güvenli şekilde iniş yaparlar.

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji     | Açıklama |
|---------------|----------|
| AirSim        | Microsoft’un açık kaynaklı drone simülasyon kütüphanesi       |
| Unreal Engine | 4.27 – Ormanlık harita oluşturuldu ve test ortamı hazırlandı  |
| Python        | Kontrol mantığı, görüntü işleme ve karar algoritmaları için   |
| OpenCV        | Görüntü işleme (Canny, threshold, alan hesaplama)             |
| NumPy         | Piksel matrisleri üzerinde hızlı işlem                        |
| Python API    | Drone kontrolü, görüntü ve derinlik verisi alma               |

---

## ⚙️ Uygulama Akışı

### 1. Çoklu Drone Başlatma
- `Drone1` ve `Drone2` eş zamanlı olarak kalkış yapar.
- Belirlenen yükseklikte havada sabitlenir.

### 2. Görüntü ve Derinlik Analizi
- Her drone, `front_center` kamerasından hem RGB hem de derinlik görüntüsü alır.
- Görüntü işleme ile dört bölgedeki (orta, alt, sol, sağ) engel yoğunluğu hesaplanır.

### 3. Engel Tespiti
- Derinlik görüntüsü analiz edilerek `2 metre` altında nesneler taranır.
- Görsel yoğunluk analizine göre yön değiştirme veya yükselme kararları alınır.

### 4. Yön Belirleme
- Engel tespit edilirse, -60° ile +60° arasında açılar denenerek en güvenli yön seçilir.
- Eğer güvenli yön yoksa, drone yukarı çıkar veya mevcut konumunu korur.

### 5. Hedefe Ulaşma ve İniş
- Drone hedef koordinatlara ulaştığında (30, 40), güvenli şekilde iniş yapar.
- Motorlar kapanır ve drone sistemden ayrılır.

---

## 🧠 Kullanılan Algoritmalar

- **Görüntü İşleme**
  - HSV dönüşüm ve dinamik eşikleme ile engel alanı ayrıştırma
  - Canny kenar bulucu ile taş/kaya gibi yapıları tespit etme
- **Derinlik Analizi**
  - Kamera merkez bölgesindeki ortalama mesafeye göre tehdit değerlendirmesi
- **Yön Kararı**
  - Çok açılı döndürme ve puanlama ile en az engel bulunan yön seçimi
- **PID benzeri hız hesaplama**
  - Hedefe olan mesafeye göre normalize edilmiş hız vektörü oluşturma

---

## ✅ Sonuç

Bu proje, AirSim ortamında görüntü işleme temelli, çarpışmadan kaçınabilen, dinamik olarak yön belirleyebilen otonom drone kontrol sistemlerinin temelini başarıyla ortaya koymuştur.

---

## ✉️ İletişim

Bu proje hakkında fikir alışverişi yapmak isterseniz LinkedIn veya GitHub üzerinden bana ulaşabilirsiniz.  
👉 [LinkedIn: Berk Efe Polat](https://www.linkedin.com/in/berk-efe-polat-13228b305/)  
👉 GitHub: [github.com/berkefepolat](https://github.com/krebtalop)
👉 Mail: (polatberk97@gmail.com)



