import app.models  # noqa: F401 - register all models with Base
from app.core.security import hash_password
from app.db import Base, SessionLocal, engine
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
