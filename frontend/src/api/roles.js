import client from './client'

function unwrap(response) {
  return response.data
}

export default {
  async getAdminRoles() {
    return unwrap(await client.get('/admin/roles'))
  },
  async createRole(payload) {
    return unwrap(await client.post('/admin/roles', payload))
  },
  async updateRole(roleId, payload) {
    return unwrap(await client.put(`/admin/roles/${roleId}`, payload))
  },
  async deleteRole(roleId) {
    return unwrap(await client.delete(`/admin/roles/${roleId}`))
  },
  async getRolePermissions(roleId) {
    return unwrap(await client.get(`/admin/roles/${roleId}/permissions`))
  },
  async assignPermissions(roleId, payload) {
    return unwrap(await client.put(`/admin/roles/${roleId}/permissions`, payload))
  }
}
