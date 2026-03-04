from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    street: str = Column(String, nullable=False)
    city: str = Column(String, nullable=False)
    state: str = Column(String, nullable=False)
    zip_code: str = Column(String, nullable=False)
    country: str = Column(String, nullable=False)
    latitude: float = Column(Float, nullable=False)
    longitude: float = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, city='{self.city}', lat={self.latitude}, lon={self.longitude})>"
