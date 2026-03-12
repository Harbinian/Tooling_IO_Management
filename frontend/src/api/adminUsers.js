import client from './client'

/**
 * 获取管理员用户列表
 * @param {Object} params 
 */
export async function getAdminUsers(params = {}) {
  const { data } = await client.get('/admin/users', { params })
  return data.data || []
}

/**
 * 获取用户详情
 * @param {string} userId 
 */
export async function getAdminUserDetail(userId) {
  const { data } = await client.get(`/admin/users/${userId}`)
  return data.data
}

/**
 * 创建后台用户
 * @param {Object} payload 
 */
export async function createAdminUser(payload) {
  const { data } = await client.post('/admin/users', payload)
  return data.data
}

/**
 * 更新用户信息
 * @param {string} userId 
 * @param {Object} payload 
 */
export async function updateAdminUser(userId, payload) {
  const { data } = await client.put(`/admin/users/${userId}`, payload)
  return data.data
}

/**
 * 更新用户角色
 * @param {string} userId 
 * @param {Object} payload 
 */
export async function updateAdminUserRoles(userId, payload) {
  const { data } = await client.put(`/admin/users/${userId}/roles`, payload)
  return data.data
}

/**
 * 更新用户状态
 * @param {string} userId 
 * @param {Object} payload 
 */
export async function updateAdminUserStatus(userId, payload) {
  const { data } = await client.put(`/admin/users/${userId}/status`, payload)
  return data.data
}

/**
 * 重置用户密码
 * @param {string} userId 
 * @param {Object} payload 
 */
export async function resetAdminUserPassword(userId, payload) {
  const { data } = await client.put(`/admin/users/${userId}/password-reset`, payload)
  return data.data
}

/**
 * 获取角色列表
 */
export async function getAdminRoles() {
  const { data } = await client.get('/admin/roles')
  return data.data || []
}
