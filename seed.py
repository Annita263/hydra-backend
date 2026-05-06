"""
Run this once to create the tables and seed the two HYDRA product variants.
Usage: python seed.py
"""
from app.database import engine, SessionLocal, Base
from app.models.models import Product  # noqa — needed to register the model

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Tables created")

db = SessionLocal()

# Only seed if products table is empty
if db.query(Product).count() == 0:
    products = [
        Product(
            name="HYDRA CORE",
            variant="core",
            description=(
                "Everyday electrolyte hydration for daily life. "
                "Clean, low-sugar, balanced sodium, potassium, and magnesium. "
                "Designed for hot climates and long commutes."
            ),
            price=1500.0,   # ₦1,500 per unit — update as needed
            stock=200,
        ),
        Product(
            name="HYDRA ACTIVE",
            variant="active",
            description=(
                "Enhanced electrolyte formula for fitness and recovery. "
                "Higher magnesium for muscle support, zero sugar. "
                "Clean hydration that won't undo your gym progress."
            ),
            price=2000.0,   # ₦2,000 per unit — update as needed
            stock=200,
        ),
    ]
    db.add_all(products)
    db.commit()
    print("✓ Products seeded: HYDRA CORE (₦1,500) and HYDRA ACTIVE (₦2,000)")
else:
    print("→ Products already exist, skipping seed")

db.close()
print("✓ Done — run: uvicorn app.main:app --reload")
