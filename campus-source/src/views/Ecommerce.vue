<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">
      
      <div class="col-span-12 text-center text-gray-400 dark:text-gray-500 py-12">
        Welcome to your Campus Panel.
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'

onMounted(() => {
  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>