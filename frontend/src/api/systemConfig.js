import client from './client'

function unwrap(response) {
  return response.data
}

export async function getSystemConfigs() {
  return unwrap(await client.get('/admin/system-config'))
}

export async function getSystemConfig(configKey) {
  return unwrap(await client.get(`/admin/system-config/${encodeURIComponent(configKey)}`))
}

export async function updateSystemConfig(configKey, payload) {
  return unwrap(await client.put(`/admin/system-config/${encodeURIComponent(configKey)}`, payload))
}
