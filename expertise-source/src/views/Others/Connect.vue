<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div
      class="h-[calc(100vh-13rem)] min-h-[480px] overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <div
        class="flex items-center border-b border-gray-200 px-5 py-3 dark:border-gray-800"
      >
        <h3 class="text-sm font-semibold text-gray-800 dark:text-white/90">Connect</h3>
      </div>

      <div class="flex h-[calc(100%-3rem)] items-center justify-center p-6">
        <p class="text-sm text-gray-400">Connect page content goes here.</p>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("Connect");
</script>