<template>
  <el-dialog
    v-model="visible"
    title="提交定检报告"
    width="600px"
    :close-on-click-modal="false"
    @closed="$emit('close')"
  >
    <el-form :model="form" label-position="top" class="space-y-4">
      <el-form-item label="检验日期" required>
        <el-date-picker
          v-model="form.inspection_date"
          type="date"
          placeholder="选择检验日期"
          value-format="YYYY-MM-DD"
          class="!w-full"
        />
      </el-form-item>

      <el-form-item label="检验结论" required>
        <el-radio-group v-model="form.result">
          <el-radio label="pass">合格</el-radio>
          <el-radio label="fail">不合格</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="测量数据 / 备注">
        <el-input
          v-model="form.data"
          type="textarea"
          :rows="4"
          placeholder="输入关键测量参数或异常说明"
        />
      </el-form-item>

      <el-form-item label="报告附件 (最大 2MB)">
        <el-upload
          class="w-full"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
          :file-list="fileList"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip text-xs text-muted-foreground">
              支持 JPG/PNG/PDF，单个文件不超过 2MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button variant="ghost" @click="visible = false">取消</Button>
        <Button :loading="submitting" @click="handleSubmit">提交报告</Button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { submitReport } from '@/api/inspection'
import Button from '@/components/ui/Button.vue'

const props = defineProps({
  taskNo: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'success'])

const visible = ref(true)
const submitting = ref(false)
const fileList = ref([])

const form = reactive({
  inspection_date: new Date().toISOString().split('T')[0],
  result: 'pass',
  data: '',
  attachment_base64: null,
  attachment_name: ''
})

function handleFileChange(file) {
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('上传附件大小不能超过 2MB!')
    fileList.value = []
    return
  }

  const reader = new FileReader()
  reader.readAsDataURL(file.raw)
  reader.onload = () => {
    form.attachment_base64 = reader.result
    form.attachment_name = file.name
  }
}

async function handleSubmit() {
  if (!form.inspection_date || !form.result) {
    ElMessage.warning('请填写必填项')
    return
  }

  submitting.value = true
  try {
    const res = await submitReport(props.taskNo, form)
    if (res.success) {
      ElMessage.success('报告提交成功')
      emit('success')
    }
  } catch (err) {
    console.error('提交报告失败:', err)
    ElMessage.error('提交报告失败')
  } finally {
    submitting.value = false
  }
}
</script>
