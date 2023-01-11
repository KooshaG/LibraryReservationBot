from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

base = declarative_base()

class User(base):
  __tablename__ = 'users'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(128), nullable=False)
  password = Column(String(128), nullable=False)
  
  reserved_dates = relationship("ReservedDate", back_populates="user", cascade="all, delete-orphan")
  reservation_requests = relationship("ReservationRequest", back_populates="user", cascade="all, delete-orphan")
  

class ReservedDate(base):
  __tablename__ = 'reserved_date'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  day_since_epoch = Column(Integer, nullable=False)
  
  user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
  user = relationship("User", back_populates="reserved_dates")


class ReservationRequest(base):
  __tablename__ = 'reservation_requests'
  
  id = Column(Integer, primary_key=True, autoincrement=True)

  dow = Column(String(32), nullable=False)
  iso_weekday = Column(Integer, nullable=False)
  slots30mins = Column(Integer, nullable=False)
  startTime = Column(String(32), nullable=False)
  startTime = Column(String(32), nullable=False)
  
  user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
  user = relationship("User", back_populates="reserved_dates")

  
  def __repr__(self):
    return f"ReservationRequest(dow='{self.dow}', iso_weekday={self.iso_weekday}, startTime='{self.startTime}', endTime='{self.endTime}', slots30mins={self.slots30mins})"
