<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12">
        <p class="text-gray-600 dark:text-gray-400">
          Welcome to your Admin Panel,
          <span class="font-semibold text-brand-500">{{ userName }}</span>!
        </p>
      </div>

      <div class="col-span-12">
        <EcommerceMetrics />
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'
import EcommerceMetrics from '../components/ecommerce/EcommerceMetrics.vue'

const userName = 'Admin'

onMounted(() => {
  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>