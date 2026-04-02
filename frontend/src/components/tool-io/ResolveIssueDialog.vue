<template>
  <el-dialog
    v-model="visible"
    title="处理运输异常"
    width="400px"
    destroy-on-close
    class="custom-dialog"
  >
    <div v-if="issue" class="mb-6 p-4 rounded-xl bg-muted/30 border border-border/50">
      <div class="flex items-center gap-2 mb-2">
        <el-tag size="small" type="warning">{{ issue.issue_type }}</el-tag>
        <span class="text-xs text-muted-foreground">{{ issue.reporter_name }} · {{ issue.report_time }}</span>
      </div>
      <p class="text-sm text-foreground/80 line-clamp-3">{{ issue.description }}</p>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
    >
      <el-form-item label="处理回复" prop="resolution">
        <el-input
          v-model="form.resolution"
          type="textarea"
          :rows="4"
          placeholder="请输入处理意见或回复内容..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button variant="outline" @click="visible = false">取消</Button>
        <Button 
          variant="default" 
          class="bg-primary hover:bg-primary/90 text-primary-foreground border-none"
          :loading="submitting"
          @click="submitForm"
        >
          确认处理
        </Button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { resolveTransportIssue } from '@/api/orders'
import Button from '@/components/ui/Button.vue'
import { useSessionStore } from '@/store/session'

const props = defineProps({
  modelValue: Boolean,
  orderNo: {
    type: String,
    required: true
  },
  issue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const session = useSessionStore()
const visible = ref(props.modelValue)
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  resolution: ''
})

const rules = {
  resolution: [
    { required: true, message: '请输入处理回复', trigger: 'blur' },
    { max: 500, message: '回复内容最多500个字符', trigger: 'blur' }
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
  form.resolution = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

async function submitForm() {
  if (!formRef.value || !props.issue) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await ElMessageBox.confirm(
        '确定要完成此异常的处理吗？',
        '处理确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )

      submitting.value = true
      
      const payload = {
        resolution: form.resolution,
        resolver_id: session.userId,
        resolver_name: session.userName,
        operator_id: session.userId,
        operator_name: session.userName,
        operator_role: session.role
      }

      const result = await resolveTransportIssue(props.orderNo, props.issue.id, payload)
      
      if (result.success) {
        ElMessage.success('异常处理完成')
        emit('success')
        visible.value = false
      } else {
        ElMessage.error(result.error || '处理失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Resolve issue error:', error)
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
