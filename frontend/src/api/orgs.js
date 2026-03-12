import client from './client'

/**
 * 获取组织列表
 * @param {boolean} includeDisabled 是否包含已禁用的组织
 */
export async function getOrgList(includeDisabled = true) {
  const { data } = await client.get('/orgs', {
    params: { include_disabled: includeDisabled }
  })
  return data.data
}

/**
 * 获取组织树结构
 * @param {boolean} includeDisabled 是否包含已禁用的组织
 */
export async function getOrgTree(includeDisabled = true) {
  const { data } = await client.get('/orgs/tree', {
    params: { include_disabled: includeDisabled }
  })
  return data.data
}

/**
 * 获取组织详情
 * @param {string} orgId 组织 ID
 */
export async function getOrgDetail(orgId) {
  const { data } = await client.get(`/orgs/${orgId}`)
  return data.data
}
