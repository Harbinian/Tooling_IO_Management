import client from './client'

export default {
  getPermissions(params) {
    return client.get('/admin/permissions', { params })
  },
  createPermission(payload) {
    return client.post('/admin/permissions', payload)
  },
  updatePermission(code, payload) {
    return client.put(`/admin/permissions/${code}`, payload)
  },
  deletePermission(code) {
    return client.delete(`/admin/permissions/${code}`)
  }
}
