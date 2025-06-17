import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  Area,
  AreaChart,
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts';
import styles from './Dashboard.module.css';

interface DashboardData {
  totalConversations: number;
  avgResponseTime: number;
  customerSatisfaction: number;
  activeUsers: number;
  responseTimeData: ResponseTimeData[];
  satisfactionTrend: SatisfactionData[];
}

interface ResponseTimeData {
  time: string;
  responseTime: number;
  date: string;
}

interface SatisfactionData {
  period: string;
  satisfaction: number;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    dataKey: string;
    color: string;
  }>;
  label?: string;
}

const CustomTooltip: React.FC<TooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className={styles.customTooltip}>
        <p className={styles.tooltipLabel}>{`${label}`}</p>
        {payload.map((entry, index) => (
          <p key={index} className={styles.tooltipValue} style={{ color: entry.color }}>
            {`${entry.dataKey}: ${entry.value}${entry.dataKey.includes('Time') ? 's' : '%'}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // TODO: Replace with real API call
    const mockData: DashboardData = {
      totalConversations: 1234,
      avgResponseTime: 2.5,
      customerSatisfaction: 92,
      activeUsers: 456,
      responseTimeData: [
        { time: '00:00', responseTime: 3.2, date: '2025-06-17' },
        { time: '04:00', responseTime: 2.8, date: '2025-06-17' },
        { time: '08:00', responseTime: 2.1, date: '2025-06-17' },
        { time: '12:00', responseTime: 2.5, date: '2025-06-17' },
        { time: '16:00', responseTime: 1.9, date: '2025-06-17' },
        { time: '20:00', responseTime: 2.3, date: '2025-06-17' },
      ],
      satisfactionTrend: [
        { period: 'Week 1', satisfaction: 89 },
        { period: 'Week 2', satisfaction: 91 },
        { period: 'Week 3', satisfaction: 90 },
        { period: 'Week 4', satisfaction: 92 },
      ]
    };
    setTimeout(() => {
      setDashboardData(mockData);
      setIsLoading(false);
    }, 1000);
  }, []);

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingText}>Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.errorText}>Error loading dashboard data</div>
      </div>
    );
  }

  return (
    <div className={styles.dashboardRoot}>
      {/* Header */}
      <div className={styles.headerSection}>
        <h1 className={styles.title}>Analytics Dashboard</h1>
        <p className={styles.subtitle}>Monitor your customer support performance</p>
      </div>

      {/* Main Grid Layout */}
      <div className={styles.metricsGrid}>
        {/* Total Conversations Card */}
        <div className={styles.metricCard + ' ' + styles.blueCard}>
          <h3 className={styles.metricTitle}>Total Conversations</h3>
          <div className={styles.metricValueHero}>{dashboardData.totalConversations.toLocaleString()}</div>
          <p className={styles.metricLabel}>This month</p>
        </div>
        {/* Average Response Time Card */}
        <div className={styles.metricCard + ' ' + styles.greenCard}>
          <h3 className={styles.metricTitle}>Avg Response Time</h3>
          <div className={styles.metricValueHero}>{dashboardData.avgResponseTime}s</div>
          <p className={styles.metricLabel}>Last 7 days</p>
        </div>
        {/* Customer Satisfaction Card */}
        <div className={styles.metricCard + ' ' + styles.purpleCard}>
          <h3 className={styles.metricTitle}>Customer Satisfaction</h3>
          <div className={styles.metricValueHero}>{dashboardData.customerSatisfaction}%</div>
          <p className={styles.metricLabel}>Average rating</p>
        </div>
        {/* Active Users Card */}
        <div className={styles.metricCard + ' ' + styles.yellowCard}>
          <h3 className={styles.metricTitle}>Active Users</h3>
          <div className={styles.metricValueHero}>{dashboardData.activeUsers}</div>
          <p className={styles.metricLabel}>Currently online</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className={styles.chartsGrid}>
        {/* Response Time Trend Chart */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Response Time Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dashboardData.responseTimeData}>
              <defs>
                <linearGradient id="responseGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-system-border)" />
              <XAxis dataKey="time" stroke="var(--color-system-foreground-tertiary)" fontSize={12} />
              <YAxis stroke="var(--color-system-foreground-tertiary)" fontSize={12} tickFormatter={(value) => `${value}s`} />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="responseTime"
                stroke="#3B82F6"
                strokeWidth={2}
                fill="url(#responseGradient)"
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        {/* Customer Satisfaction Radial Chart */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Satisfaction Score</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadialBarChart 
              cx="50%" 
              cy="50%" 
              innerRadius="60%" 
              outerRadius="90%" 
              data={[{ name: 'Satisfaction', value: dashboardData.customerSatisfaction, fill: '#8B5CF6' }]}
            >
              <RadialBar
                dataKey="value"
                cornerRadius={10}
                fill="#8B5CF6"
              />
              <text 
                x="50%" 
                y="50%" 
                textAnchor="middle" 
                dominantBaseline="middle" 
                className={styles.radialText}
              >
                {dashboardData.customerSatisfaction}%
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Metrics Row */}
      <div className={styles.metricsRow}>
        {/* Satisfaction Trend Line Chart */}
        <div className={styles.metricsRowChart + ' ' + styles.metricsRowChartWide}>
          <h3 className={styles.chartTitle}>Satisfaction Trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={dashboardData.satisfactionTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-system-border)" />
              <XAxis dataKey="period" stroke="var(--color-system-foreground-tertiary)" fontSize={12} />
              <YAxis stroke="var(--color-system-foreground-tertiary)" fontSize={12} domain={[85, 95]} tickFormatter={(value) => `${value}%`} />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="satisfaction"
                stroke="#10B981"
                strokeWidth={3}
                dot={{ fill: '#10B981', strokeWidth: 2, r: 5 }}
                activeDot={{ r: 7, stroke: '#10B981', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* Quick Stats */}
        <div className={styles.metricsRowStats}>
          <h3 className={styles.chartTitle}>Quick Stats</h3>
          <div className={styles.quickStatsList}>
            <div className={styles.quickStat}><span>Avg Resolution Time</span><span className={styles.blueText}>4.2 min</span></div>
            <div className={styles.quickStat}><span>First Response Rate</span><span className={styles.greenText}>94%</span></div>
            <div className={styles.quickStat}><span>Escalation Rate</span><span className={styles.yellowText}>6%</span></div>
            <div className={styles.quickStat}><span>Agent Utilization</span><span className={styles.purpleText}>87%</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { Dashboard };
