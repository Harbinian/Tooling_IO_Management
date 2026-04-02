<template>
  <div class="workflow-stepper">
    <!-- Step Header -->
    <div v-if="showHeader" class="flex items-center justify-between mb-6">
      <div>
        <p v-if="currentStepNumber" class="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">
          步骤 {{ currentStepNumber }} / {{ totalSteps }}
        </p>
        <p class="text-sm font-semibold text-foreground">{{ stepTitle }}</p>
      </div>
      <div v-if="nextRole" class="flex items-center gap-2">
        <span class="text-xs text-muted-foreground">下一步:</span>
        <span class="rounded-full bg-muted px-3 py-1 text-xs font-medium text-foreground">
          {{ nextRole }}
        </span>
      </div>
    </div>

    <!-- Steps -->
    <div class="space-y-3">
      <div
        v-for="(step, index) in computedSteps"
        :key="step.key"
        class="flex items-start gap-4 rounded-2xl border px-4 py-4 transition-all"
        :class="stepClass(step.state)"
      >
        <!-- Step Number / Icon -->
        <div
          class="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold shrink-0"
          :class="stepDotClass(step.state)"
        >
          <Check v-if="step.state === 'complete'" class="h-4 w-4" />
          <span v-else>{{ String(index + 1).padStart(2, '0') }}</span>
        </div>

        <!-- Step Content -->
        <div class="flex-1 space-y-1">
          <div class="flex items-center gap-2">
            <p class="text-sm font-semibold text-foreground">{{ step.label }}</p>
            <span
              v-if="step.state === 'current'"
              class="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-primary"
            >
              当前
            </span>
          </div>
          <p class="text-sm leading-6 text-muted-foreground">{{ step.description }}</p>
        </div>

        <!-- Step Role Badge -->
        <div v-if="step.role" class="shrink-0">
          <span class="rounded-full bg-muted px-2.5 py-1 text-[10px] font-medium text-muted-foreground">
            {{ step.role }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check } from 'lucide-vue-next'

const props = defineProps({
  currentStatus: {
    type: String,
    required: true
  },
  workflowType: {
    type: String,
    default: 'outbound',
    validator: (value) => ['outbound', 'inbound', 'inspection'].includes(value)
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  stepTitle: {
    type: String,
    default: '流程进度'
  },
  customLabels: {
    type: Object,
    default: () => ({})
  }
})

const workflows = {
  outbound: [
    { key: 'draft', label: '草稿', description: '发起人已填写申请', role: '发起人' },
    { key: 'submitted', label: '已提交', description: '进入保管员审核阶段', role: '保管员' },
    { key: 'keeper_confirmed', label: '保管员已确认', description: '审核和数量确认完成', role: '运输员' },
    { key: 'transport_notified', label: '运输通知', description: '运输人员已收到通知', role: '运输员' },
    { key: 'final_confirm_pending', label: '班组长最终确认', description: '等待班组长确认完成', role: '班组长' },
    { key: 'completed', label: '已完成', description: '流程已完成', role: null }
  ],
  inbound: [
    { key: 'draft', label: '草稿', description: '发起人已填写申请', role: '发起人' },
    { key: 'submitted', label: '已提交', description: '进入保管员审核阶段', role: '保管员' },
    { key: 'keeper_confirmed', label: '保管员已确认', description: '审核和数量确认完成', role: '运输员' },
    { key: 'transport_notified', label: '运输通知', description: '运输人员已收到通知', role: '运输员' },
    { key: 'final_confirm_pending', label: '保管员最终确认', description: '等待保管员确认完成', role: '保管员' },
    { key: 'completed', label: '已完成', description: '流程已完成', role: null }
  ],
  inspection: [
    { key: 'pending', label: '待定检', description: '任务已生成，等待开始', role: '定检员' },
    { key: 'received', label: '已接收', description: '定检员已接收任务', role: '定检员' },
    { key: 'outbound_created', label: '出库申请已创建', description: '定检所需工装已发起出库', role: '发起人' },
    { key: 'outbound_completed', label: '出库已完成', description: '工装已到达定检区', role: '定检员' },
    { key: 'in_progress', label: '定检中', description: '正在执行定检作业', role: '定检员' },
    { key: 'report_submitted', label: '报告已提交', description: '定检报告已上传等待审核', role: '审核员' },
    { key: 'accepted', label: '审核通过', description: '定检结论已确认', role: '发起人' },
    { key: 'inbound_created', label: '入库申请已创建', description: '工装定检后发起回库', role: '发起人' },
    { key: 'inbound_completed', label: '入库已完成', description: '工装已归还库房', role: '保管员' },
    { key: 'closed', label: '已关闭', description: '任务全流程结束', role: null }
  ]
}

const computedSteps = computed(() => {
  const steps = workflows[props.workflowType] || workflows.outbound
  const currentIndex = steps.findIndex(s => s.key === props.currentStatus)
  
  return steps.map((step, index) => {
    let state = 'pending'
    if (index < currentIndex) state = 'complete'
    else if (index === currentIndex) state = 'current'
    
    return {
      ...step,
      state,
      label: props.customLabels[step.key]?.label || step.label,
      description: props.customLabels[step.key]?.description || step.description
    }
  })
})

const currentStepNumber = computed(() => {
  const index = computedSteps.value.findIndex(s => s.state === 'current')
  return index !== -1 ? index + 1 : null
})

const totalSteps = computed(() => computedSteps.value.length)

const nextRole = computed(() => {
  const currentStep = computedSteps.value.find(s => s.state === 'current')
  return currentStep?.role || null
})

function stepClass(state) {
  switch (state) {
    case 'complete': return 'border-primary/20 bg-primary/5 opacity-80'
    case 'current': return 'border-primary bg-card shadow-lg shadow-primary/10'
    default: return 'border-border bg-muted/20 grayscale opacity-60'
  }
}

function stepDotClass(state) {
  switch (state) {
    case 'complete': return 'bg-primary text-primary-foreground'
    case 'current': return 'bg-primary text-primary-foreground animate-pulse'
    default: return 'bg-muted text-muted-foreground'
  }
}
</script>
