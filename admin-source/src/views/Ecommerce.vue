<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">
      
      <div class="col-span-12">
        <EcommerceMetrics />
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

onMounted(() => {
  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>