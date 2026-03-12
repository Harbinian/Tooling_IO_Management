import { useSessionStore } from '@/store/session'

/**
 * v-debug-id directive
 *
 * Usage: <div v-debug-id="DEBUG_IDS.DASHBOARD.SUMMARY_CARD">...</div>
 *
 * Only active for Administrators when ?debugUI=1 or ?debugUI=pin is present.
 */

const BADGE_ATTR = 'data-debug-id-badge'
const OUTLINE_ATTR = 'data-debug-id-outline'
const CLICK_ATTR = 'data-debug-id-click'

function getDebugMode() {
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('debugUI') || sessionStorage.getItem('debugUI') || ''
}

function isAdministrator(session) {
  const roles = session.roles || []
  const roleMatch = roles.some((role) => {
    const code = String(role.role_code || '').toLowerCase()
    const name = String(role.role_name || '').toLowerCase()
    return (
      ['sys_admin', 'admin', 'administrator'].includes(code) ||
      ['system administrator', 'administrator'].includes(name)
    )
  })

  if (roleMatch) {
    return true
  }

  if (typeof session.hasPermission === 'function' && session.hasPermission('admin:user_manage')) {
    return true
  }

  return ['admin', 'sys_admin'].includes(String(session.role || '').toLowerCase())
}

function ensureRelativePosition(el) {
  const current = window.getComputedStyle(el).position
  if (current === 'static') {
    el.style.position = 'relative'
  }
}

function cleanup(el) {
  const target = el.__debugTargetEl || el
  const badge = target.querySelector(`[${BADGE_ATTR}="true"]`)
  if (badge) {
    badge.remove()
  }

  if (el.__debugMouseEnter) {
    el.removeEventListener('mouseenter', el.__debugMouseEnter)
    el.__debugMouseEnter = null
  }
  if (el.__debugMouseLeave) {
    el.removeEventListener('mouseleave', el.__debugMouseLeave)
    el.__debugMouseLeave = null
  }
  if (el.__debugClick) {
    el.removeEventListener('click', el.__debugClick, true)
    el.__debugClick = null
  }

  if (el.getAttribute(OUTLINE_ATTR) === 'true') {
    el.style.outline = ''
    el.removeAttribute(OUTLINE_ATTR)
  }

  el.__debugTargetEl = null
}

function syncDebugBadge(el, binding) {
  cleanup(el)

  const debugId = binding.value
  if (!debugId) {
    return
  }

  const debugMode = getDebugMode()
  if (!debugMode) {
    return
  }

  const session = useSessionStore()
  if (!session.initialized || !isAdministrator(session)) {
    return
  }

  const isPinMode = debugMode === 'pin'
  const badge = document.createElement('div')
  badge.setAttribute(BADGE_ATTR, 'true')
  badge.innerText = debugId

  Object.assign(badge.style, {
    position: 'absolute',
    top: '0',
    right: '0',
    backgroundColor: '#ef4444',
    color: 'white',
    fontSize: '10px',
    padding: '1px 4px',
    borderRadius: '0 0 0 4px',
    zIndex: '10000',
    pointerEvents: 'auto',
    fontFamily: 'monospace',
    boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
    whiteSpace: 'nowrap',
    opacity: isPinMode ? '1' : '0',
    transition: 'opacity 0.2s ease-in-out',
    cursor: 'copy'
  })

  const voidElements = ['INPUT', 'IMG', 'BR', 'HR', 'SELECT', 'TEXTAREA']
  const isVoid = voidElements.includes(el.tagName)
  const targetEl = isVoid ? el.parentElement : el
  if (!targetEl) {
    return
  }

  if (isVoid) {
    ensureRelativePosition(targetEl)
    badge.style.top = `${el.offsetTop}px`
    const parentWidth = targetEl.offsetWidth
    const elRight = el.offsetLeft + el.offsetWidth
    badge.style.right = `${Math.max(parentWidth - elRight, 0)}px`
  } else {
    ensureRelativePosition(el)
  }

  targetEl.appendChild(badge)
  el.__debugTargetEl = targetEl

  const reveal = () => {
    badge.style.opacity = '1'
    el.style.outline = '1px dashed #ef4444'
    el.setAttribute(OUTLINE_ATTR, 'true')
  }
  const hide = () => {
    badge.style.opacity = '0'
    el.style.outline = ''
    el.removeAttribute(OUTLINE_ATTR)
  }

  if (!isPinMode) {
    el.__debugMouseEnter = reveal
    el.__debugMouseLeave = hide
    el.addEventListener('mouseenter', el.__debugMouseEnter)
    el.addEventListener('mouseleave', el.__debugMouseLeave)
  } else {
    reveal()
  }

  const handleCopy = () => {
    const debugInfo = {
      Page: document.title || window.location.pathname,
      Route: window.location.pathname,
      Role: session.roleName || 'Administrator',
      DebugID: debugId,
      Element: el.innerText ? el.innerText.substring(0, 50).replace(/\s+/g, ' ').trim() : 'Unknown Element'
    }

    const copyText = `Page: ${debugInfo.Page}\nRoute: ${debugInfo.Route}\nRole: ${debugInfo.Role}\nDebugID: ${debugInfo.DebugID}\nElement: ${debugInfo.Element}`

    navigator.clipboard.writeText(copyText).then(() => {
      const originalBg = badge.style.backgroundColor
      const originalText = badge.innerText
      badge.style.backgroundColor = '#10b981'
      badge.innerText = 'COPIED!'
      setTimeout(() => {
        badge.style.backgroundColor = originalBg
        badge.innerText = originalText
      }, 1000)
    }).catch((err) => {
      console.error('Failed to copy debug info:', err)
    })
  }

  badge.addEventListener('click', (e) => {
    e.stopPropagation()
    handleCopy()
  })

  el.__debugClick = (e) => {
    if (e.altKey) {
      e.preventDefault()
      e.stopPropagation()
      handleCopy()
    }
  }
  el.addEventListener('click', el.__debugClick, true)
}

export default {
  mounted(el, binding) {
    syncDebugBadge(el, binding)
  },
  updated(el, binding) {
    syncDebugBadge(el, binding)
  },
  unmounted(el) {
    cleanup(el)
  }
}
