import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import User, Donor, Hospital, Pharmacy, Medicine, BloodStock

# Import Routers
from app.routers import (
    auth,
    users,
    donors,
    hospitals,
    pharmacies,
    medicines,
    blood_requests,
    matching,
    notifications,
    admin,
    blood_stock
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lifelink")

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Emergency Healthcare Coordination Platform connecting Patients, Blood Donors, Hospitals, Pharmacies & Administrators.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive for prototype dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handlers for consistent API responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected server error occurred. Please try again later."
        }
    )

# Register Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(donors.router)
app.include_router(hospitals.router)
app.include_router(pharmacies.router)
app.include_router(medicines.router)
app.include_router(blood_requests.router)
app.include_router(matching.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(blood_stock.router)

@app.on_event("startup")
def auto_seed_database_if_empty():
    """Seed initial demo data if database is brand new."""

    db: Session = SessionLocal()

    try:
        user_count = db.query(User).count()

        if user_count == 0:
            logger.info("Database empty. Populating LifeLink demo dataset...")

            from app.security import hash_password
            from datetime import date

            # ---------------------------------------------------------
            # PASSWORD
            # ---------------------------------------------------------
            # Keep this short because bcrypt has a 72-byte limitation.
            demo_password = "LifeLink@123"
            pass_hash = hash_password(demo_password)

            # =========================================================
            # 1. ADMIN
            # =========================================================

            admin_user = User(
                full_name="LifeLink Admin",
                email="admin@lifelink.org",
                phone="+91 9876543210",
                password_hash=pass_hash,
                role="admin",
                address="Central Health Admin Tower",
                city="Bengaluru",
                latitude=12.9716,
                longitude=77.5946
            )

            db.add(admin_user)

            # =========================================================
            # 2. PATIENT
            # =========================================================

            patient_user = User(
                full_name="Aarav Sharma",
                email="patient1@example.com",
                phone="+91 9812345670",
                password_hash=pass_hash,
                role="patient",
                address="102 MG Road, Indiranagar",
                city="Bengaluru",
                latitude=12.9784,
                longitude=77.6408
            )

            db.add(patient_user)

            # =========================================================
            # 3. DONOR 1 - RAVI
            # =========================================================

            donor_user_1 = User(
                full_name="Ravi Kumar",
                email="ravi.kumar@example.com",
                phone="+91 9900112233",
                password_hash=pass_hash,
                role="donor",
                address="Indiranagar 100ft Road",
                city="Bengaluru",
                latitude=12.9719,
                longitude=77.6412
            )

            db.add(donor_user_1)
            db.flush()

            donor_1 = Donor(
                user_id=donor_user_1.id,
                blood_group="O+",
                date_of_birth=date(1992, 5, 14),
                availability_status="available",
                latitude=12.9719,
                longitude=77.6412,
                city="Bengaluru",
                response_rate=95.0,
                total_donations=6,
                verified=True
            )

            db.add(donor_1)

            # =========================================================
            # 4. DONOR 2 - PRIYA
            # =========================================================

            donor_user_2 = User(
                full_name="Priya Sharma",
                email="priya.sharma@example.com",
                phone="+91 9911223344",
                password_hash=pass_hash,
                role="donor",
                address="Koramangala 5th Block",
                city="Bengaluru",
                latitude=12.9352,
                longitude=77.6245
            )

            db.add(donor_user_2)
            db.flush()

            donor_2 = Donor(
                user_id=donor_user_2.id,
                blood_group="O+",
                date_of_birth=date(1995, 8, 21),
                availability_status="available",
                latitude=12.9352,
                longitude=77.6245,
                city="Bengaluru",
                response_rate=90.0,
                total_donations=4,
                verified=True
            )

            db.add(donor_2)

            # =========================================================
            # 5. DONOR 3 - ARJUN
            # =========================================================

            donor_user_3 = User(
                full_name="Arjun Raj",
                email="arjun.raj@example.com",
                phone="+91 9887766554",
                password_hash=pass_hash,
                role="donor",
                address="Velachery Main Road",
                city="Chennai",
                latitude=12.9750,
                longitude=80.2200
            )

            db.add(donor_user_3)
            db.flush()

            donor_3 = Donor(
                user_id=donor_user_3.id,
                blood_group="A+",
                date_of_birth=date(1994, 3, 10),
                availability_status="available",
                latitude=12.9750,
                longitude=80.2200,
                city="Chennai",
                response_rate=88.0,
                total_donations=3,
                verified=True
            )

            db.add(donor_3)

            # =========================================================
            # 6. DONOR 4 - KAVYA
            # =========================================================

            donor_user_4 = User(
                full_name="Kavya Menon",
                email="kavya.menon@example.com",
                phone="+91 9876655443",
                password_hash=pass_hash,
                role="donor",
                address="HSR Layout",
                city="Bengaluru",
                latitude=12.9116,
                longitude=77.6389
            )

            db.add(donor_user_4)
            db.flush()

            donor_4 = Donor(
                user_id=donor_user_4.id,
                blood_group="B+",
                date_of_birth=date(1996, 11, 5),
                availability_status="available",
                latitude=12.9116,
                longitude=77.6389,
                city="Bengaluru",
                response_rate=92.0,
                total_donations=5,
                verified=True
            )

            db.add(donor_4)

            # =========================================================
            # 7. HOSPITAL
            # =========================================================

            hosp_user = User(
                full_name="Manipal Hospital Indiranagar",
                email="manipal@lifelink.org",
                phone="+91 8025024444",
                password_hash=pass_hash,
                role="hospital",
                address="98 HAL Old Airport Rd",
                city="Bengaluru",
                latitude=12.9585,
                longitude=77.6483
            )

            db.add(hosp_user)
            db.flush()

            hosp_profile = Hospital(
                user_id=hosp_user.id,
                hospital_name="Manipal Hospital Indiranagar",
                registration_number="REG-KA-BLR-001",
                phone="+91 8025024444",
                address="98 HAL Old Airport Rd",
                city="Bengaluru",
                latitude=12.9585,
                longitude=77.6483,
                verified=True
            )

            db.add(hosp_profile)
            db.flush()

            # Blood stock
            for bg in [
                "A+",
                "A-",
                "B+",
                "B-",
                "AB+",
                "AB-",
                "O+",
                "O-"
            ]:
                db.add(
                    BloodStock(
                        hospital_id=hosp_profile.id,
                        blood_group=bg,
                        units_available=15,
                        low_stock_threshold=5
                    )
                )

            # =========================================================
            # 8. PHARMACY 1 - APOLLO
            # =========================================================

            pharm_user_1 = User(
                full_name="Apollo Pharmacy Koramangala",
                email="apollopharm1@lifelink.org",
                phone="+91 8025531122",
                password_hash=pass_hash,
                role="pharmacy",
                address="12 Koramangala 5th Block",
                city="Bengaluru",
                latitude=12.9350,
                longitude=77.6150
            )

            db.add(pharm_user_1)
            db.flush()

            pharm_profile_1 = Pharmacy(
                user_id=pharm_user_1.id,
                pharmacy_name="Apollo Pharmacy Koramangala",
                phone="+91 8025531122",
                address="12 Koramangala 5th Block",
                city="Bengaluru",
                latitude=12.9350,
                longitude=77.6150,
                opening_time="08:00",
                closing_time="22:00",
                verified=True
            )

            db.add(pharm_profile_1)
            db.flush()

            # Apollo medicines

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_1.id,
                    medicine_name="Paracetamol 650mg",
                    generic_name="Acetaminophen",
                    category="Analgesics",
                    quantity=150,
                    unit="tablets",
                    price=32.50,
                    availability_status="in_stock"
                )
            )

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_1.id,
                    medicine_name="Amoxicillin 500mg",
                    generic_name="Amoxicillin Trihydrate",
                    category="Antibiotics",
                    quantity=60,
                    unit="capsules",
                    price=120.00,
                    availability_status="in_stock"
                )
            )

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_1.id,
                    medicine_name="Insulin Glargine",
                    generic_name="Insulin Glargine",
                    category="Diabetes",
                    quantity=25,
                    unit="vials",
                    price=650.00,
                    availability_status="in_stock"
                )
            )

            # =========================================================
            # 9. PHARMACY 2 - MEDPLUS
            # =========================================================

            pharm_user_2 = User(
                full_name="MedPlus Pharmacy Chennai",
                email="medplus@lifelink.org",
                phone="+91 4422334455",
                password_hash=pass_hash,
                role="pharmacy",
                address="45 Velachery Main Road",
                city="Chennai",
                latitude=12.9750,
                longitude=80.2200
            )

            db.add(pharm_user_2)
            db.flush()

            pharm_profile_2 = Pharmacy(
                user_id=pharm_user_2.id,
                pharmacy_name="MedPlus Pharmacy Chennai",
                phone="+91 4422334455",
                address="45 Velachery Main Road",
                city="Chennai",
                latitude=12.9750,
                longitude=80.2200,
                opening_time="07:30",
                closing_time="23:00",
                verified=True
            )

            db.add(pharm_profile_2)
            db.flush()

            # MedPlus medicines

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_2.id,
                    medicine_name="Paracetamol 500mg",
                    generic_name="Acetaminophen",
                    category="Analgesics",
                    quantity=120,
                    unit="tablets",
                    price=28.00,
                    availability_status="in_stock"
                )
            )

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_2.id,
                    medicine_name="Azithromycin 500mg",
                    generic_name="Azithromycin",
                    category="Antibiotics",
                    quantity=60,
                    unit="tablets",
                    price=72.00,
                    availability_status="in_stock"
                )
            )

            db.add(
                Medicine(
                    pharmacy_id=pharm_profile_2.id,
                    medicine_name="Cetirizine 10mg",
                    generic_name="Cetirizine Hydrochloride",
                    category="Antihistamines",
                    quantity=100,
                    unit="tablets",
                    price=25.00,
                    availability_status="in_stock"
                )
            )

            # =========================================================
            # COMMIT EVERYTHING
            # =========================================================

            db.commit()

            logger.info(
                "LifeLink demo dataset created successfully!"
            )

        else:
            logger.info(
                f"Database already contains {user_count} users. "
                "Skipping auto-seed."
            )

    except Exception as e:
        logger.error(f"Auto-seed exception: {e}")
        db.rollback()

    finally:
        db.close()