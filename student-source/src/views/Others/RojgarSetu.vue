<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="RojgarSetu">
        <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
          Loading job postings...
        </div>

        <div v-else-if="error" class="py-10 text-center text-error-500">
          {{ error }}
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-gray-100 dark:border-gray-800">
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Job Title</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Company</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Location</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Experience</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Salary (LPA)</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Apply</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="job in jobs"
                :key="job.JobId"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ job.JobTitle }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ job.CompanyName }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ job.Location }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ job.Experience }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ job.SalaryLPA }}</td>
                <td class="px-4 py-3 text-sm">
                  <a
                    v-if="job.ApplicationLink"
                    :href="job.ApplicationLink"
                    target="_blank"
                    rel="noopener"
                    class="px-2.5 py-1 rounded-md bg-brand-500 text-white text-xs font-medium hover:bg-brand-600"
                  >
                    Apply
                  </a>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="jobs.length === 0" class="py-10 text-center text-gray-500 dark:text-gray-400">
            No job postings yet.
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

const currentPageTitle = ref("RojgarSetu");

const jobs = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/rojgarsetu", { credentials: "include" });
    const data = await res.json();

    if (data.success) {
      jobs.value = data.data;
    } else {
      error.value = data.error || "Failed to load job postings.";
    }
  } catch (e) {
    error.value = "Unable to connect to the server.";
  } finally {
    loading.value = false;
  }
});
</script>