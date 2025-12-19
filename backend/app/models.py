from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .db import Base


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))

    train_journeys = relationship("TrainJourney", back_populates="schedule")
    carriage_prices = relationship("CarriagePrice", back_populates="schedule")


class TrainStation(Base):
    __tablename__ = "train_station"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(200))

    journey_stations = relationship("JourneyStation", back_populates="station")


class TrainJourney(Base):
    __tablename__ = "train_journey"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    name = Column(String(500))

    schedule = relationship("Schedule", back_populates="train_journeys")
    journey_stations = relationship("JourneyStation", back_populates="journey", order_by="JourneyStation.stop_order")
    journey_carriages = relationship("JourneyCarriage", back_populates="journey")
    bookings = relationship("Booking", back_populates="train_journey")


class JourneyStation(Base):
    __tablename__ = "journey_station"

    journey_id = Column(Integer, ForeignKey("train_journey.id"), primary_key=True)
    station_id = Column(Integer, ForeignKey("train_station.id"), primary_key=True)
    stop_order = Column(Integer)
    departure_time = Column(DateTime)

    journey = relationship("TrainJourney", back_populates="journey_stations")
    station = relationship("TrainStation", back_populates="journey_stations")


class CarriageClass(Base):
    __tablename__ = "carriage_class"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(50))
    seating_capacity = Column(Integer)

    journey_carriages = relationship("JourneyCarriage", back_populates="carriage_class")
    carriage_prices = relationship("CarriagePrice", back_populates="carriage_class")
    bookings = relationship("Booking", back_populates="ticket_class")


class JourneyCarriage(Base):
    __tablename__ = "journey_carriage"

    journey_id = Column(Integer, ForeignKey("train_journey.id"), primary_key=True)
    carriage_class_id = Column(Integer, ForeignKey("carriage_class.id"), primary_key=True)
    position = Column(Integer)

    journey = relationship("TrainJourney", back_populates="journey_carriages")
    carriage_class = relationship("CarriageClass", back_populates="journey_carriages")


class CarriagePrice(Base):
    __tablename__ = "carriage_price"

    schedule_id = Column(Integer, ForeignKey("schedule.id"), primary_key=True)
    carriage_class_id = Column(Integer, ForeignKey("carriage_class.id"), primary_key=True)
    price = Column(Integer)

    schedule = relationship("Schedule", back_populates="carriage_prices")
    carriage_class = relationship("CarriageClass", back_populates="carriage_prices")


class BookingStatus(Base):
    __tablename__ = "booking_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))

    bookings = relationship("Booking", back_populates="status")


class Passenger(Base):
    __tablename__ = "passenger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(500))
    last_name = Column(String(500))
    email_address = Column(String(350), unique=True, index=True)
    password = Column(String(500))

    bookings = relationship("Booking", back_populates="passenger")


class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey("passenger.id"))
    status_id = Column(Integer, ForeignKey("booking_status.id"))
    booking_date = Column(Date)
    starting_station_id = Column(Integer, ForeignKey("train_station.id"))
    ending_station_id = Column(Integer, ForeignKey("train_station.id"))
    train_journey_id = Column(Integer, ForeignKey("train_journey.id"))
    ticket_class_id = Column(Integer, ForeignKey("carriage_class.id"))
    amount_paid = Column(Integer)
    ticket_no = Column(Integer, unique=True, index=True)
    seat_no = Column(String(5))

    passenger = relationship("Passenger", back_populates="bookings")
    status = relationship("BookingStatus", back_populates="bookings")
    starting_station = relationship("TrainStation", foreign_keys=[starting_station_id])
    ending_station = relationship("TrainStation", foreign_keys=[ending_station_id])
    train_journey = relationship("TrainJourney", back_populates="bookings")
    ticket_class = relationship("CarriageClass", back_populates="bookings")