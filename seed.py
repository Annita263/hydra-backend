from app.database import engine, SessionLocal, Base
from app.models.models import Product

Base.metadata.create_all(bind=engine)
print("✓ Tables created")

db = SessionLocal()

# Clear existing products and reseed
db.query(Product).delete()
db.commit()

products = [
    Product(name="HYDRA 200ml 6-Pack",  variant="200ml_6-Pack",  description="200ml bottles, pack of 6. Clean electrolyte hydration for daily use.", price=1200.0, stock=200),
    Product(name="HYDRA 200ml 24-Pack", variant="200ml_24-Pack", description="200ml bottles, pack of 24. Best value for daily hydration.", price=4580.0, stock=200),
    Product(name="HYDRA 350ml 6-Pack",  variant="350ml_6-Pack",  description="350ml bottles, pack of 6. Perfect for long commutes and active days.", price=1500.0, stock=200),
    Product(name="HYDRA 350ml 24-Pack", variant="350ml_24-Pack", description="350ml bottles, pack of 24. Stock up and save.", price=5680.0, stock=200),
    Product(name="HYDRA 500ml 6-Pack",  variant="500ml_6-Pack",  description="500ml bottles, pack of 6. Maximum hydration for high activity.", price=1800.0, stock=200),
    Product(name="HYDRA 500ml 24-Pack", variant="500ml_24-Pack", description="500ml bottles, pack of 24. Best value for serious hydration.", price=6370.0, stock=200),
]

db.add_all(products)
db.commit()
print("✓ Products reseeded with size and pack variants")
db.close()