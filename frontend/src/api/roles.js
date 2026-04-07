import client from './client'

export default {
  getAdminRoles() {
    return client.get('/admin/roles')
  },
  createRole(payload) {
    return client.post('/admin/roles', payload)
  },
  updateRole(roleId, payload) {
    return client.put(`/admin/roles/${roleId}`, payload)
  },
  deleteRole(roleId) {
    return client.delete(`/admin/roles/${roleId}`)
  },
  getRolePermissions(roleId) {
    return client.get(`/admin/roles/${roleId}/permissions`)
  },
  assignPermissions(roleId, payload) {
    return client.put(`/admin/roles/${roleId}/permissions`, payload)
  }
}
