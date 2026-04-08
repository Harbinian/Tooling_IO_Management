import type { ApiResponse } from './response'

export interface DashboardMetrics extends Record<string, unknown> {
  pending_count?: number
  completed_count?: number
  alert_count?: number
}

export interface DashboardMetricsResponse extends ApiResponse<DashboardMetrics> {}
