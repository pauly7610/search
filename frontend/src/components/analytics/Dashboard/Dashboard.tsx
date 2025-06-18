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
  Cell,
  BarChart,
  Bar
} from 'recharts';
import styles from './Dashboard.module.css';
import { useAnalytics } from '../../../hooks/useAnalytics';

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

const dateRanges = [
  { label: 'Last 7 days', value: 7 },
  { label: 'Last 30 days', value: 30 },
  { label: 'All time', value: 0 },
];

const Dashboard: React.FC = () => {
  const [selectedDateRange, setSelectedDateRange] = useState<number>(7);
  const [customStartDate, setCustomStartDate] = useState<string>('');
  const [customEndDate, setCustomEndDate] = useState<string>('');
  const [selectedIntent, setSelectedIntent] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [drilldownIntent, setDrilldownIntent] = useState<string | null>(null);
  const { data: dashboardData, loading: isLoading, error, topIntents, hardestQuestions, mostSuccessful, leastSuccessful, refresh } = useAnalytics(selectedDateRange, selectedIntent, selectedDifficulty, selectedAgent, customStartDate, customEndDate);

  // Unique intents for filter dropdown
  const intentOptions = Object.keys(topIntents || {}).map(intent => ({ label: intent, value: intent }));
  // Difficulty options (static for now, could be dynamic)
  const difficultyOptions = [
    { label: 'All', value: '' },
    { label: 'Beginner', value: 'beginner' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Advanced', value: 'advanced' },
  ];
  // Agent options (static for now, could be dynamic)
  const agentOptions = [
    { label: 'All', value: '' },
    { label: 'Tech Support', value: 'tech_support' },
    { label: 'Billing', value: 'billing' },
    { label: 'General', value: 'general' },
  ];

  // Filtered lists for drilldown
  const filterByIntent = (list: any[]) => drilldownIntent ? list.filter(item => item.intent === drilldownIntent) : list;

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingText}>Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.errorText}>Error loading dashboard data: {error}</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.errorText}>No dashboard data available</div>
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

      {/* Filtering Controls */}
      <div className={styles.filterBar}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Date Range:</label>
          <select
            className={styles.filterSelect}
            value={selectedDateRange}
            onChange={e => setSelectedDateRange(Number(e.target.value))}
          >
            {dateRanges.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
            <option value={-1}>Custom</option>
          </select>
        </div>
        {selectedDateRange === -1 && (
          <div className={styles.filterGroup}>
            <label className={styles.filterLabel}>From:</label>
            <input
              type="date"
              className={styles.filterSelect}
              value={customStartDate}
              onChange={e => setCustomStartDate(e.target.value)}
            />
            <label className={styles.filterLabel}>To:</label>
            <input
              type="date"
              className={styles.filterSelect}
              value={customEndDate}
              onChange={e => setCustomEndDate(e.target.value)}
            />
          </div>
        )}
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Intent:</label>
          <select
            className={styles.filterSelect}
            value={selectedIntent}
            onChange={e => setSelectedIntent(e.target.value)}
          >
            <option value="">All</option>
            {intentOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Difficulty:</label>
          <select
            className={styles.filterSelect}
            value={selectedDifficulty}
            onChange={e => setSelectedDifficulty(e.target.value)}
          >
            {difficultyOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Agent:</label>
          <select
            className={styles.filterSelect}
            value={selectedAgent}
            onChange={e => setSelectedAgent(e.target.value)}
          >
            {agentOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <button className={styles.filterButton} onClick={() => refresh()}>Refresh</button>
      </div>

      {/* Main Grid Layout */}
      <div className={styles.metricsGrid}>
        {/* Total Conversations Card */}
        <div className={styles.metricCard + ' ' + styles.blueCard}>
          <h3 className={styles.metricTitle}>Total Conversations</h3>
          <div className={styles.metricValueHero}>{dashboardData.totalConversations?.toLocaleString?.() ?? dashboardData.totalConversations}</div>
          <p className={styles.metricLabel}>This month</p>
        </div>
        {/* Average Response Time Card */}
        <div className={styles.metricCard + ' ' + styles.greenCard}>
          <h3 className={styles.metricTitle}>Avg Response Time</h3>
          <div className={styles.metricValueHero}>{dashboardData.averageResponseTime}</div>
          <p className={styles.metricLabel}>Last 7 days</p>
        </div>
        {/* Customer Satisfaction Card */}
        <div className={styles.metricCard + ' ' + styles.purpleCard}>
          <h3 className={styles.metricTitle}>Customer Satisfaction</h3>
          <div className={styles.metricValueHero}>{dashboardData.satisfactionRate}</div>
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
            <AreaChart data={dashboardData.responseTimeTrend}>
              <defs>
                <linearGradient id="responseGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-system-border)" />
              <XAxis dataKey="date" stroke="var(--color-system-foreground-tertiary)" fontSize={12} />
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
              data={[{ name: 'Satisfaction', value: parseFloat(dashboardData.satisfactionRate), fill: '#8B5CF6' }]}
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
                {dashboardData.satisfactionRate}
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
              <XAxis dataKey="date" stroke="var(--color-system-foreground-tertiary)" fontSize={12} />
              <YAxis stroke="var(--color-system-foreground-tertiary)" fontSize={12} domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
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
        {/* Quick Stats (placeholder, can be replaced with new metrics) */}
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

      {/* Placeholders for new granular analytics (to be implemented next) */}
      <div className={styles.metricsRow}>
        {/* Top Intents Bar Chart */}
        <div className={styles.metricsRowChart}>
          <h3 className={styles.chartTitle}>Top Intents</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={Object.entries(topIntents).map(([intent, count]) => ({ intent, count }))}
              layout="vertical"
              margin={{ left: 20, right: 20, top: 10, bottom: 10 }}
              onClick={e => {
                if (e && e.activeLabel) setDrilldownIntent(e.activeLabel);
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-system-border)" />
              <XAxis type="number" stroke="var(--color-system-foreground-tertiary)" fontSize={12} allowDecimals={false} />
              <YAxis dataKey="intent" type="category" stroke="var(--color-system-foreground-tertiary)" fontSize={12} width={100} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#6366F1" barSize={18} radius={[8, 8, 8, 8]} />
            </BarChart>
          </ResponsiveContainer>
          {drilldownIntent && (
            <div className={styles.drilldownModal}>
              <div className={styles.drilldownHeader}>
                <span>Drilldown for intent: <b>{drilldownIntent}</b></span>
                <button className={styles.closeButton} onClick={() => setDrilldownIntent(null)}>×</button>
              </div>
              <div className={styles.drilldownContent}>
                <h4>Hardest Questions</h4>
                <div className={styles.analyticsList}>
                  {filterByIntent(hardestQuestions).map((item, idx) => (
                    <div key={idx} className={styles.analyticsListItem}>
                      <div className={styles.analyticsListContent}>{item.content}</div>
                      <div className={styles.analyticsListScore + ' ' + styles.negative}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
                    </div>
                  ))}
                </div>
                <h4>Most Successful</h4>
                <div className={styles.analyticsList}>
                  {filterByIntent(mostSuccessful).map((item, idx) => (
                    <div key={idx} className={styles.analyticsListItem}>
                      <div className={styles.analyticsListContent}>{item.content}</div>
                      <div className={styles.analyticsListScore + ' ' + styles.positive}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
                    </div>
                  ))}
                </div>
                <h4>Least Successful</h4>
                <div className={styles.analyticsList}>
                  {filterByIntent(leastSuccessful).map((item, idx) => (
                    <div key={idx} className={styles.analyticsListItem}>
                      <div className={styles.analyticsListContent}>{item.content}</div>
                      <div className={styles.analyticsListScore + ' ' + styles.negative}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        {/* Hardest Questions List */}
        <div className={styles.metricsRowChart}>
          <h3 className={styles.chartTitle}>Hardest Questions</h3>
          <div className={styles.analyticsList}>
            {hardestQuestions && hardestQuestions.length > 0 ? hardestQuestions.map((item, idx) => (
              <div key={idx} className={styles.analyticsListItem}>
                <div className={styles.analyticsListIntent}>{item.intent || 'Unknown'}</div>
                <div className={styles.analyticsListContent}>{item.content}</div>
                <div className={styles.analyticsListScore + ' ' + styles.negative}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
              </div>
            )) : <div className={styles.analyticsListEmpty}>No data</div>}
          </div>
        </div>
        {/* Most Successful List */}
        <div className={styles.metricsRowChart}>
          <h3 className={styles.chartTitle}>Most Successful</h3>
          <div className={styles.analyticsList}>
            {mostSuccessful && mostSuccessful.length > 0 ? mostSuccessful.map((item, idx) => (
              <div key={idx} className={styles.analyticsListItem}>
                <div className={styles.analyticsListIntent}>{item.intent || 'Unknown'}</div>
                <div className={styles.analyticsListContent}>{item.content}</div>
                <div className={styles.analyticsListScore + ' ' + styles.positive}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
              </div>
            )) : <div className={styles.analyticsListEmpty}>No data</div>}
          </div>
        </div>
        {/* Least Successful List */}
        <div className={styles.metricsRowChart}>
          <h3 className={styles.chartTitle}>Least Successful</h3>
          <div className={styles.analyticsList}>
            {leastSuccessful && leastSuccessful.length > 0 ? leastSuccessful.map((item, idx) => (
              <div key={idx} className={styles.analyticsListItem}>
                <div className={styles.analyticsListIntent}>{item.intent || 'Unknown'}</div>
                <div className={styles.analyticsListContent}>{item.content}</div>
                <div className={styles.analyticsListScore + ' ' + styles.negative}>{item.avg_rating !== null ? item.avg_rating.toFixed(2) : 'N/A'}</div>
              </div>
            )) : <div className={styles.analyticsListEmpty}>No data</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

export { Dashboard };
