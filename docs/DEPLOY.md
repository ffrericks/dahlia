# Deploying the Dahlia tool

The app is one process that serves both the API and the web UI. **All data — the
SQLite database and your photos — lives in one folder**, so a backup is just a copy
of that folder.

> **Security:** there is no login. Keep it on your home network only; don't forward
> the port to the internet.

Two ways to run it on a Proxmox container:

- **Option A — Native (recommended for an LXC):** runs directly with `systemd`. No Docker.
- **Option B — Docker:** uses the existing `Dockerfile` / `docker-compose.yml`.

---

## Get the code onto the container

Either clone it (the repo is private, so you'll be asked to log in or use a token):

```bash
git clone https://github.com/ffrericks/dahlia.git
cd dahlia
```

…or copy it from your PC over SSH (run this on your PC, from the project folder):

```bash
# replace user@CT-IP and the path
scp -r . root@192.168.1.50:/opt/dahlia
```

---

## Option A — Native install (Proxmox LXC)

1. **Create the container** in Proxmox: a **Debian 12** LXC, ~1 vCPU, 512 MB–1 GB RAM,
   4 GB disk. Unprivileged is fine. Give it a static IP or note its DHCP IP.

2. **SSH into the container** and go to the code folder (e.g. `/opt/dahlia`).

3. **Run the installer** (installs Python + Node, builds the UI, creates a service):

   ```bash
   sudo bash deploy/install.sh
   ```

   Options if you want to change them:

   ```bash
   sudo PORT=8080 DATA_DIR=/var/lib/dahlia bash deploy/install.sh
   ```

4. **Open it** from any device on your network: `http://<container-ip>:8000`

That's it — it now starts automatically on boot.

**Handy commands**

```bash
systemctl status dahlia      # is it running?
journalctl -u dahlia -f      # live logs
systemctl restart dahlia     # restart
```

**Update to a newer version**

```bash
cd /opt/dahlia
sudo bash deploy/update.sh    # pulls latest, rebuilds, restarts (data is kept)
```

---

## Option B — Docker

Works on any VM, or an LXC with **nesting enabled** (Proxmox → container → Options →
Features → check *Nesting*; Docker in an unprivileged LXC needs this).

1. Install Docker on the container:

   ```bash
   curl -fsSL https://get.docker.com | sh
   ```

2. From the code folder, build and start:

   ```bash
   docker compose up -d --build
   ```

3. Open `http://<container-ip>:8000`. Data is stored in `./data` next to the compose file.

**Commands**

```bash
docker compose logs -f        # logs
docker compose pull && docker compose up -d   # update (if using a published image)
docker compose down           # stop
```

### Moving the image without a registry

If you build the image on your PC and want it on the container without GitHub:

```bash
# on your PC
docker build -t dahlia .
docker save dahlia | ssh root@192.168.1.50 docker load
# then on the container, run it with a data volume:
ssh root@192.168.1.50 'docker run -d --name dahlia -p 8000:8000 -v /opt/dahlia-data:/data --restart unless-stopped dahlia'
```

### Publishing to GitHub Container Registry (optional)

The repo includes `.github/workflows/build.yml`, which builds and pushes an image to
`ghcr.io/ffrericks/dahlia` on every push to `main`. To enable it you must add the
`workflow` scope to your GitHub CLI and push the workflow file:

```bash
gh auth refresh -h github.com -s workflow
git add .github/workflows/build.yml && git commit -m "Add CI" && git push
```

Then set `image: ghcr.io/ffrericks/dahlia:latest` in `docker-compose.yml` (and remove
`build: .`) to pull instead of build.

---

## Backups

Stop nothing — just copy the data folder regularly:

- Native: the `data/` folder in the repo (or your `DATA_DIR`).
- Docker: the `data/` folder next to `docker-compose.yml`.

```bash
# example: copy the data folder to your PC over SSH
scp -r root@192.168.1.50:/opt/dahlia/data ./dahlia-backup-$(date +%F)
```

To restore: stop the app, put the folder back, start it again.
