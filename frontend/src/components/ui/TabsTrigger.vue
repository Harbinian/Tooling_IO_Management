<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  value: {
    type: String,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <button
    type="button"
    @click="$emit('update:modelValue', value)"
    :class="cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-bold tracking-tight ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
      modelValue === value 
        ? 'bg-background text-foreground shadow-sm scale-[1.02]' 
        : 'hover:bg-background/50 hover:text-foreground hover:scale-[1.01]',
      props.class
    )"
  >
    <slot />
  </button>
</template>
