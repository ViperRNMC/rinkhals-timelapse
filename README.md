Rinkhals Timelapse — Home Assistant Add-on
=========================================

Korte beschrijving
- Rinkhals Timelapse maakt automatisch timelapses van je Anycubic (Rinkhals) 3D-printer via Moonraker/webcam.
- Deze repository bevat een Home Assistant add-on in `addon/` die Ingress ondersteunt.

Credits
- Deze project is een fork/bewerking van het origineel gemaakt door aenima1337: https://github.com/aenima1337/Rinkhals-Timelapse
- Verder verwijzen de installatie-instructies naar jouw fork/repository (gebruik jouw GitHub-repo-URL bij installatie via Supervisor).

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
3. Zoek de add-on `Rinkhals Timelapse` en installeer.
4. Geef bij installatie/opties `printer_ip` en `media_path` (`/media/timelapse`).
5. Start de add-on en klik op "Open Web UI" (Ingress). De app draait via Ingress in een sideview.

Optie B — Lokale test met Docker (snel testen buiten Supervisor):
```bash
# bouw image
docker build -t rinkhals-timelapse-addon ./addon

# run (mount voor persistente media/config)
docker run --rm -p 5005:5005 \
  -v "$(pwd)/data":/media/timelapse \
  -e PRINTER_IP=10.10.10.99 \
  -e MEDIA_PATH=/media/timelapse \
  rinkhals-timelapse-addon
```
Open in je browser: `http://localhost:5005` (niet via Ingress, dit is voor testing).

Opmerkingen en tips
- Gebruik `/media/timelapse` als media map als je wilt dat Home Assistant's Media Browser de video's kan vinden.
- Zorg dat de map permissies heeft voor de gebruiker in de container (Supervisor regelt dit meestal bij `media` mapping).
- Ingress gebruikt poort 5005 intern; geen externe poort nodig als je Ingress activeert.
- Als je de add-on direct installeert via Supervisor, stel `media_path` in op `/media/timelapse` en `printer_ip` op het IP van je printer.

Probleemoplossing
- Als de add-on de webcam niet kan bereiken: controleer `printer_ip` en of de webcam URL (`http://PRINTER_IP/webcam/?action=snapshot`) bereikbaar is vanaf het host.
- Als ffmpeg ontbreekt of render faalt: controleer container logs; `addon/Dockerfile` installeert `ffmpeg`.

Volgende stap (voor jou)
- Als je wilt dat ik nu push naar je remote, geef akkoord (ik probeer te committen en te pushen vanuit deze workspace). Als push faalt door credentials, zal ik de foutmelding tonen en uitleggen hoe te fixen.
# Rinkhals-Timelapse

**Important Requirement:** This tool requires a printer running [Rinkhals by jbatonnet](https://github.com/jbatonnet/Rinkhals) to function on Anycubic devices. A huge thank you to the creator of Rinkhals for making Klipper accessible on these machines.

---

Rinkhals-Timelapse is a lightweight Docker-based tool that automatically creates timelapse videos of your 3D prints. It is designed to work passively by monitoring your printer via the Moonraker API, requiring no special G-code modifications or slicer plugins. It is particularly effective for HueForge prints where traditional layer-change triggers may be absent.

## Features

* **Smart Time Mode:** Automatically calculates the optimal capture interval based on the estimated print time to produce a consistent video length (approximately 15 seconds), ideal for social media sharing.
* **Layer Mode:** Captures a frame at every detected layer change.
* **G-Code Independent:** No need to add TIMELAPSE_TAKE_FRAME or similar commands to your slicer. The script monitors the printer status via Moonraker.
* **Stable Web Interface:** Provides real-time status updates and image previews without layout shifts or flickering.
* **Multi-Architecture Support:** Compatible with both PC (x86_64) and Raspberry Pi (ARM64).
* **Manual Render:** Option to manually trigger video generation from existing snapshots if a print is interrupted.
* **Zero Printer Load:** All processing happens on your Docker host (Pi/PC). No stress for the printer MCU.

## Setup with Docker Compose

1. Create a directory for the project.
2. Create a `docker-compose.yml` file with the following content:

```yaml
services:
  rinkhals-timelapse:
    image: ghcr.io/aenima1337/rinkhals-timelapse:latest
    container_name: rinkhals-timelapse
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./snapshots:/app/snapshots
      - ./videos:/app/videos

```

3. Start the container:
```bash
docker compose up -d

```


4. Access the interface via `http://[YOUR_DOCKER_HOST_IP]:5005`.
5. Enter your printer's IP address in the settings field and save.

## How it Works

The application communicates with the Moonraker API to track print progress.

* In **Layer Mode**, it triggers a snapshot whenever the `current_layer` value increases.
* In **Smart Time Mode**, it fetches metadata from the G-code file to determine the estimated print duration and divides it by the target frame count to set a custom capture interval.

## License and Credits

* **Author:** aenima1337
* **License:** MIT
* **Acknowledgments:** Special thanks to jbatonnet for the Rinkhals project.
