<template>
  <Badge :class="badgeClass">
    {{ presentation.label }}
  </Badge>
</template>

<script setup>
import { computed } from 'vue'
import Badge from '@/components/ui/Badge.vue'
import { cn } from '@/lib/utils'
import { getStatusPresentation } from '@/utils/toolIO'

const props = defineProps({
  status: {
    type: String,
    default: ''
  },
  item: {
    type: Boolean,
    default: false
  }
})

const labelMap = {
  draft: '草稿',
  submitted: '已提交',
  keeper_confirmed: '保管员已确认',
  partially_confirmed: '部分确认',
  transport_notified: '已通知运输',
  transport_in_progress: '运输中',
  transport_completed: '运输已完成',
  final_confirmation_pending: '待最终确认',
  completed: '已完成',
  rejected: '已驳回',
  cancelled: '已取消',
  pending_check: '待确认',
  approved: '已通过'
}

const presentation = computed(() => {
  const base = getStatusPresentation(props.status, props.item)
  return {
    ...base,
    label: labelMap[props.status] || base.label || props.status || '-'
  }
})

const toneMap = {
  info: 'border-muted bg-muted text-muted-foreground',
  warning: 'border-amber-500/20 bg-amber-500/10 text-amber-500',
  success: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-500',
  primary: 'border-blue-500/20 bg-blue-500/10 text-blue-500',
  danger: 'border-rose-500/20 bg-rose-500/10 text-rose-500'
}

const badgeClass = computed(() =>
  cn(
    'rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider shadow-none transition-all',
    toneMap[presentation.value.type] || toneMap.info
  )
)
</script>
