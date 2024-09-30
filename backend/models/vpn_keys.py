from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.objects.Database import Base


class VPNKeys(Base):
    __tablename__ = 'vpn_keys'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    uuid = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    gb_limit = Column(Integer, nullable=False)

    user = relationship("User", back_populates="vpn_keys")

    def __repr__(self):
        return f"<VPNKeys(id={self.id}, user_id={self.user_id}, uuid='{self.uuid}', client_id='{self.client_id}', expires_at={self.expires_at})>"
