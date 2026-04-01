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

    <!-- Navigation (Optional) -->
    <div v-if="showNavigation" class="mt-6 flex items-center justify-between border-t border-border pt-4">
      <button
        v-if="previousLabel"
        class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        @click="$emit('previous')"
      >
        <ChevronLeft class="h-4 w-4" />
        {{ previousLabel }}
      </button>
      <div v-else></div>
      <button
        v-if="nextLabel"
        class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        @click="$emit('next')"
      >
        {{ nextLabel }}
        <ChevronRight class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  /**
   * Current active status (e.g., 'draft', 'submitted', 'keeper_confirmed')
   */
  currentStatus: {
    type: String,
    required: true
  },

  /**
   * Order type: 'outbound' or 'inbound'
   */
  orderType: {
    type: String,
    default: 'outbound'
  },

  /**
   * Whether to show the header with step number and next role
   */
  showHeader: {
    type: Boolean,
    default: true
  },

  /**
   * Whether to show navigation buttons
   */
  showNavigation: {
    type: Boolean,
    default: false
  },

  /**
   * Custom step title
   */
  stepTitle: {
    type: String,
    default: '流程进度'
  },

  /**
   * Custom labels for steps based on status
   * Format: { status: { stepKey: { label, description } } }
   * Example: { 'partially_confirmed': { 'keeper_confirmed': { label: '部分确认', description: '...' } } }
   */
  customLabels: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['previous', 'next'])

// Workflow definition
const workflowOrder = ['draft', 'submitted', 'keeper_confirmed', 'transport_in_progress', 'transport_completed', 'completed']

const workflowStepsDef = computed(() => ({
  outbound: [
    {
      key: 'draft',
      label: '草稿',
      description: '发起人已填写申请，但还未正式提交流程。',
      role: '发起人'
    },
    {
      key: 'submitted',
      label: '已提交',
      description: '单据已进入保管员审核阶段。',
      role: '保管员'
    },
    {
      key: 'keeper_confirmed',
      label: '保管员已确认',
      description: '保管员审核和数量确认已完成。',
      role: '运输员'
    },
    {
      key: 'transport_in_progress',
      label: '运输中',
      description: '工装正在由运输人员执行转运。',
      role: '运输员'
    },
    {
      key: 'transport_completed',
      label: '运输已完成',
      description: '实物转运已结束，单据可以进入最终确认。',
      role: '班组长'
    },
    {
      key: 'completed',
      label: '已完成',
      description: '流程已到达最终完成状态。',
      role: null
    }
  ],
  inbound: [
    {
      key: 'draft',
      label: '草稿',
      description: '发起人已填写申请，但还未正式提交流程。',
      role: '发起人'
    },
    {
      key: 'submitted',
      label: '已提交',
      description: '单据已进入保管员审核阶段。',
      role: '保管员'
    },
    {
      key: 'keeper_confirmed',
      label: '保管员已确认',
      description: '保管员审核和数量确认已完成。',
      role: '运输员'
    },
    {
      key: 'transport_in_progress',
      label: '运输中',
      description: '工装正在由运输人员执行转运。',
      role: '运输员'
    },
    {
      key: 'transport_completed',
      label: '运输已完成',
      description: '实物转运已结束，单据可以进入最终确认。',
      role: '保管员'
    },
    {
      key: 'completed',
      label: '已完成',
      description: '流程已到达最终完成状态。',
      role: null
    }
  ]
}))

const computedSteps = computed(() => {
  const steps = workflowStepsDef.value[props.orderType] || workflowStepsDef.value.outbound
  const activeStatus = props.currentStatus
  const activeIndex = workflowOrder.indexOf(activeStatus)
  const statusCustomLabels = props.customLabels[activeStatus] || {}

  return steps.map((step, index) => {
    const customLabel = statusCustomLabels[step.key]
    return {
      ...step,
      label: customLabel?.label || step.label,
      description: customLabel?.description || step.description,
      state: getStepState(index, activeIndex, activeStatus)
    }
  })
})

const currentStepNumber = computed(() => {
  const activeIndex = workflowOrder.indexOf(props.currentStatus)
  if (activeIndex === -1) return null
  // Map workflow order to step numbers (1-6)
  return activeIndex + 1
})

const totalSteps = computed(() => {
  return 6 // Always 6 steps in the workflow
})

const nextRole = computed(() => {
  const activeIndex = workflowOrder.indexOf(props.currentStatus)
  if (activeIndex === -1 || activeIndex >= 5) return null

  const steps = workflowStepsDef.value[props.orderType] || workflowStepsDef.value.outbound
  const nextStep = steps[activeIndex + 1]
  return nextStep?.role || null
})

const previousLabel = computed(() => {
  const activeIndex = workflowOrder.indexOf(props.currentStatus)
  if (activeIndex <= 0) return null
  return '上一步'
})

const nextLabel = computed(() => {
  const activeIndex = workflowOrder.indexOf(props.currentStatus)
  if (activeIndex >= 5) return null
  return '下一步'
})

function getStepState(index, activeIndex, activeStatus) {
  // Handle special states
  if (['rejected', 'cancelled'].includes(activeStatus)) {
    return index < Math.max(activeIndex, 0) ? 'complete' : 'upcoming'
  }
  if (activeStatus === 'partially_confirmed') {
    if (index < 2) return 'complete'
    if (index === 2) return 'current'
    return 'upcoming'
  }
  if (activeStatus === 'transport_notified') {
    if (index < 3) return 'complete'
    if (index === 3) return 'current'
    return 'upcoming'
  }
  if (activeStatus === 'final_confirmation_pending') {
    if (index < 4) return 'complete'
    if (index === 4) return 'current'
    return 'upcoming'
  }
  if (activeIndex === -1) return 'upcoming'
  if (index < activeIndex) return 'complete'
  if (index === activeIndex) return 'current'
  return 'upcoming'
}

function stepClass(state) {
  if (state === 'complete') return 'border-emerald-500/30 bg-emerald-500/10'
  if (state === 'current') return 'border-sky-500/40 bg-sky-500/10'
  if (state === 'blocked') return 'border-rose-500/30 bg-rose-500/10'
  return 'border-border bg-muted/20'
}

function stepDotClass(state) {
  if (state === 'complete') return 'bg-emerald-500 text-white'
  if (state === 'current') return 'bg-sky-500 text-white'
  if (state === 'blocked') return 'bg-rose-500 text-white'
  return 'bg-muted text-muted-foreground'
}
</script>
