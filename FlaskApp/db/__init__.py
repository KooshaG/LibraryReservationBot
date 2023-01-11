from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship

base = declarative_base()

class User(base):
  __tablename__ = 'users'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(128), nullable=False)
  password = Column(String(128), nullable=False)
  
  reserved_dates = relationship("ReservedDate", back_populates="user", cascade="all, delete-orphan")
  reservation_requests = relationship("ReservationRequest", back_populates="user", cascade="all, delete-orphan")
  
  def __repr__(self):
    return f"ReservationRequest(id={self.id}, username='{self.username}', password={self.password})"
  

class Reservation(base):
  __tablename__ = 'reservation'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  day_since_epoch = Column(Integer, nullable=False)
  room_id = Column(Integer, ForeignKey("room.id"), nullable=False)
  
  user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
  user = relationship("User", back_populates="reserved_dates")
  
  room = relationship("Room", back_populates="room")
  
  

class Room(base):
  __tablename__ = 'room'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(64), nullable=False)
  tech = Column(Boolean, nullable=False)
  priority = Column(Integer, nullable=False)
  seats = Column(Boolean, nullable=False)
  
  reservations = relationship("Reservation", back_populates="reservation")
  
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
    return f"ReservationRequest(id={self.id}, dow='{self.dow}', iso_weekday={self.iso_weekday}, startTime='{self.startTime}', endTime='{self.endTime}', slots30mins={self.slots30mins}, user_id={self.user_id})"
