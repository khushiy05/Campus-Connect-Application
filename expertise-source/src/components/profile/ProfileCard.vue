<template>
  <div class="mb-6 rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
    <div class="flex flex-col items-center gap-5 xl:flex-row">
      <div
        class="bg-brand-500 flex h-20 w-20 shrink-0 items-center justify-center rounded-full text-2xl font-semibold text-white"
      >
        {{ initials }}
      </div>
      <div>
        <h4
          class="mb-2 text-center text-lg font-semibold text-gray-800 dark:text-white/90 xl:text-left"
        >
          {{ profile?.name }}
        </h4>
        <div class="flex flex-col items-center gap-1 xl:flex-row xl:gap-3">
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ profile?.college_name }}</p>
          <div class="hidden h-3.5 w-px bg-gray-300 dark:bg-gray-700 xl:block"></div>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ profile?.city }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: {
    type: Object,
    default: () => ({}),
  },
})

const initials = computed(() =>
  (props.profile?.name || '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join(''),
)
</script>