<template>
  <el-dialog
    v-model="visible"
    title="上报运输异常"
    width="500px"
    destroy-on-close
    class="custom-dialog"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="mt-4"
    >
      <el-form-item label="异常类型" prop="issue_type">
        <el-select v-model="form.issue_type" placeholder="请选择异常类型" class="w-full">
          <el-option label="工装损坏" value="工装损坏" />
          <el-option label="数量不符" value="数量不符" />
          <el-option label="位置错误" value="位置错误" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>

      <el-form-item label="异常描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请详细描述发现的异常情况（最少10字符）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="图片上传 (可选，最多3张)">
        <el-upload
          v-model:file-list="fileList"
          action="#"
          list-type="picture-card"
          :auto-upload="false"
          :limit="3"
          :on-exceed="handleExceed"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button variant="outline" @click="visible = false">取消</Button>
        <Button 
          variant="default" 
          class="bg-amber-500 hover:bg-amber-400 text-white border-none"
          :loading="submitting"
          @click="submitForm"
        >
          提交异常
        </Button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { reportTransportIssue } from '@/api/orders'
import Button from '@/components/ui/Button.vue'
import { useSessionStore } from '@/store/session'

const props = defineProps({
  modelValue: Boolean,
  orderNo: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const session = useSessionStore()
const visible = ref(props.modelValue)
const formRef = ref(null)
const submitting = ref(false)
const fileList = ref([])

const form = reactive({
  issue_type: '',
  description: ''
})

const rules = {
  issue_type: [{ required: true, message: '请选择异常类型', trigger: 'change' }],
  description: [
    { required: true, message: '请输入异常描述', trigger: 'blur' },
    { min: 10, message: '描述最少需要10个字符', trigger: 'blur' }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    resetForm()
  }
})

function resetForm() {
  form.issue_type = ''
  form.description = ''
  fileList.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

function handleExceed() {
  ElMessage.warning('最多只能上传3张图片')
}

async function submitForm() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await ElMessageBox.confirm(
        '确定要提交此运输异常吗？',
        '提交确认',
        {
          confirmButtonText: '确定提交',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      submitting.value = true
      
      const payload = {
        issue_type: form.issue_type,
        description: form.description,
        reporter_id: session.userId,
        reporter_name: session.userName,
        operator_id: session.userId,
        operator_name: session.userName,
        operator_role: session.role
      }

      // Note: Image upload is optional and logic for processing base64 or multipart 
      // would go here if backend supports it. For now we send the text fields.
      
      const result = await reportTransportIssue(props.orderNo, payload)
      
      if (result.success) {
        ElMessage.success('异常上报成功')
        emit('success')
        visible.value = false
      } else {
        ElMessage.error(result.error || '上报失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Report issue error:', error)
        ElMessage.error('操作异常')
      }
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
:deep(.custom-dialog) {
  border-radius: 1rem;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  margin-right: 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

:deep(.el-dialog__body) {
  padding-top: 1rem;
}
</style>
