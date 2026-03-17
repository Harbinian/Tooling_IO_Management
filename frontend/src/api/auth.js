import client from './client'

/**
 * 用户登录
 * @param {Object} credentials { login_name, password }
 */
export async function login(credentials) {
  const { data } = await client.post('/auth/login', credentials)
  return data
}

/**
 * 获取当前登录用户信息
 */
export async function getCurrentUser() {
  const { data } = await client.get('/auth/me')
  return data.user
}

/**
 * Change password for the current authenticated user.
 * @param {Object} payload { old_password, new_password }
 */
export async function changePassword(payload) {
  const { data } = await client.post('/user/change-password', payload)
  return data
}
