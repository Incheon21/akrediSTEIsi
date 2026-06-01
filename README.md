# Sistem Akreditasi STEI ITB

Sistem Terintegrasi Repository dan Dashboard Data Akreditasi SPSI STEI. Proyek ini dikembangkan oleh Kelompok 11 (IF3250 K01) untuk memfasilitasi pelaporan, evaluasi diri, dan pemantauan akreditasi (seperti standar LAM Teknik 2025) di lingkungan Sekolah Teknik Elektro dan Informatika (STEI) ITB.

## 🛠 Tech Stack

- **Frontend:** Next.js (App Router), React, Tailwind CSS, TypeScript
- **Backend:** FastAPI, SQLAlchemy, Alembic, Python 3.13 (managed via `uv`)
- **Database:** PostgreSQL 17
- **Infrastructure:** Docker & Docker Compose

---

## 🚀 Getting Started

### Prerequisites
Make sure you have the following installed on your machine:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Environment Variables
The project contains `.env.example` and `.env.local` files in both the `frontend` and `backend` directories. Docker Compose is already configured to pass the necessary environment variables for local development, so you can run the app immediately without manual `.env` setup.

### Running the Application

To build and start all services (Database, Backend, and Frontend), simply run:

```bash
docker-compose up --build
```

Once the containers are successfully running, you can access:
- **Frontend Web App:** [http://localhost:3000](http://localhost:3000)
- **Backend API (Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the application, press `Ctrl+C` or run:
```bash
docker-compose down
```

---

## 🗄 Database & Seeding

The backend Docker container is configured with a `startup.sh` script that **automatically runs the database seeder** every time it starts. 

The seeder is idempotent (safe to run repeatedly) and will automatically populate the database with:
1. System Roles
2. Default Users
3. Program Studi (e.g., Teknik Informatika, Sistem Teknologi Informasi)
4. Target Akreditasi
5. **Kriteria & Indikator LAM Teknik 2025** (Fully structured and nested)

### Default Test Accounts
You can log in to the frontend using any of the following pre-configured accounts:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@stei.itb.ac.id` | `admin123` |
| **Pimpinan** | `pimpinan@stei.itb.ac.id` | `pimpinan123` |
| **Koordinator** | `koordinator@stei.itb.ac.id` | `koordinator123` |
| **Tim Prodi** | `timprodi@stei.itb.ac.id` | `timprodi123` |

### Hard Resetting the Database
If you ever need to completely wipe the database and let the seeder recreate everything from scratch (e.g., if you modify the LAM Teknik indicator structure in the code), you must remove the Docker volume holding the PostgreSQL data:

```bash
# Bring down containers AND remove volumes
docker-compose down -v

# Rebuild and start fresh
docker-compose up --build
```

---

## 🚢 VPS Deployment

The production compose file builds the backend and frontend on the server, keeps PostgreSQL private, stores uploaded evidence files in a Docker volume, and uses Caddy for HTTP/HTTPS reverse proxying.

### 1. Prepare the VPS

Install Docker and the Compose plugin on the VPS, then open ports `80` and `443` in the VPS firewall/security group.

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Log out and back in after adding your user to the `docker` group.

### 2. Copy the Project

Clone or upload this repository to the VPS.

```bash
git clone <your-repository-url>
cd if3250_k01_g11_stei1
```

### 3. Configure Environment

Create the root production env file:

```bash
cp .env.production.example .env
```

Edit `.env` and set:

- `DOMAIN` to your domain, for example `akreditasi.example.com`.
- `POSTGRES_PASSWORD` to a strong password.
- Keep `NEXT_PUBLIC_API_URL` empty when using the provided Caddy config.

Create the backend env file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:

- `APP_ENV=production`
- `SECRET_KEY` to a strong value from `openssl rand -hex 32`
- `DATABASE_URL=postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@db:5432/<POSTGRES_DB>`

The database values in `backend/.env` must match the values in the root `.env`.

### 4. Point DNS

Create an `A` record for your domain pointing to the VPS public IP. Caddy will automatically request HTTPS certificates once DNS points to the server.

For an IP-only test, set `DOMAIN=:80` in `.env`. HTTPS will not be automatic in that mode.

### 5. Start Production

```bash
docker compose -f prod.docker-compose.yml up -d --build
docker compose -f prod.docker-compose.yml logs -f
```

Open `https://your-domain`.

### Useful Commands

```bash
# Check services
docker compose -f prod.docker-compose.yml ps

# Follow backend logs
docker compose -f prod.docker-compose.yml logs -f backend

# Deploy a new version after git pull
docker compose -f prod.docker-compose.yml up -d --build

# Stop without deleting data
docker compose -f prod.docker-compose.yml down
```
