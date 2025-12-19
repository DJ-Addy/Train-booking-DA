from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List


# ============================================================================
# STATION SCHEMAS
# ============================================================================

class StationBase(BaseModel):
    station_name: str


class StationCreate(StationBase):
    pass


class StationResponse(StationBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================================
# SCHEDULE SCHEMAS
# ============================================================================

class ScheduleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ============================================================================
# CARRIAGE CLASS SCHEMAS
# ============================================================================

class CarriageClassResponse(BaseModel):
    id: int
    class_name: str
    seating_capacity: int

    class Config:
        from_attributes = True


# ============================================================================
# PASSENGER SCHEMAS
# ============================================================================

class PassengerBase(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr


class PassengerCreate(PassengerBase):
    password: str = Field(min_length=6)


class PassengerResponse(PassengerBase):
    id: int

    class Config:
        from_attributes = True


class PassengerLogin(BaseModel):
    email_address: EmailStr
    password: str


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    passenger_id: Optional[int] = None


# ============================================================================
# JOURNEY SCHEMAS
# ============================================================================

class JourneyStationDetail(BaseModel):
    station_id: int
    station_name: str
    stop_order: int
    departure_time: datetime

    class Config:
        from_attributes = True


class AvailableClassInfo(BaseModel):
    class_id: int
    class_name: str
    price: int
    seating_capacity: int
    seats_available: int


class JourneySearchRequest(BaseModel):
    origin_station_id: int
    destination_station_id: int
    travel_date: date


class JourneySearchResponse(BaseModel):
    journey_id: int
    journey_name: str
    schedule_id: int
    schedule_name: str
    stations: List[JourneyStationDetail]
    available_classes: List[AvailableClassInfo]


class JourneyDetailResponse(BaseModel):
    id: int
    name: str
    schedule_id: int
    schedule_name: str
    stations: List[JourneyStationDetail]

    class Config:
        from_attributes = True


# ============================================================================
# BOOKING SCHEMAS
# ============================================================================

class BookingCreate(BaseModel):
    starting_station_id: int
    ending_station_id: int
    train_journey_id: int
    ticket_class_id: int
    seat_no: str = Field(max_length=5)


class BookingResponse(BaseModel):
    id: int
    passenger_id: int
    status_id: int
    booking_date: date
    starting_station_id: int
    ending_station_id: int
    train_journey_id: int
    ticket_class_id: int
    amount_paid: int
    ticket_no: int
    seat_no: str

    class Config:
        from_attributes = True


class BookingDetailResponse(BaseModel):
    id: int
    ticket_no: int
    booking_date: date
    passenger_name: str
    origin_station: str
    destination_station: str
    journey_name: str
    class_name: str
    seat_no: str
    amount_paid: int
    status_name: str


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class BookingStatsResponse(BaseModel):
    total_bookings: int
    total_revenue: float
    average_booking_value: float
    bookings_by_status: dict
    bookings_by_class: dict


class RevenueStatsResponse(BaseModel):
    total_revenue: float
    revenue_by_date: List[dict]  # [{"date": "2024-03-15", "revenue": 1500}, ...]
    revenue_by_class: List[dict]  # [{"class": "First", "revenue": 5000}, ...]
    revenue_by_route: List[dict]  # [{"route": "NY-Boston", "revenue": 3000}, ...]


class PopularRouteResponse(BaseModel):
    origin: str
    destination: str
    booking_count: int
    total_revenue: float
    average_price: float


class DailyBookingTrendResponse(BaseModel):
    date: str
    booking_count: int
    revenue: float


class ClassDistributionResponse(BaseModel):
    class_name: str
    booking_count: int
    revenue: float
    percentage: float


class AnalyticsDashboardResponse(BaseModel):
    overview: BookingStatsResponse
    daily_trends: List[DailyBookingTrendResponse]
    popular_routes: List[PopularRouteResponse]
    class_distribution: List[ClassDistributionResponse]


class DateRangeRequest(BaseModel):
    start_date: date
    end_date: date