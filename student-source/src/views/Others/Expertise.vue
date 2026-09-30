<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Expertise">
        <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
          Loading experts...
        </div>

        <div v-else-if="error" class="py-10 text-center text-error-500">
          {{ error }}
        </div>

        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="expert in experts"
            :key="expert.ID"
            class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div class="flex items-center gap-3">
              <img
                v-if="expert.Photo"
                :src="`/static/uploads/experts/${expert.Photo}`"
                alt=""
                class="h-12 w-12 rounded-full object-cover"
              />
              <div
                v-else
                class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-400 dark:bg-gray-800"
              >
                👤
              </div>
              <div>
                <p class="font-medium text-gray-800 dark:text-white/90">{{ expert.Name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ expert.Domain }}</p>
              </div>
            </div>
            <a
              v-if="expert.LinkedinURL"
              :href="expert.LinkedinURL"
              target="_blank"
              rel="noopener"
              class="mt-3 inline-block text-xs font-medium text-brand-500 hover:underline"
            >
              View LinkedIn
            </a>
          </div>

          <div v-if="experts.length === 0" class="col-span-full py-10 text-center text-gray-500 dark:text-gray-400">
            No experts yet.
          </div>
        </div>
      </ComponentCard>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Expertise");

const experts = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/experts", { credentials: "include" });
    const data = await res.json();

    if (data.success) {
      experts.value = data.data;
    } else {
      error.value = data.error || "Failed to load experts.";
    }
  } catch (e) {
    error.value = "Unable to connect to the server.";
  } finally {
    loading.value = false;
  }
});
</script>