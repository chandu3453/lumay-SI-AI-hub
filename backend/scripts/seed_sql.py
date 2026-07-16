"""Database Seeder Script — Populates SQLite tables with synthetic data.

Run via:
    python scripts/seed_sql.py
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.platform.database.session import init_db_engine, get_session_factory, close_db_engine
from app.demo.synthetic import generate_synthetic_data, get_synthetic_store
from domains.customer.models.customer import Customer
from domains.customer.constants.customer_constants import CustomerSegment, CustomerStatus, CustomerType
from domains.interaction.models.interaction import Interaction
from domains.interaction.constants.interaction_constants import InteractionChannel, InteractionDirection, InteractionStatus
from domains.complaint.models.complaint import Complaint
from domains.workflow.models.workflow import Workflow
from domains.notification.models.notification import Notification

async def seed():
    print("Initializing database engine...")
    await init_db_engine()
    
    print("Generating synthetic demo data...")
    store = generate_synthetic_data()
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        # 1. Seed Customers
        customers_data = store.get("customers")
        print(f"Generating {len(customers_data)} customers inside SQL database...")
        
        # Check if table already populated
        from sqlalchemy import select, func
        cust_count_query = select(func.count(Customer.id))
        result = await session.execute(cust_count_query)
        count = result.scalar_one()
        
        if count > 0:
            print(f"Database already has {count} customers. Skipping seeding.")
        else:
            for idx, c in enumerate(customers_data):
                try:
                    cust_uuid = uuid.UUID(c["id"])
                    created_at_dt = datetime.fromisoformat(c["created_at"])
                except Exception:
                    cust_uuid = uuid.uuid4()
                    created_at_dt = datetime.now(timezone.utc)
                
                # Mock profile metadata for the customer
                # Let's add policy_number and product fields as used in conversation engine
                policy_num = f"POL-{10000 + idx}-22"
                product = "Motor Comprehensive" if idx % 2 == 0 else "Medical Insurance"
                if idx % 5 == 0:
                    product = "Travel Insurance"
                elif idx % 5 == 1:
                    product = "Home Comprehensive"
                
                profile_meta = {
                    "policy_number": policy_num,
                    "product": product,
                }
                
                cust = Customer(
                    id=cust_uuid,
                    customer_number=c["customer_number"],
                    external_ref=c["external_ref"],
                    full_name=c["full_name"],
                    email=c["email"],
                    mobile_number=c["mobile_number"],
                    segment=CustomerSegment(c["segment"]),
                    status=CustomerStatus(c["status"]),
                    customer_type=CustomerType.ACTIVE,
                    profile_metadata=profile_meta,
                    created_at=created_at_dt,
                    updated_at=created_at_dt,
                )
                session.add(cust)
            
            # Let's add Fatima Al Lawati specifically if she doesn't exist
            # FATIMA details:
            # id: "cust-102"
            # name: "Fatima Al Lawati"
            # phone: "+968 9912 3456"
            # email: "fatima.lawati@email.com"
            # policyNumber: "POL-99281-22"
            # product: "Motor Comprehensive"
            fatima_email = "fatima.lawati@email.com"
            fatima_check = [c for c in customers_data if c["email"] == fatima_email]
            if not fatima_check:
                fatima = Customer(
                    id=uuid.uuid4(),
                    customer_number="CUST-99999",
                    external_ref="cust-102",
                    full_name="Fatima Al Lawati",
                    email=fatima_email,
                    mobile_number="+968 9912 3456",
                    segment=CustomerSegment.VIP,
                    status=CustomerStatus.ACTIVE,
                    customer_type=CustomerType.ACTIVE,
                    profile_metadata={
                        "policy_number": "POL-99281-22",
                        "product": "Motor Comprehensive",
                        "city": "Muscat",
                    },
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(fatima)
                print("Added Fatima Al Lawati VIP customer record.")
            
            await session.commit()
            print("Successfully seeded customers table in SQL database.")
            
    print("Database seeding completed.")
    await close_db_engine()

if __name__ == "__main__":
    asyncio.run(seed())
