import React from 'react';
import { motion } from 'framer-motion';
import { 
  ChatBubbleLeftRightIcon,
  ClockIcon,
  StarIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { MetricsCard } from '../MetricsCard/MetricsCard';
import { Card, CardHeader, CardContent } from '../../ui/Card/Card';
import { useAnalytics } from '../../../hooks/useAnalytics';
import styles from './Dashboard.module.css';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042'];

export const Dashboard: React.FC = () => {
  const { data, loading, error } = useAnalytics();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.3
      }
    }
  };

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <h2>Error Loading Analytics</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (loading) return <div className={styles.loading}>Loading...</div>;
  if (!data) return null;

  // Prepare data for mini-charts
  const totalConversationsData = [{ name: 'Total', value: data.totalConversations }];
  const avgResponseTimeData = [{ name: 'Avg', value: parseFloat(data.averageResponseTime) || 0 }];
  const satisfactionValue = parseFloat(data.satisfactionRate);
  const satisfactionData = [
    { name: 'Satisfied', value: isNaN(satisfactionValue) ? 0 : satisfactionValue },
    { name: 'Unsatisfied', value: isNaN(satisfactionValue) ? 100 : 100 - satisfactionValue },
  ];
  const activeUsersData = [{ name: 'Active', value: data.activeUsers }];

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h1 className={styles.title}>Analytics Dashboard</h1>
        <p className={styles.subtitle}>Monitor your customer support performance</p>
      </div>

      <motion.div
        className={styles.metricsGrid}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <div className={styles.metricCard}>
            <h2>Total Conversations</h2>
            <div className={styles.metricValueRow}>
              <span className={styles.metricValue}>{data.totalConversations}</span>
              <ResponsiveContainer width={60} height={40}>
                <BarChart data={totalConversationsData} layout="vertical">
                  <Bar dataKey="value" fill="#8884d8" barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className={styles.metricLabel}>This month</div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className={styles.metricCard}>
            <h2>Avg Response Time</h2>
            <div className={styles.metricValueRow}>
              <span className={styles.metricValue}>{data.averageResponseTime}</span>
              <ResponsiveContainer width={60} height={40}>
                <BarChart data={avgResponseTimeData} layout="vertical">
                  <Bar dataKey="value" fill="#82ca9d" barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className={styles.metricLabel}>Last 7 days</div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className={styles.metricCard}>
            <h2>Customer Satisfaction</h2>
            <div className={styles.metricValueRow}>
              <span className={styles.metricValue}>{data.satisfactionRate}</span>
              <ResponsiveContainer width={60} height={40}>
                <PieChart>
                  <Pie
                    data={satisfactionData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={12}
                    outerRadius={20}
                    startAngle={90}
                    endAngle={-270}
                  >
                    {satisfactionData.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className={styles.metricLabel}>Average rating</div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className={styles.metricCard}>
            <h2>Active Users</h2>
            <div className={styles.metricValueRow}>
              <span className={styles.metricValue}>{data.activeUsers}</span>
              <ResponsiveContainer width={60} height={40}>
                <BarChart data={activeUsersData} layout="vertical">
                  <Bar dataKey="value" fill="#ff8042" barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className={styles.metricLabel}>Currently online</div>
          </div>
        </motion.div>
      </motion.div>

      <motion.div
        className={styles.chartsGrid}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <Card variant="elevated">
            <CardHeader>
              <h3 className={styles.cardTitle}>Conversation Volume</h3>
            </CardHeader>
            <CardContent>
              <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.conversationVolume} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="conversations" fill="#8884d8" name="Conversations" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card variant="elevated">
            <CardHeader>
              <h3 className={styles.cardTitle}>Response Time Trends</h3>
            </CardHeader>
            <CardContent>
              <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.responseTimeTrend} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="responseTime" stroke="#82ca9d" name="Response Time (s)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card variant="elevated">
            <CardHeader>
              <h3 className={styles.cardTitle}>Satisfaction Trends</h3>
            </CardHeader>
            <CardContent>
              <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.satisfactionTrend} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="satisfaction" stroke="#ffc658" name="Satisfaction (%)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
};
