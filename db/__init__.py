from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
import os

DB_HOSTNAME = os.environ['DB_HOSTNAME']
DB_DATABASE = os.environ['DB_DATABASE']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_DATABASE}?sslmode=require"

Base = declarative_base()

class User(Base):
  __tablename__ = 'users'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  
  username = Column(String(128), nullable=False)
  password = Column(String(128), nullable=False)
  
  concordia_email = Column(String(128), nullable=False)
  concordia_password = Column(String(128), nullable=False)
  
  reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")
  reservationRequests = relationship("ReservationRequest", back_populates="user", cascade="all, delete-orphan")
  
  def __repr__(self):
    return f"ReservationRequest(id={self.id}, username='{self.username}', password={self.password})"
  

class Reservation(Base):
  __tablename__ = 'reservation'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  day_since_epoch = Column(Integer, nullable=False)
  actual_date = Column(DateTime, nullable=False)
  
  startTime = Column(String, nullable=False)
  endTime = Column(String, nullable=False)
  
  users_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  user = relationship("User", back_populates="reservations")
    

class Room(Base):
  __tablename__ = 'rooms'
  
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(64), nullable=False, unique=True)
  tech = Column(Boolean, nullable=False)
  priority = Column(Integer, nullable=False)
  seats = Column(Boolean, nullable=False)  
  
class ReservationRequest(Base):
  __tablename__ = 'reservation_requests'
  
  id = Column(Integer, primary_key=True, autoincrement=True)

  dow = Column(String(32), nullable=False)
  iso_weekday = Column(Integer, nullable=False)
  slots30mins = Column(Integer, nullable=False)
  startTime = Column(String(32), nullable=False)
  startTime = Column(String(32), nullable=False)
  
  users_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  user = relationship("User", back_populates="reservations")

  
  def __repr__(self):
    return f"ReservationRequest(id={self.id}, dow='{self.dow}', iso_weekday={self.iso_weekday}, startTime='{self.startTime}', endTime='{self.endTime}', slots30mins={self.slots30mins}, user_id={self.user_id})"

def createObjects(engine):
  
  with Session(engine) as session:
    test_user = User(
      username = "Nice",
      password = "Cool",
      concordia_username = "koosha.cool@concordia.ca",
      concordia_password = "fart"
    )
    
    test_room = Room(
      name = "LB 257 - Croatia",
      tech = True,
      priority = 1,
      seats = True
    )
    
    session.add(test_room)
    session.add(test_user)
  

if __name__ == "__main__":
  engine = create_engine(CONNECTION_STRING, echo=True, future=True)
  Base.metadata.create_all(engine)
  # print(engine.table_names)
  createObjects(engine)
