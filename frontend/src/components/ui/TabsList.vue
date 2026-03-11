<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'outbound',
  },
  class: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div :class="cn('inline-flex h-10 items-center justify-center rounded-xl bg-muted/50 p-1 text-muted-foreground backdrop-blur-sm border border-border/50', props.class)">
    <slot />
  </div>
</template>
