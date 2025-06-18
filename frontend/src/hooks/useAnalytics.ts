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

export const useAnalytics = (
  dateRange: number = 7,
  intent: string = '',
  difficulty: string = '',
  agent: string = '',
  customStartDate: string = '',
  customEndDate: string = ''
) => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topIntents, setTopIntents] = useState<any[]>([]);
  const [hardestQuestions, setHardestQuestions] = useState<any[]>([]);
  const [mostSuccessful, setMostSuccessful] = useState<any[]>([]);
  const [leastSuccessful, setLeastSuccessful] = useState<any[]>([]);

  const buildQuery = () => {
    const params = [];
    if (dateRange && dateRange > 0) params.push(`days=${dateRange}`);
    if (dateRange === -1 && customStartDate) params.push(`start_date=${customStartDate}`);
    if (dateRange === -1 && customEndDate) params.push(`end_date=${customEndDate}`);
    if (intent) params.push(`intent=${encodeURIComponent(intent)}`);
    if (difficulty) params.push(`difficulty=${encodeURIComponent(difficulty)}`);
    if (agent) params.push(`agent=${encodeURIComponent(agent)}`);
    return params.length ? `?${params.join('&')}` : '';
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const query = buildQuery();
      // Fetch all analytics endpoints in parallel
      const [overviewRes, topIntentsRes, hardestRes, mostRes, leastRes] = await Promise.all([
        fetch(`/api/v1/analytics/overview${query}`),
        fetch(`/api/v1/analytics/top-intents${query}`),
        fetch(`/api/v1/analytics/hardest-questions${query}`),
        fetch(`/api/v1/analytics/most-successful${query}`),
        fetch(`/api/v1/analytics/least-successful${query}`),
      ]);
      if (!overviewRes.ok) throw new Error('Failed to fetch analytics overview');
      const analyticsData = await overviewRes.json();
      setData(analyticsData);
      setTopIntents(topIntentsRes.ok ? await topIntentsRes.json() : []);
      setHardestQuestions(hardestRes.ok ? await hardestRes.json() : []);
      setMostSuccessful(mostRes.ok ? await mostRes.json() : []);
      setLeastSuccessful(leastRes.ok ? await leastRes.json() : []);
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
  }, [dateRange, intent, difficulty, agent, customStartDate, customEndDate]);

  return {
    data,
    loading,
    error,
    refresh: fetchAnalytics,
    topIntents,
    hardestQuestions,
    mostSuccessful,
    leastSuccessful,
  };
}; 