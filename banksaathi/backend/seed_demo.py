"""
BankSathi Demo Seed Script

Seeds the standard hackathon demo environment described in DEMO.md and BankSathi_Trusted_Circle_Change.md:
- User: Meena Devi (Mother) (Phone: 9999999001, Password: demoPassword123!)
- Beneficiary: Ravi Kumar (Masked: ****4321, trust_level: known)
- Completed Transaction History:
  * ₹1,200 to Ravi Kumar (Groceries)
  * ₹1,800 to Electricity Bill
  * Baseline historical average: ₹1,500.00
- Trusted Circle Member: Ananya (Daughter) (Phone: 9999999002, Password: daughterPassword123!)
  * Active membership with relationship "Daughter"
- Pending Demo Transaction & Notification:
  * ₹5,000 to Ravi Kumar (Higher than usual -> MEDIUM Risk)
  * Trusted Circle notification waiting for Ananya's second opinion!
- Community Digital Literacy Sessions:
  * "Spotting Fraud Calls & Fake Bank SMS"
  * "How UPI QR Codes & Voice Banking Work"
"""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import get_settings
from app.core.auth import hash_password, hash_phone
from app.database import Base
from app.models.accessibility_profile import AccessibilityProfile
from app.models.beneficiary import Beneficiary
from app.models.community_session import CommunitySession, CommunitySessionStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.trusted_circle import (
    MemberStatus,
    NotificationStatus,
    TrustedCircleMember,
    TrustedCircleNotification,
)
from app.models.user import User

settings = get_settings()


async def seed():
    db_url = str(settings.database_url)
    try:
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"PostgreSQL unreachable ({e}). Falling back to local SQLite database for local demo: sqlite+aiosqlite:///./banksaathi_demo.db")
        db_url = "sqlite+aiosqlite:///./banksaathi_demo.db"
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Check or create Meena Devi (Mother)
        phone_hash = hash_phone("9999999001")
        res = await session.execute(select(User).where(User.phone_hash == phone_hash))
        meena = res.scalar_one_or_none()

        if not meena:
            meena = User(
                name="Meena Devi",
                phone_hash=phone_hash,
                hashed_password=hash_password("demoPassword123!"),
                role="user",
            )
            session.add(meena)
            await session.flush()

            # Add accessibility profile
            a11y = AccessibilityProfile(
                user_id=meena.id,
                language="en",
                font_scale=1.3,
                high_contrast=False,
                speech_rate=1.0,
                confirmation_mode="single",
            )
            session.add(a11y)

        # 2. Add Beneficiary: Ravi Kumar
        b_res = await session.execute(
            select(Beneficiary).where(Beneficiary.user_id == meena.id)
        )
        ravi = b_res.scalar_one_or_none()
        if not ravi:
            ravi = Beneficiary(
                user_id=meena.id,
                display_name="Ravi Kumar",
                masked_account="****4321",
                trust_level="known",
                last_used_at=datetime.now(timezone.utc) - timedelta(days=2),
            )
            session.add(ravi)
            await session.flush()

        # 3. Add History Transactions (₹1,200 and ₹1,800 -> Average ₹1,500)
        tx_res = await session.execute(
            select(Transaction).where(Transaction.user_id == meena.id)
        )
        existing_txs = tx_res.scalars().all()
        if not existing_txs:
            tx1 = Transaction(
                user_id=meena.id,
                beneficiary_id=ravi.id,
                beneficiary_name="Ravi Kumar",
                amount=Decimal("1200.00"),
                currency="INR",
                intent="TRANSFER",
                status=TransactionStatus.COMPLETED,
                risk_score=10,
                risk_level="LOW",
                bank_reference="DEMO-102938",
            )
            tx2 = Transaction(
                user_id=meena.id,
                beneficiary_name="Electricity Bill",
                amount=Decimal("1800.00"),
                currency="INR",
                intent="PAY_BILL",
                status=TransactionStatus.COMPLETED,
                risk_score=15,
                risk_level="LOW",
                bank_reference="DEMO-584732",
            )
            session.add_all([tx1, tx2])
            await session.flush()

        # 4. Add Trusted Circle Member: Ananya (Daughter)
        daughter_phone_hash = hash_phone("9999999002")
        d_res = await session.execute(
            select(User).where(User.phone_hash == daughter_phone_hash)
        )
        ananya = d_res.scalar_one_or_none()
        if not ananya:
            ananya = User(
                name="Ananya (Daughter)",
                phone_hash=daughter_phone_hash,
                hashed_password=hash_password("daughterPassword123!"),
                role="helper",
            )
            session.add(ananya)
            await session.flush()

        # Check or create Trusted Circle Membership
        tc_res = await session.execute(
            select(TrustedCircleMember).where(
                TrustedCircleMember.user_id == meena.id,
                TrustedCircleMember.trusted_person_id == ananya.id,
            )
        )
        membership = tc_res.scalar_one_or_none()
        if not membership:
            membership = TrustedCircleMember(
                user_id=meena.id,
                trusted_person_id=ananya.id,
                relationship_label="Daughter",
                status=MemberStatus.ACTIVE,
                verified_at=datetime.now(timezone.utc),
            )
            session.add(membership)
            await session.flush()

        # 5. Create Demo Flagged Transaction & Notification (₹5,000 to Ravi Kumar)
        pending_tx_res = await session.execute(
            select(Transaction).where(
                Transaction.user_id == meena.id,
                Transaction.status == TransactionStatus.AWAITING_CONFIRMATION,
            )
        )
        pending_tx = pending_tx_res.scalar_one_or_none()
        if not pending_tx:
            pending_tx = Transaction(
                user_id=meena.id,
                beneficiary_id=ravi.id,
                beneficiary_name="Ravi Kumar",
                amount=Decimal("5000.00"),
                currency="INR",
                intent="TRANSFER",
                status=TransactionStatus.AWAITING_CONFIRMATION,
                risk_score=40,
                risk_level="MEDIUM",
                risk_reasons={
                    "reasons": [
                        "Amount is 3.3x higher than your average transfer (₹1,500.00)",
                        "Recipient is known and trusted",
                        "Normal daytime transaction hours",
                    ]
                },
            )
            session.add(pending_tx)
            await session.flush()

            # Create notification for Ananya
            notif = TrustedCircleNotification(
                transaction_id=pending_tx.id,
                trusted_circle_member_id=membership.id,
                risk_level="MEDIUM",
                risk_reasons={
                    "reasons": [
                        "Amount is higher than typical recent transfers",
                        "Known recipient (Ravi Kumar)",
                    ]
                },
                amount_display="₹5,000.00",
                beneficiary_display="Ravi Kumar",
                status=NotificationStatus.PENDING,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
            )
            session.add(notif)

        # 6. Add Community Sessions
        c_res = await session.execute(select(CommunitySession))
        if not c_res.scalars().first():
            cs1 = CommunitySession(
                host_id=meena.id,
                topic="Spotting Fraud Calls & Fake Bank SMS",
                description="Learn how to detect callers pretending to be bank officials asking for OTP.",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
                max_participants=30,
                duration_minutes=45,
                status=CommunitySessionStatus.SCHEDULED,
            )
            cs2 = CommunitySession(
                host_id=meena.id,
                topic="How UPI QR Codes & Voice Banking Work",
                description="Hands-on practice paying small amounts safely using voice commands.",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
                max_participants=25,
                duration_minutes=30,
                status=CommunitySessionStatus.SCHEDULED,
            )
            session.add_all([cs1, cs2])

        await session.commit()
        print("Demo database seeded successfully with Meena Devi, Ananya (Daughter in Trusted Circle), and demo alert!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
