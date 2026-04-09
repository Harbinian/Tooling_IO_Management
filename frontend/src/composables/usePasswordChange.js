/**
 * usePasswordChange - Composable for password change functionality.
 *
 * This composable handles:
 * - Password validation (length, complexity)
 * - Password change submission
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'

export function usePasswordChange() {
  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const passwordLoading = ref(false)

  function validatePassword(password) {
    if (password.length < 8) {
      return { valid: false, message: '新密码长度至少为 8 位' }
    }
    const hasUpper = /[A-Z]/.test(password)
    const hasLower = /[a-z]/.test(password)
    const hasDigit = /\d/.test(password)
    if (!(hasUpper && hasLower && hasDigit)) {
      return { valid: false, message: '新密码必须包含大小写字母和数字' }
    }
    return { valid: true }
  }

  async function handlePasswordChange() {
    if (!passwordForm.value.oldPassword) {
      ElMessage.warning('请输入当前密码')
      return { success: false }
    }

    const validation = validatePassword(passwordForm.value.newPassword)
    if (!validation.valid) {
      ElMessage.warning(validation.message)
      return { success: false }
    }

    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      ElMessage.warning('两次输入的新密码不一致')
      return { success: false }
    }

    passwordLoading.value = true
    try {
      await changePassword({
        old_password: passwordForm.value.oldPassword,
        new_password: passwordForm.value.newPassword
      })
      ElMessage.success('密码修改成功')
      passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
      return { success: true }
    } catch (error) {
      ElMessage.error(error.message || '密码修改失败')
      return { success: false, error }
    } finally {
      passwordLoading.value = false
    }
  }

  return {
    passwordForm,
    passwordLoading,
    handlePasswordChange,
    validatePassword
  }
}
