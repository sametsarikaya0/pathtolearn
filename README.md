# PathToLearn — Akıllı Öğrenme Yol Haritası Platformu

**PathToLearn**, 10.000+ derslik geniş katalogu doğal dil ipuçları, çoklu tema paletleri, kişisel ders notları, alternatif ders değiştirme, başarı sertifikası ve `.MD` / `.JSON` dışa aktarma araçlarıyla birleştiren tek sayfa tabanlı (`SPA`), sunucusuz (`serverless` / istemci taraflı) öğrenme planlama platformudur.

![PathToLearn Ana Sayfa Görünümü](./screenshots/home-indigo.png)

---

## İçindekiler

1. [Proje Genel Bakışı](#proje-genel-bakışı)
2. [Temel Özellikler ve İşlevsel Modüller](#temel-özellikler-ve-işlevsel-modüller)
3. [Cümle Analizi ve Yol Haritası Motoru](#cümle-analizi-ve-yol-haritası-motoru)
4. [10.000+ Derslik Katalog ve Kalıcı Admin Dersleri](#10000-derslik-katalog-ve-kalıcı-admin-dersleri)
5. [Çoklu Renk Temaları ve Açık / Koyu Mod](#çoklu-renk-temaları-ve-açık--koyu-mod)
6. [Sekmeler ve Kullanıcı Akışları](#sekmeler-ve-kullanıcı-akışları)
7. [Veri Kalıcılığı, Yedekleme ve Dışa Aktarma](#veri-kalıcılığı-yedekleme-ve-dışa-aktarma)
8. [Proje Dosya Yapısı](#proje-dosya-yapısı)
9. [Yerel Çalıştırma ve Geliştirme](#yerel-çalıştırma-ve-geliştirme)
10. [GitHub ve Vercel ile Yayınlama](#github-ve-vercel-ile-yayınlama)
11. [Bilinen Davranışlar ve Teknik Notlar](#bilinen-davranışlar-ve-teknik-notlar)

---

## Proje Genel Bakışı

PathToLearn; kullanıcının öğrenmek istediği konuyu serbest bir cümle halinde yazmasına olanak tanır, bu cümleyi branş, seviye, tempo, amaç ve ikincil/destek alan açısından çözümler ve ortaya çıkan ders sıralamasını ayrı bir **Yol Haritası** görünümünde sunar.

- **Mimari Yaklaşım:** Tek HTML dosyası (`public/index.html`) içinde Tailwind CSS (CDN), Lucide Icons, `Plus Jakarta Sans` yazı tipi ve saf JavaScript ile çalışır.
- **Harici Bağımlılık İhtiyacı:** Kurulum veya paket yöneticisi (`npm`, `pip`, `Docker`) gerektirmez; herhangi bir statik sunucu veya doğrudan tarayıcı üzerinden çalışır.

---

## Temel Özellikler ve İşlevsel Modüller

### 1. Cümleden Yol Haritası Oluşturma (`createRoadmapInTab`, `createRoadmapData`)
- Kullanıcının yazdığı hedef cümle ve isteğe bağlı filtreler (*Geniş Branş Filtresi*, *Seviye Filtresi*, *Odak Anahtar Kelime*) birleştirilerek değerlendirilir.
- Varsayılan olarak **12 ders** seçilir ve üç aşamaya bölünür:
  - **1. Aşama — Temel Kavramlar**
  - **2. Aşama — Uygulama ve Pratik**
  - **3. Aşama — Derinleşme ve Proje**
- **+6 Ek Ders Daha Göster (`loadMoreRoadmapCourses`):** Mevcut yol haritasındaki ders sayısını aynı kriterlere uygun yeni derslerle 6'şarlı adımlarla artırır (üst sınır: 36 ders).

### 2. Ders Kartlarında Kişisel Not ve Alternatif Ders
- **Kişisel Not Alanı (`saveCourseNote`):** Yol haritası görünümündeki her ders kartında not giriş alanı bulunur. Girilen metin `userState.courseNotes[courseId]` altında saklanır ve yol haritası içi aramada eşleştirilir.
- **Alternatif Ders Değiştirme (`replaceCourseWithAlternative`):** Karttaki **Alternatif** butonu, ilgili dersi haritada o an bulunmayan, aynı branş ve seviyedeki (veya bulunamazsa aynı branştaki) başka bir dersle değiştirir.
- **Tamamlama Durumu (`toggleCourseDone`):** Ders kartındaki **Bitir / Tamamlandı** butonu dersi `userState.completedCourseIds` listesine ekler veya çıkarır; ilerleme çubuğunu ve **Bitirilenler** sayacını anlık günceller.

### 3. Topluluk Yorumları ve Önerileri (`addCommunityComment`, `renderCommunityComments`)
- Ana sayfa altındaki topluluk bölümünden rumuz ve öneri metni bırakılabilir.
- Yorumlar `ptl_community_comments_v5` anahtarıyla `localStorage` üzerinde kalıcı olarak tutulur.

### 4. Başarı Sertifikası (`openCertificate`, `closeCertificate`)
- **Bitirilenler** sekmesindeki **Sertifika** butonu, kullanıcı adı ve güncel tarih ile sertifika penceresini açar.
- Pencere içindeki **Yazdır / PDF Kaydet** butonu `@media print` kurallarına uygun çıktı akışını tetikler.

### 5. Akıllı Kaydırma Butonları (`scrollToTopSmooth`, `scrollToBottomSmooth`, `syncScrollButtons`)
- Sağ altta sabit duran kaydırma kontrolünde **Yukarı Kaydır** butonu sayfa en üstteyken (`scrollY < 180`) gizlenir, aşağı inildikçe görünür hale gelir.
- **Aşağı Kaydır** butonu sayfa sonuna yaklaşıldığında (`y >= maxY - 120`) gizlenir.

---

## Cümle Analizi ve Yol Haritası Motoru

`analyzeSentenceAndFilters(sentence, forcedDomain, forcedLevel, keyword)` fonksiyonu metni küçük harfe çevirerek şu boyutları tespit eder:

| Boyut | Algılama Mantığı | Çıktı Değerleri |
| :--- | :--- | :--- |
| **Ana Branş (`domain`)** | Seçili filtre `Auto` ise `domainCatalog` içindeki anahtar kelimelerin cümledeki eşleşme uzunluk puanına göre en yüksek puanlı branş seçilir; eşleşme yoksa varsayılan `History` atanır. | `History`, `Music`, `Art`, `Psychology`, `Game`, `Python`, `AI`, `Data`, `Finance`, `Tech`, `Math`, `Engineering`, `Design`, `Business`, `Productivity` |
| **İkincil Branş (`secondaryDomain`)** | Ana branş dışındaki branşlar arasında puanı `0`'dan büyük olan ilk branş destek alanı olarak belirlenir. | Branş kimliği veya `null` |
| **Seviye (`level`)** | Seçili filtre `Auto` ise cümledeki `başlangıç`, `sıfır`, `yeni başlayan`, `101`, `temel`, `hızlı` → `Beginner`; `ileri`, `uzman`, `ileri seviye` → `Advanced`; `orta` → `Intermediate` eşleşmelerine bakar; aksi halde `Beginner` döner. | `Beginner`, `Intermediate`, `Advanced` |
| **Tempo (`paceLabel`)** | `hızlı`/`kısa`/`özet` → `Hızlı Özet`; `hafta son`/`az vakit`/`günde 20` → `Hafif Tempo`; `yoğun`/`derin`/`detaylı` → `Derin Odak`; aksi halde `Standart Tempo`. | `Hızlı Özet`, `Hafif Tempo`, `Derin Odak`, `Standart Tempo` |
| **Amaç (`aimLabel`)** | `sınav`/`test`/`hazırlık` → `Sınav Hazırlığı`; `proje`/`yapmak`/`üretmek` → `Uygulama & Proje`; `hobi`/`keyif`/`merak` → `Hobi & Keşif`; aksi halde `Genel Gelişim`. | `Sınav Hazırlığı`, `Uygulama & Proje`, `Hobi & Keşif`, `Genel Gelişim` |

### Aday Ders Sıralama (`getCandidateCourses`)
1. Hedef branş ve seviyeye uyan dersler toplanır (12 dersten azsa aynı branştaki diğer seviyeler eklenir).
2. İkincil branş varsa en fazla 6 destek dersi eklenir.
3. Toplam havuz 24 dersin altındaysa diğer derslerle tamamlanır.
4. Cümle ve odak anahtar kelimesindeki 2 karakterden uzun kelimelere göre başlık, açıklama ve branş etiketindeki eşleşme sayısına göre sıralanır. Odak anahtar kelime verilmişse ve en az 6 eşleşen ders varsa liste bu sonuçlarla daraltılır.

---

## 10.000+ Derslik Katalog ve Kalıcı Admin Dersleri

`build10000CoursePool()` fonksiyonu kataloğu iki kaynaktan birleştirir:

1. **Admin Özel Dersleri (`loadCustomCourses()`):** `localStorage` içindeki `ptl_custom_courses_v5` dizisinden okunur ve listenin en başına eklenir.
2. **Üretilmiş 10.000 Ders (`1..10000`):**
   - `domainCatalog` içindeki 15 branş sırayla döner.
   - Her branşın kendi `topics` dizisindeki 5 alt konu modüler olarak eşleştirilir.
   - Seviyeler (`Beginner`, `Intermediate`, `Advanced`), eğitmenler (`instructorsPool`) ve süreler (`2` ile `8` hafta arası) deterministik olarak atanır.
   - Her ders için `https://ocw.mit.edu/search/?q=...` arama bağlantısı üretilir.

---

## Çoklu Renk Temaları ve Açık / Koyu Mod

Uygulama `html` etiketi üzerinde `data-palette` niteliğini ve `dark` sınıfını kullanarak tema değişkenlerini (`--brand-50` .. `--brand-900`, `--accent-2`, `--glow-1`, `--glow-2`) günceller:

- **İndigo (`indigo`):** İndigo ve camgöbeği (`cyan`) vurgu tonları.
- **Okyanus (`ocean`):** Gökyüzü/okyanus mavisi ve indigo vurgu tonları.
- **Mercan (`rose`):** Gül/mercan kırmızısı ve turuncu vurgu tonları.
- **Kehribar (`amber`):** Kehribar/altın sarısı ve pembe vurgu tonları.
- **Zümrüt (`emerald`):** Zümrüt yeşili ve deniz yeşili (`teal`) vurgu tonları.

Tercihler `ptl_palette_v5` ve `ptl_theme_v5` anahtarlarıyla `localStorage` içinde saklanır; `@media (prefers-reduced-motion: reduce)` kuralı hareket hassasiyeti olan sistemlerde animasyon ve geçişleri devre dışı bırakır.

---

## Sekmeler ve Kullanıcı Akışları

Uygulama 9 ana görünüm (`viewMap`) arasında geçiş yapar:

1. **Ana Sayfa (`home`):** Tanıtım kartı, **Günlük Öneri** kartı, hedef cümle ve filtre formu, **Hızlı Başlangıç Cümleleri** ve **Topluluk Yorumları ve Önerileri**.
2. **Yol Haritası (`roadmap`):** Aktif yol haritasının 3 aşamalı görünümü, **+6 Ek Ders Daha Göster**, **.MD İndir**, yol haritası içi arama/seviye filtresi, ders notları ve **Alternatif** ders butonu.
3. **Önerilen Yollar (`recommendedPaths`):** Tarih, Müzik, Resim, Psikoloji, Oyun Geliştirme ve Para Yönetimi & Teknoloji 101 yol özetleri.
4. **Örnek Yol Haritaları (`exampleRoadmaps`):** Hazır senaryo kartları ve tek tıkla yol haritası sekmesinde açma aksiyonu.
5. **Önerilen Dersler (`recommendedCourses`):** Seçili branşlardan örnek ders kartları.
6. **Bitirilenler (`completed`):** Tamamlanan ders listesi ve başarı sertifikası tetikleyicisi.
7. **Admin (`admin`):** Yetkili admin girişinde açılan yönetim merkezi:
   - Ana sayfa, günlük öneri ve hoş geldiniz popup metinlerini düzenleme
   - 4 hızlı başlangıç cümlesini güncelleme
   - Kataloga kalıcı yeni ders ekleme
   - Topluluk yorumlarını silme ve metinleri varsayılana döndürme
8. **Profil (`profile`):** Kullanıcı adı, oturum durumu, bitirilen ders sayısı, çalışma serisi, son aranan hedefler ve `.JSON` yedekleme / geri yükleme araçları.

![PathToLearn Profil Ekranı](./screenshots/themes-and-profile.png)

9. **Yardım (`help`):** Kullanım rehberi, hakkında bölümü, sıkça sorulan sorular ve iletişim formu.

![PathToLearn Yardım ve Destek Ekranı](./screenshots/home-help.png)

---

## Veri Kalıcılığı, Yedekleme ve Dışa Aktarma

### Kullanılan `localStorage` Anahtarları
- `ptl_custom_courses_v5`: Admin tarafından eklenen özel dersler.
- `ptl_site_settings_v5`: Site metinleri, günlük öneri, hoş geldiniz modalı durumu ve hızlı başlangıç cümleleri.
- `ptl_community_comments_v5`: Topluluk yorumları ve önerileri.
- `ptl_active_user_v5`: Aktif oturum kullanıcı adı.
- `ptl_users_db_v5`: Kayıtlı kullanıcı kimlik bilgileri.
- `ptl_state_v5_<kullanici>` ve `ptl_guest_state_v5`: Tamamlanan dersler, ders notları (`courseNotes`), çalışma serisi (`streak`), son ziyaret tarihi, son hedefler ve aktif yol haritası (`activeRoadmap`).
- `ptl_palette_v5` ve `ptl_theme_v5`: Seçili renk paleti ve açık/koyu mod durumu.

### Dışa Aktarma ve Yedekleme Formatları
- **Markdown (`.MD`):** `exportRoadmapMarkdown()` ile `pathtolearn-yol-haritasi.md` dosyası oluşturur; her dersin tamamlanma kutusunu (`[x]` / `[ ]`), başlığını, branş/seviye/süre bilgisini, eğitmenini ve varsa kişisel notunu içerir.
- **JSON Yedek (`.JSON`):** `exportUserBackupJSON()` ile `exportedAt`, `user`, `userState` ve `communityComments` alanlarını içeren yedek dosyası üretir; `importUserBackupJSON()` ile geri yükler.

---

## Proje Dosya Yapısı

```text
pathtolearn/
├── public/
│   └── index.html      # Tam uygulama (arayüz, stiller, katalog, analiz motoru, state yönetimi)
├── screenshots/        # Uygulama ekran görüntüleri
└── README.md           # Proje dokümantasyonu
