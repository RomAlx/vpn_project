from sqlalchemy.orm import Session
from backend.models import VPNKeys
from datetime import datetime
from sqlalchemy import and_

from backend.objects.Database import session


class VPNKeysRepository:

    @staticmethod
    def create_vpn_key(user_id: int, uuid: str, client_id: str, experation_time: int, gb_limit: int):
        vpn_key = VPNKeys(
            user_id=user_id,
            client_id=client_id,
            uuid=uuid,
            expires_at=datetime.fromtimestamp(experation_time / 1000),
            gb_limit=gb_limit
        )
        session.add(vpn_key)
        session.commit()
        return vpn_key

    @staticmethod
    def get_vpn_key_by_id(vpn_key_id: int) -> VPNKeys:
        return session.query(VPNKeys).filter(
            VPNKeys.id == vpn_key_id,
            VPNKeys.expires_at > datetime.now()
        ).first()

    @staticmethod
    def get_vpn_keys_by_user_id(user_id: int):
        return session.query(VPNKeys).filter(
            VPNKeys.user_id == user_id,
            VPNKeys.expires_at > datetime.now()
        ).all()

    @staticmethod
    def update_vpn_key(vpn_key_id: int, new_key: str, new_expires_at: datetime):
        vpn_key = VPNKeysRepository.get_vpn_key_by_id(vpn_key_id)
        if vpn_key:
            vpn_key.key = new_key
            vpn_key.expires_at = new_expires_at
            session.commit()
        return vpn_key

    @staticmethod
    def delete_vpn_key(vpn_key_id: int):
        vpn_key = VPNKeysRepository.get_vpn_key_by_id(vpn_key_id)
        if vpn_key:
            session.delete(vpn_key)
            session.commit()

    @staticmethod
    def list_all_vpn_keys():
        return session.query(VPNKeys).all()

    @staticmethod
    def get_keys_expiring_soon(expiration_threshold):
        current_time = datetime.utcnow()
        return session.query(VPNKeys).filter(
                VPNKeys.expires_at <= expiration_threshold
        ).all()
