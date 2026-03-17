<script setup>
import { cn } from '@/lib/utils'
import { ref, computed, onMounted, onUnmounted } from 'vue'

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
  options: {
    type: Array,
    default: () => []
  },
  optionLabel: {
    type: String,
    default: 'label'
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  placeholder: {
    type: String,
    default: '请选择'
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const selectRef = ref(null)

const selectedLabel = computed(() => {
  if (!props.modelValue) return ''
  const selected = props.options.find(opt => opt[props.optionValue] === props.modelValue)
  return selected ? selected[props.optionLabel] : ''
})

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function selectOption(option) {
  emit('update:modelValue', option[props.optionValue])
  isOpen.value = false
}

function handleClickOutside(event) {
  if (selectRef.value && !selectRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="selectRef" class="relative">
    <button
      type="button"
      :disabled="disabled"
      @click="toggleDropdown"
      :class="cn(
        'flex h-10 w-full items-center justify-between rounded-md border border-border/50 bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all shadow-sm text-left',
        props.class
      )"
    >
      <span :class="modelValue ? 'text-foreground' : 'text-muted-foreground'">
        {{ selectedLabel || placeholder }}
      </span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-full overflow-hidden rounded-md border border-border/50 bg-white shadow-lg"
      >
        <div class="max-h-60 overflow-y-auto py-1">
          <button
            v-for="option in options"
            :key="option[optionValue]"
            type="button"
            @click="selectOption(option)"
            :class="cn(
              'w-full px-3 py-2 text-left text-sm hover:bg-slate-100 focus:bg-slate-100 focus:outline-none',
              option[optionValue] === modelValue ? 'bg-slate-100 font-medium text-foreground' : 'text-foreground'
            )"
          >
            {{ option[optionLabel] }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
