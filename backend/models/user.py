from sqlalchemy import Column, Integer, String, BigInteger, Float
from sqlalchemy.orm import relationship
from backend.objects.Database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    balance = Column(Float, default=0)

    vpn_keys = relationship("VPNKeys", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, first_name='{self.first_name}', balance={self.balance})>"
