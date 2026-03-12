import client from './client'

/**
 * 获取仪表盘汇总数据
 */
export async function getDashboardMetrics() {
  const { data } = await client.get('/dashboard/metrics')
  return data
}
