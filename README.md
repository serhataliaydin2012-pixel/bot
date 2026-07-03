# Discord Kufur Engel Botu

Bu proje Python ile yazilmis Discord kufur engel botu ve web panelidir.

## Dosyalar

- `main.py`: Bot ve web panel kodu
- `templates/`: Panel sayfalari
- `static/styles.css`: Panel tasarimi
- `requirements.txt`: Gerekli Python paketleri
- `Procfile`: Render baslatma ayari

## Yerelde calistirma

1. Python paketlerini kur:

```bash
pip install -r requirements.txt
```

2. Ortam degiskenlerini ayarla:

```bash
set DISCORD_TOKEN=bot_tokenin
set PANEL_PASSWORD=panel_sifren
set PANEL_SECRET=rastgele_bir_gizli_yazi
```

3. Baslat:

```bash
python main.py
```

Panel adresi:

```text
http://localhost:10000
```

## Render ayarlari

Render'da yeni bir Web Service olustur ve GitHub reposunu bagla.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python main.py
```

Environment Variables:

```text
DISCORD_TOKEN=Discord bot tokenin
PANEL_PASSWORD=Panel sifren
PANEL_SECRET=Uzun rastgele bir yazi
PUBLIC_URL=Render web servis adresin
```

Discord Developer Portal'da `Message Content Intent` acik olmali.

Botun sunucuda su izinlere ihtiyaci var:

- Mesajlari gor
- Mesajlari yonet
- Mesaj gonder
- Uyeleri sustur

Timeout calismasi icin bot rolu, susturulacak kullanicinin rolunden yukarida olmalidir.
