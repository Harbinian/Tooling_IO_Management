import client from './client'

export async function getUsersByRole(roleCode, params = {}) {
  const { data } = await client.get(`/users/by-role/${roleCode}`, { params })
  return data.data || []
}
