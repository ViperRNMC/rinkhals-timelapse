Rinkhals Timelapse — Home Assistant Add-on
=========================================

Korte beschrijving
- Rinkhals Timelapse maakt automatisch timelapses van je Anycubic (Rinkhals) 3D-printer via Moonraker/webcam.
- Deze repository bevat een Home Assistant add-on in `addon/` die Ingress ondersteunt.

Credits
-- Deze project is een fork/bewerking van het origineel gemaakt door aenima1337: https://github.com/aenima1337/Rinkhals-Timelapse
-- Gebruik voor installatie en releases deze repository: https://github.com/ViperRNMC/rinkhals-timelapse

Standaard instellingen
- Default `media_path`: `/media/timelapse` (aanpasbaar via add-on opties)
- Default `printer_ip`: `10.10.10.99` (pas aan in add-on configuratie)

Wat is toegevoegd
- `addon/config.json` — Home Assistant add-on manifest met `ingress: true` en opties `printer_ip` + `media_path`.
- `addon/Dockerfile` — buildfile voor de add-on image (gebruikt de code in `app/`).
- Aanpassingen in `app/app.py` zodat `PRINTER_IP`, `MEDIA_PATH` en `CONFIG_FILE` via environment-variabelen ingesteld kunnen worden.

Installatie-opties

Optie A — (Aanbevolen voor HA) Gebruik jouw fork van deze repository als custom add-on repository:
1. Zorg dat deze repository (jouw fork) op GitHub staat.
2. In Home Assistant: Supervisor → Add-on Store → Drie puntjes → Repositories → Voeg je GitHub repo URL (jouw fork) toe.
Rinkhals Timelapse — Home Assistant Add-on
=========================================

Beschrijving
- Deze repository bevat een Home Assistant Supervisor add-on (`rinkhals-timelapse`) die automatisch timelapse-video's maakt van Rinkhals/Anycubic 3D-prints door de Moonraker API en webcam te gebruiken.

Belangrijk
- Dit project is een fork en onderhoud van het origineel. Origineel: https://github.com/aenima1337/Rinkhals-Timelapse

Add-on structuur
- Add-on map: `rinkhals-timelapse/` (op root van deze repo)
- Belangrijke bestanden in die map:
  - `config.json` — add-on manifest (ingress = true, opties: `printer_ip`, `media_path`)
  - `Dockerfile` — buildfile voor de add-on image
  - `app/` — de applicatiecode (`app.py`, `requirements.txt`)
  - `logo.svg` — add-on icoon

Standarde opties
- `media_path`: `/media/timelapse` (aanpasbaar in add-on opties)
- `printer_ip`: `10.10.10.99` (aanpasbaar in add-on opties)

Installatie (Supervisor - aanbevolen)
1. Zorg dat deze repository (jouw fork) op GitHub staat: https://github.com/ViperRNMC/rinkhals-timelapse
2. In Home Assistant: Supervisor → Add-on Store → Drie puntjes → Repositories → Voeg je GitHub repo URL toe.
3. De add-on `Rinkhals Timelapse` verschijnt in de lijst — installeer hem.
4. Stel bij installatie de opties `printer_ip` (IP van je printer) en `media_path` (bijv. `/media/timelapse`).
5. Start de add-on en klik op "Open Web UI" om de app via Ingress in een sideview te gebruiken.

Lokale test (Docker)
```bash
# bouw image (in repo root)
docker build -t rinkhals-timelapse-addon ./rinkhals-timelapse

# run (mount voor persistente media/config)
docker run --rm -p 5005:5005 \
  -v "$(pwd)/data":/media/timelapse \
  -e PRINTER_IP=10.10.10.99 \
  -e MEDIA_PATH=/media/timelapse \
  rinkhals-timelapse-addon
```
Open: `http://localhost:5005` (testmodus, niet via Ingress).

Tips
- Gebruik `/media/timelapse` als `media_path` om video's zichtbaar te maken in Home Assistant's Media Browser.
- Controleer permissies van de gemounte map.

Foutopsporing bij add-on registratie
- Als Supervisor meldt "not a valid add-on repository":
  - Zorg dat je de juiste repo-URL gebruikt (jouw fork: `https://github.com/ViperRNMC/rinkhals-timelapse`).
  - De repo moet een map voor de add-on bevatten op root (dit repo heeft `rinkhals-timelapse/`): OK.
  - Sommige Supervisor versies verwachten een `logo.png` — we leveren `logo.svg`, wat meestal ok is. Laat me weten als je een PNG wilt, dan voeg ik die toe.

Licentie
- MIT

Contact
- Repo: https://github.com/ViperRNMC/rinkhals-timelapse
