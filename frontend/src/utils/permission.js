import { useSessionStore } from '@/store/session'

/**
 * Check if the current user has a specific permission.
 * @param {string} permission 
 * @returns {boolean}
 */
export function hasPermission(permission) {
  const session = useSessionStore()
  return session.hasPermission(permission)
}

/**
 * Check if the current user has any of the listed permissions.
 * @param {string[]} permissions 
 * @returns {boolean}
 */
export function hasAnyPermission(permissions) {
  if (!Array.isArray(permissions)) return false
  const session = useSessionStore()
  return permissions.some(p => session.hasPermission(p))
}

/**
 * Check if the current user has all of the listed permissions.
 * @param {string[]} permissions 
 * @returns {boolean}
 */
export function hasAllPermissions(permissions) {
  if (!Array.isArray(permissions)) return false
  const session = useSessionStore()
  return permissions.every(p => session.hasPermission(p))
}
