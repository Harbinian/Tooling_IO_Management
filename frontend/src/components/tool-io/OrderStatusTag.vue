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
  draft: 'Draft',
  submitted: 'Submitted',
  keeper_confirmed: 'Keeper confirmed',
  partially_confirmed: 'Partially confirmed',
  transport_notified: 'Transport notified',
  final_confirmation_pending: 'Final confirmation pending',
  completed: 'Completed',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
  pending_check: 'Pending check',
  approved: 'Approved'
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
