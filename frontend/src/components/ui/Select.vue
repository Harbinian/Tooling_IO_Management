<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  class: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

function handleChange(event) {
  emit('update:modelValue', event.target.value)
}
</script>

<template>
  <select
    :value="modelValue"
    :disabled="disabled"
    @change="handleChange"
    :class="cn(
      'flex h-10 w-full rounded-md border border-input bg-background/50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-sm',
      props.class
    )"
  >
    <slot />
  </select>
</template>
