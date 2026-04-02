<template>
  <div class="animate-in fade-in space-y-8 duration-500 text-foreground">
    <header class="page-header">
      <div class="relative z-10">
        <Badge variant="outline" class="badge-outline mb-4 uppercase tracking-widest text-[10px]">
          管理管理
        </Badge>
        <h1 class="page-header-title">创建定检计划</h1>
        <p class="page-header-desc">
          定义新的定检计划，包括名称、周期和类型。
        </p>
      </div>
      <div class="page-header-blur"></div>
    </header>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-8">
        <Card class="border-border bg-card shadow-xl overflow-hidden">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <div class="card-header-accent" />
              <CardTitle class="card-title">计划基本信息</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <el-form :model="form" label-position="top" class="grid grid-cols-1 gap-x-8 gap-y-4 md:grid-cols-2">
              <el-form-item label="计划名称" required class="md:col-span-2">
                <el-input v-model="form.plan_name" placeholder="请输入计划名称" />
              </el-form-item>
              
              <el-form-item label="年度" required>
                <el-date-picker
                  v-model="form.year"
                  type="year"
                  placeholder="选择年度"
                  value-format="YYYY"
                  class="!w-full"
                />
              </el-form-item>
              
              <el-form-item label="月份" required>
                <el-select v-model="form.month" placeholder="选择月份" class="!w-full">
                  <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
                </el-select>
              </el-form-item>

              <el-form-item label="定检类型" required>
                <el-select v-model="form.plan_type" placeholder="选择类型" class="!w-full">
                  <el-option label="常规" value="regular" />
                  <el-option label="年度" value="annual" />
                  <el-option label="专项" value="special" />
                </el-select>
              </el-form-item>

              <el-form-item label="备注" class="md:col-span-2">
                <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="补充说明计划内容" />
              </el-form-item>
            </el-form>
          </CardContent>
        </Card>
      </div>

      <div class="space-y-6">
        <Card class="border-border bg-card shadow-xl sticky top-8">
          <CardHeader class="card-header">
            <div class="card-header-inner">
              <CardTitle class="card-title">操作</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-6 space-y-4">
            <p class="text-sm text-muted-foreground">
              保存计划后可以在列表中继续编辑或发布。发布计划将不可修改，并立即生成定检任务。
            </p>
            <Button class="w-full" :loading="submitting" @click="handleSave('draft')">
              保存为草稿
            </Button>
            <Button variant="outline" class="w-full" :loading="submitting" @click="handleSave('published')">
              立即发布
            </Button>
            <Button variant="ghost" class="w-full" @click="goBack">
              取消返回
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createPlan } from '@/api/inspection'
import { useSessionStore } from '@/store/session'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'

const router = useRouter()
const session = useSessionStore()
const submitting = ref(false)

const form = reactive({
  plan_name: '',
  year: new Date().getFullYear().toString(),
  month: new Date().getMonth() + 1,
  plan_type: 'regular',
  remark: ''
})

async function handleSave(status) {
  if (!form.plan_name || !form.year || !form.month) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (status === 'published') {
    try {
      await ElMessageBox.confirm(
        '确认立即发布该计划吗？发布后将自动生成定检任务，且计划内容不可更改。',
        '发布确认',
        {
          confirmButtonText: '确认发布',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch (err) {
      return
    }
  }

  submitting.value = true
  try {
    const res = await createPlan({
      ...form,
      status,
      org_id: session.orgId,
      created_by: session.userId
    })
    if (res.success) {
      ElMessage.success(status === 'published' ? '计划已发布' : '计划已保存')
      router.push('/inspection/plans')
    }
  } catch (err) {
    console.error('保存计划失败:', err)
    ElMessage.error('保存计划失败')
  } finally {
    submitting.value = false
  }
}

function goBack() {
  router.back()
}
</script>
