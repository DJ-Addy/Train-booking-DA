from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional
import pandas as pd

from ..db import get_db
from ..models import Booking, TrainStation, CarriageClass, BookingStatus, Passenger, TrainJourney
from .. import schemas

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_date_range(days: int = 30):
    """Get default date range"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def get_bookings_df(db: Session, start_date: date = None, end_date: date = None) -> pd.DataFrame:
    """
    Load bookings into pandas DataFrame with all related data.
    This is the core function that feeds all analytics.
    """
    if not start_date or not end_date:
        start_date, end_date = get_date_range(30)

    # Query all bookings with joins in one go
    query = """
        SELECT 
            b.id,
            b.booking_date,
            b.amount_paid,
            b.ticket_no,
            b.seat_no,
            s1.station_name as origin_station,
            s2.station_name as destination_station,
            cc.class_name,
            bs.name as status,
            p.first_name,
            p.last_name,
            p.email_address,
            tj.name as journey_name
        FROM booking b
        JOIN train_station s1 ON b.starting_station_id = s1.id
        JOIN train_station s2 ON b.ending_station_id = s2.id
        JOIN carriage_class cc ON b.ticket_class_id = cc.id
        JOIN booking_status bs ON b.status_id = bs.id
        JOIN passenger p ON b.passenger_id = p.id
        JOIN train_journey tj ON b.train_journey_id = tj.id
        WHERE b.booking_date BETWEEN %(start_date)s AND %(end_date)s
    """

    df = pd.read_sql(query, db.bind, params={'start_date': start_date, 'end_date': end_date})
    df['booking_date'] = pd.to_datetime(df['booking_date'])
    df['route'] = df['origin_station'] + ' → ' + df['destination_station']
    df['passenger_name'] = df['first_name'] + ' ' + df['last_name']

    return df


# ============================================================================
# BOOKING STATISTICS
# ============================================================================

@router.get("/bookings/stats", response_model=schemas.BookingStatsResponse)
def get_booking_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """Get comprehensive booking statistics using pandas"""
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return schemas.BookingStatsResponse(
            total_bookings=0,
            total_revenue=0.0,
            average_booking_value=0.0,
            bookings_by_status={},
            bookings_by_class={}
        )

    return schemas.BookingStatsResponse(
        total_bookings=len(df),
        total_revenue=float(df['amount_paid'].sum()),
        average_booking_value=float(df['amount_paid'].mean()),
        bookings_by_status=df['status'].value_counts().to_dict(),
        bookings_by_class=df['class_name'].value_counts().to_dict()
    )


# ============================================================================
# REVENUE ANALYTICS
# ============================================================================

@router.get("/revenue/stats", response_model=schemas.RevenueStatsResponse)
def get_revenue_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """Get detailed revenue analytics using pandas"""
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return schemas.RevenueStatsResponse(
            total_revenue=0.0,
            revenue_by_date=[],
            revenue_by_class=[],
            revenue_by_route=[]
        )

    # Revenue by date
    revenue_by_date = df.groupby('booking_date')['amount_paid'].sum().reset_index()
    revenue_by_date['booking_date'] = revenue_by_date['booking_date'].dt.strftime('%Y-%m-%d')
    revenue_by_date_list = revenue_by_date.rename(
        columns={'booking_date': 'date', 'amount_paid': 'revenue'}
    ).to_dict('records')

    # Revenue by class
    revenue_by_class = df.groupby('class_name')['amount_paid'].sum().reset_index()
    revenue_by_class_list = revenue_by_class.rename(
        columns={'class_name': 'class', 'amount_paid': 'revenue'}
    ).to_dict('records')

    # Revenue by route (top 10)
    revenue_by_route = df.groupby('route')['amount_paid'].sum().nlargest(10).reset_index()
    revenue_by_route_list = revenue_by_route.rename(
        columns={'amount_paid': 'revenue'}
    ).to_dict('records')

    return schemas.RevenueStatsResponse(
        total_revenue=float(df['amount_paid'].sum()),
        revenue_by_date=revenue_by_date_list,
        revenue_by_class=revenue_by_class_list,
        revenue_by_route=revenue_by_route_list
    )


# ============================================================================
# POPULAR ROUTES
# ============================================================================

@router.get("/popular-routes", response_model=List[schemas.PopularRouteResponse])
def get_popular_routes(
        limit: int = Query(10, ge=1, le=50),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """Get most popular routes by booking count using pandas"""
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return []

    # Group by route and aggregate
    route_stats = df.groupby(['origin_station', 'destination_station', 'route']).agg({
        'id': 'count',  # booking_count
        'amount_paid': ['sum', 'mean']  # total_revenue, average_price
    }).reset_index()

    # Flatten column names
    route_stats.columns = ['origin', 'destination', 'route', 'booking_count', 'total_revenue', 'average_price']

    # Sort by booking count and take top N
    route_stats = route_stats.nlargest(limit, 'booking_count')

    # Convert to response format
    return [
        schemas.PopularRouteResponse(
            origin=row['origin'],
            destination=row['destination'],
            booking_count=int(row['booking_count']),
            total_revenue=float(row['total_revenue']),
            average_price=float(row['average_price'])
        )
        for _, row in route_stats.iterrows()
    ]


# ============================================================================
# DAILY TRENDS
# ============================================================================

@router.get("/daily-trends", response_model=List[schemas.DailyBookingTrendResponse])
def get_daily_booking_trends(
        days: int = Query(30, ge=1, le=365),
        db: Session = Depends(get_db)
):
    """Get daily booking and revenue trends using pandas"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return []

    # Group by date and aggregate
    daily_stats = df.groupby('booking_date').agg({
        'id': 'count',  # booking_count
        'amount_paid': 'sum'  # revenue
    }).reset_index()

    daily_stats['booking_date'] = daily_stats['booking_date'].dt.strftime('%Y-%m-%d')

    return [
        schemas.DailyBookingTrendResponse(
            date=row['booking_date'],
            booking_count=int(row['id']),
            revenue=float(row['amount_paid'])
        )
        for _, row in daily_stats.iterrows()
    ]


