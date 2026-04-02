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

// Feature flag endpoints
export async function getFeatureFlags() {
  return unwrap(await client.get('/admin/feature-flags'))
}

export async function updateFeatureFlag(flagKey, value) {
  return unwrap(await client.put(`/admin/feature-flags/${encodeURIComponent(flagKey)}`, { value }))
}
