<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: any
  label: string
  value: number | string
  change?: number // e.g. 11.01 or -9.05
}

const props = defineProps<Props>()

const isPositive = computed(() => (props.change ?? 0) >= 0)
</script>

<template>
  <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-5">
    <div class="flex items-center justify-center w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-xl">
      <component :is="icon" class="w-6 h-6 text-gray-800 dark:text-white" />
    </div>

    <div class="mt-5">
      <span class="text-sm text-gray-500 dark:text-gray-400">{{ label }}</span>
      <div class="flex items-end justify-between mt-2">
        <h4 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ value }}
        </h4>
        <span
          v-if="change !== undefined"
          class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
          :class="isPositive
            ? 'bg-green-50 text-green-600 dark:bg-green-500/15 dark:text-green-400'
            : 'bg-red-50 text-red-600 dark:bg-red-500/15 dark:text-red-400'"
        >
          <svg v-if="isPositive" class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 5l7 7-1.4 1.4L13 8.8V19h-2V8.8l-4.6 4.6L5 12z" fill="currentColor" />
          </svg>
          <svg v-else class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 19l-7-7 1.4-1.4L11 15.2V5h2v10.2l4.6-4.6L19 12z" fill="currentColor" />
          </svg>
          {{ Math.abs(change) }}%
        </span>
      </div>
    </div>
  </div>
</template>