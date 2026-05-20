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
