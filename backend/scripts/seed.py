import app.models  # noqa: F401 - register all models with Base
from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
from app.models.program_studi import ProgramStudi
from app.models.role import Role
from app.models.user import User


def seed():
    Base.metadata.create_all(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        # Seed roles
        role_names = ["admin", "pimpinan", "koordinator", "tim_prodi"]
        roles = {}
        for name in role_names:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name)
                db.add(role)
                db.flush()
                print(f"Seeded role: {name}")
            else:
                print(f"Role already exists: {name}")
            roles[name] = role

        db.commit()

        # Seed program studi
        prodi_data = [
            {"kode": "IF", "nama": "Teknik Informatika", "jenjang": "S1", "fakultas": "STEI", "perguruan_tinggi": "Institut Teknologi Bandung"},
            {"kode": "EL", "nama": "Teknik Elektro", "jenjang": "S1", "fakultas": "STEI", "perguruan_tinggi": "Institut Teknologi Bandung"},
            {"kode": "TE", "nama": "Teknik Tenaga Listrik", "jenjang": "S1", "fakultas": "STEI", "perguruan_tinggi": "Institut Teknologi Bandung"},
            {"kode": "TS", "nama": "Teknik Telekomunikasi", "jenjang": "S1", "fakultas": "STEI", "perguruan_tinggi": "Institut Teknologi Bandung"},
            {"kode": "SI", "nama": "Sistem dan Teknologi Informasi", "jenjang": "S1", "fakultas": "STEI", "perguruan_tinggi": "Institut Teknologi Bandung"},
        ]
        for data in prodi_data:
            existing_ps = db.query(ProgramStudi).filter(ProgramStudi.kode == data["kode"]).first()
            if existing_ps:
                print(f"Program studi already exists: {data['nama']}")
            else:
                ps = ProgramStudi(**data)
                db.add(ps)
                print(f"Seeded program studi: {data['nama']}")
        db.commit()

        # Seed admin user
        admin_email = "admin@stei.itb.ac.id"
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"User already exists: id={existing.id}, email={existing.email}")
        else:
            admin = User(
                email=admin_email,
                hashed_password=hash_password("admin123"),
                nama="Admin User",
                role_id=roles["admin"].id,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Seeded user: id={admin.id}, email={admin.email}, role=admin")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
