import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../../ui/Card/Card';
import styles from './MetricsCard.module.css';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  loading?: boolean;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  loading = false
}) => {
  return (
    <Card variant="elevated" hoverable>
      <CardContent>
        <div className={styles.metricsCard}>
          {icon && (
            <div className={styles.iconContainer}>
              {icon}
            </div>
          )}
          
          <div className={styles.content}>
            <div className={styles.header}>
              <h3 className={styles.title}>{title}</h3>
              {trend && (
                <div className={`${styles.trend} ${
                  trend.isPositive ? styles.positive : styles.negative
                }`}>
                  <span className={styles.trendValue}>
                    {trend.isPositive ? '+' : ''}{trend.value}%
                  </span>
                </div>
              )}
            </div>
            
            {loading ? (
              <div className={styles.skeleton}>
                <div className={styles.skeletonValue} />
                {subtitle && <div className={styles.skeletonSubtitle} />}
              </div>
            ) : (
              <>
                <motion.div
                  className={styles.value}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  {value}
                </motion.div>
                {subtitle && (
                  <div className={styles.subtitle}>
                    {subtitle}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
