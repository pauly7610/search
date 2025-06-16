import { useState, useEffect } from 'react'

interface AnalyticsData {
  totalConversations: number;
  averageResponseTime: string;
  satisfactionRate: string;
  activeUsers: number;
  conversationVolume: Array<{
    date: string;
    conversations: number;
  }>;
  responseTimeTrend: Array<{
    date: string;
    responseTime: number;
  }>;
  satisfactionTrend: Array<{
    date: string;
    satisfaction: number;
  }>;
  intentDistribution: Record<string, number>;
}

export const useAnalytics = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/v1/analytics/overview');
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      
      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    // Refresh data every 5 minutes
    const interval = setInterval(fetchAnalytics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return {
    data,
    loading,
    error,
    refresh: fetchAnalytics
  };
}; 