<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div :class="cn('rounded-2xl border border-border/50 bg-card text-card-foreground shadow-shimmer transition-all hover:shadow-lg hover:scale-[1.002]', props.class)">
    <slot />
  </div>
</template>
