import client from './client'

function unwrap(response) {
  return response.data
}

export default {
  async getPermissions(params) {
    return unwrap(await client.get('/admin/permissions', { params }))
  },
  async createPermission(payload) {
    return unwrap(await client.post('/admin/permissions', payload))
  },
  async updatePermission(code, payload) {
    return unwrap(await client.put(`/admin/permissions/${code}`, payload))
  },
  async deletePermission(code) {
    return unwrap(await client.delete(`/admin/permissions/${code}`))
  }
}
