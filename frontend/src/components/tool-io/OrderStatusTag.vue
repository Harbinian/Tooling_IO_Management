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
  info: 'border-slate-200 bg-slate-50 text-slate-600',
  warning: 'border-amber-200 bg-amber-50/50 text-amber-700',
  success: 'border-emerald-200 bg-emerald-50/50 text-emerald-700',
  primary: 'border-sky-200 bg-sky-50/50 text-sky-700',
  danger: 'border-rose-200 bg-rose-50/50 text-rose-700'
}

const badgeClass = computed(() =>
  cn(
    'rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider shadow-none transition-all',
    toneMap[presentation.value.type] || toneMap.info
  )
)
</script>
