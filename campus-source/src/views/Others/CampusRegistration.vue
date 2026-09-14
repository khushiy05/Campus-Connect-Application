<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Campus Registrations">
        <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
          Loading registrations...
        </div>

        <div v-else-if="error" class="py-10 text-center text-error-500">
          {{ error }}
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-gray-100 dark:border-gray-800">
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">ID</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Name</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Email</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Mobile No.</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">City</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">College</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Registered On</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in registrations"
                :key="row.id"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.id }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.name }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.email }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.mobile }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.city }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.college_name }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.registered_on }}</td>
                <td class="px-4 py-3 text-sm">
                  <button
                    v-if="!row.approved"
                    @click="approveRegistration(row.id)"
                    :disabled="approvingId === row.id"
                    class="px-3 py-1.5 rounded-md bg-success-500 text-white text-xs font-medium hover:bg-success-600 disabled:opacity-50"
                  >
                    {{ approvingId === row.id ? "Approving..." : "Approve" }}
                  </button>
                  <span
                    v-else
                    class="px-3 py-1.5 rounded-md bg-success-50 text-success-600 text-xs font-medium"
                  >
                    Approved
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="registrations.length === 0" class="py-10 text-center text-gray-500 dark:text-gray-400">
            No registrations yet.
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

const currentPageTitle = ref("Campus Registration");

const registrations = ref([]);
const loading = ref(true);
const error = ref(null);
const approvingId = ref(null);

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/registrations");
    const data = await res.json();

    if (data.success) {
      registrations.value = data.data;
    } else {
      error.value = data.error || "Failed to load registrations.";
    }
  } catch (e) {
    error.value = "Unable to connect to the server.";
  } finally {
    loading.value = false;
  }
});

async function approveRegistration(id) {
  approvingId.value = id;
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/registrations/${id}/approve`, {
      method: "PUT",
    });
    const data = await res.json();

    if (data.success) {
      const row = registrations.value.find((r) => r.id === id);
      if (row) row.approved = true;
    } else {
      alert(data.error || "Failed to approve registration.");
    }
  } catch (e) {
    alert("Unable to connect to the server.");
  } finally {
    approvingId.value = null;
  }
}
</script>