from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String


class Base(DeclarativeBase):
    pass

class Room(Base):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(String(30), nullable=False)
    date: Mapped[str] = mapped_column(String(30), nullable=False)
    time_slots = [f"{hour:02d}:00" for hour in range(24)]
    for time_slot in time_slots:
        locals()[time_slot] = mapped_column(String(30), nullable=True)
        
    def __repr__(self) -> str:
        return f"Room(id={self.id!r}, location={self.location!r}, date={self.date!r}, " + \
               ', '.join(f"{slot}={getattr(self, slot)!r}" for slot in self.time_slots)
        