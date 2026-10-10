<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="space-y-6">
      <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
        Loading job postings...
      </div>

      <div v-else-if="error" class="py-10 text-center text-error-500">
        {{ error }}
      </div>

      <div v-else>
        <!-- Heading -->
        <h1 class="mb-6 text-3xl font-bold text-gray-800 dark:text-white/90 sm:text-4xl">
          Latest <span class="text-[#FF6B00]">Job Openings</span>
        </h1>

        <!-- Search -->
        <div class="mb-6">
          <input
            v-model="searchQuery"
            type="text"
            autocomplete="off"
            placeholder="Search jobs by title, company, category or city..."
            class="h-11 w-full rounded-lg border border-gray-300 bg-white px-4 text-sm text-gray-800 placeholder:text-gray-400 focus:border-[#FF6B00] focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/20 dark:border-gray-700 dark:bg-white/[0.03] dark:text-white/90"
          />
        </div>

        <!-- Job Cards -->
        <div class="space-y-4">
          <div
            v-for="job in filteredJobs"
            :key="job.JobId"
            class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div class="flex flex-col items-center gap-4 md:flex-row">
              <!-- Icon -->
              <div class="flex w-full justify-center md:w-24 md:flex-shrink-0">
                <div
                  class="flex h-[60px] w-[60px] items-center justify-center rounded-full bg-gray-100 dark:bg-white/5"
                >
                  <svg class="h-6 w-6 text-[#FF6B00]" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M20 6h-4V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zM10 4h4v2h-4V4zm10 9H4v-2h16v2z"
                    />
                  </svg>
                </div>
              </div>

              <!-- Details -->
              <div class="min-w-0 flex-1 text-center md:text-left">
                <h5 class="mb-1 text-lg font-medium text-gray-800 dark:text-white/90">
                  {{ job.JobTitle }} — {{ job.CompanyName }}
                </h5>
                <p class="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-sm text-gray-500 dark:text-gray-400 md:justify-start">
                  <span class="inline-flex items-center gap-1">
                    <svg class="h-4 w-4 text-[#FF6B00]" viewBox="0 0 24 24" fill="currentColor">
                      <path
                        d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"
                      />
                    </svg>
                    {{ job.Location }}, India
                  </span>
                  <span v-if="job.JobCategory" class="text-gray-300 dark:text-gray-600">|</span>
                  <span
                    v-if="job.JobCategory"
                    class="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-800 dark:bg-white/10 dark:text-white/90"
                  >
                    {{ job.JobCategory }}
                  </span>
                  <span class="text-gray-300 dark:text-gray-600">|</span>
                  <span class="text-xs">Exp: {{ job.Experience }}</span>
                </p>
              </div>

              <!-- Apply + Salary -->
              <div class="flex flex-col items-center md:items-end md:text-right">
                <a
                  v-if="job.ApplicationLink"
                  :href="job.ApplicationLink"
                  target="_blank"
                  rel="noopener"
                  class="rounded-md bg-[#FF6B00] px-3.5 py-1.5 text-sm font-medium text-white hover:bg-[#e55f00]"
                >
                  Apply Now
                </a>
                <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Salary: {{ formatSalary(job.SalaryLPA) }}
                </p>
              </div>
            </div>
          </div>

          <p v-if="filteredJobs.length === 0" class="py-6 text-center text-gray-500 dark:text-gray-400">
            {{ jobs.length === 0 ? "No job postings yet. Check back soon!" : "No jobs match your search." }}
          </p>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("RojgarSetu");

const jobs = ref([]);
const loading = ref(true);
const error = ref(null);

const searchQuery = ref("");

// Matches title, company, category, city (and experience / salary text too)
const filteredJobs = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return jobs.value;
  return jobs.value.filter((job) =>
    [job.JobTitle, job.CompanyName, job.JobCategory, job.Location, job.Experience, job.SalaryLPA].some((v) =>
      (v ?? "").toString().toLowerCase().includes(q)
    )
  );
});

// Avoid "LPA LPA" when the value already contains LPA
const formatSalary = (val) => {
  const s = (val ?? "").toString().trim();
  if (!s) return "—";
  return /lpa/i.test(s) ? s : `${s} LPA`;
};

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