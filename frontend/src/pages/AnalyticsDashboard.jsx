import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { analyticsAPI } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  // Dashboard data
  const [overview, setOverview] = useState(null);
  const [dailyTrends, setDailyTrends] = useState([]);
  const [popularRoutes, setPopularRoutes] = useState([]);
  const [classDistribution, setClassDistribution] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await analyticsAPI.getDashboard(timeRange);
      const data = response.data;

      setOverview(data.overview);
      setDailyTrends(data.daily_trends);
      setPopularRoutes(data.popular_routes);
      setClassDistribution(data.class_distribution);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-xl">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>

        <div className="flex gap-2">
          <button
            onClick={() => setTimeRange(7)}
            className={`px-4 py-2 rounded ${timeRange === 7 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            7 Days
          </button>
          <button
            onClick={() => setTimeRange(30)}
            className={`px-4 py-2 rounded ${timeRange === 30 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            30 Days
          </button>
          <button
            onClick={() => setTimeRange(90)}
            className={`px-4 py-2 rounded ${timeRange === 90 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Total Bookings</h3>
            <p className="text-3xl font-bold text-blue-600">{overview.total_bookings}</p>
          </div>

          <div className="bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Total Revenue</h3>
            <p className="text-3xl font-bold text-green-600">
              ${overview.total_revenue.toLocaleString()}
            </p>
          </div>

          <div className="bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Average Booking Value</h3>
            <p className="text-3xl font-bold text-purple-600">
              ${overview.average_booking_value.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Daily Trends Chart */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Booking Trends</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyTrends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="booking_count"
              stroke="#8884d8"
              name="Bookings"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="revenue"
              stroke="#82ca9d"
              name="Revenue ($)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Popular Routes */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Popular Routes</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={popularRoutes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="origin" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="booking_count" fill="#8884d8" name="Bookings" />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4 space-y-2">
            {popularRoutes.slice(0, 5).map((route, index) => (
              <div key={index} className="flex justify-between items-center border-b pb-2">
                <span className="font-medium">
                  {route.origin} → {route.destination}
                </span>
                <div className="text-right">
                  <div className="text-sm text-gray-600">{route.booking_count} bookings</div>
                  <div className="text-sm font-semibold text-green-600">
                    ${route.total_revenue.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Class Distribution */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Booking Distribution by Class</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={classDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ class_name, percentage }) => `${class_name}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="booking_count"
              >
                {classDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="mt-4 space-y-2">
            {classDistribution.map((cls, index) => (
              <div key={index} className="flex justify-between items-center border-b pb-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-4 h-4 rounded"
                    style={{backgroundColor: COLORS[index % COLORS.length]}}
                  />
                  <span className="font-medium">{cls.class_name}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">{cls.booking_count} bookings</div>
                  <div className="text-sm font-semibold text-green-600">
                    ${cls.revenue.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;