# ============================================================================
# CLASS DISTRIBUTION
# ============================================================================

@router.get("/class-distribution", response_model=List[schemas.ClassDistributionResponse])
def get_class_distribution(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """Get booking and revenue distribution by carriage class using pandas"""
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return []

    # Group by class and aggregate
    class_stats = df.groupby('class_name').agg({
        'id': 'count',  # booking_count
        'amount_paid': 'sum'  # revenue
    }).reset_index()

    # Calculate percentages
    total_bookings = class_stats['id'].sum()
    class_stats['percentage'] = (class_stats['id'] / total_bookings * 100).round(2)

    return [
        schemas.ClassDistributionResponse(
            class_name=row['class_name'],
            booking_count=int(row['id']),
            revenue=float(row['amount_paid']),
            percentage=float(row['percentage'])
        )
        for _, row in class_stats.iterrows()
    ]


# ============================================================================
# COMPREHENSIVE DASHBOARD
# ============================================================================

@router.get("/dashboard", response_model=schemas.AnalyticsDashboardResponse)
def get_analytics_dashboard(
        days: int = Query(30, ge=1, le=365),
        db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard data in one call.
    At scale would fail would need to switch to caching and aggregation
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Get all components (all use the same DataFrame internally)
    overview = get_booking_statistics(start_date, end_date, db)
    daily_trends = get_daily_booking_trends(days, db)
    popular_routes = get_popular_routes(10, start_date, end_date, db)
    class_distribution = get_class_distribution(start_date, end_date, db)

    return schemas.AnalyticsDashboardResponse(
        overview=overview,
        daily_trends=daily_trends,
        popular_routes=popular_routes,
        class_distribution=class_distribution
    )

# ============================================================================
# PASSENGER ANALYTICS
# ============================================================================

@router.get("/passengers/top-spenders")
def get_top_spending_passengers(
        limit: int = Query(5, ge=1, le=50),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """
    Get top spending passengers using pandas
    Now accepts date range parameters to filter by time period
    """
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return []

    # Group by passenger and aggregate
    passenger_stats = df.groupby(['passenger_name', 'email_address']).agg({
        'id': 'count',  # total_bookings
        'amount_paid': 'sum'  # total_spent
    }).reset_index()

    # Sort by spending and take top N
    top_spenders = passenger_stats.nlargest(limit, 'amount_paid')

    return [
        {
            "name": row['passenger_name'],
            "email": row['email_address'],
            "total_bookings": int(row['id']),
            "total_spent": float(row['amount_paid'])
        }
        for _, row in top_spenders.iterrows()
    ]


# ============================================================================
# JOURNEY ANALYTICS
# ============================================================================

@router.get("/journeys/performance")
def get_journey_performance(
        limit: int = Query(5, ge=1, le=50),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    """
    Get journey performance metrics using pandas
    Now accepts date range parameters to filter by time period
    """
    df = get_bookings_df(db, start_date, end_date)

    if df.empty:
        return []

    # Group by journey and aggregate
    journey_stats = df.groupby('journey_name').agg({
        'id': 'count',  # total_bookings
        'amount_paid': ['sum', 'mean']  # total_revenue, avg_booking_value
    }).reset_index()

    # Flatten column names
    journey_stats.columns = ['journey_name', 'total_bookings', 'total_revenue', 'average_booking_value']

    # Sort by bookings and take top N
    top_journeys = journey_stats.nlargest(limit, 'total_bookings')

    return [
        {
            "journey_name": row['journey_name'],
            "total_bookings": int(row['total_bookings']),
            "total_revenue": float(row['total_revenue']),
            "average_booking_value": float(row['average_booking_value'])
        }
        for _, row in top_journeys.iterrows()
    ]