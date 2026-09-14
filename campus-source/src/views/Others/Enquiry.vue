<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Enquiries">
        <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
          Loading enquiries...
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
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Message</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in enquiries"
                :key="row.id"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.id }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.name }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.email }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.mobile }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ row.message }}</td>
                <td class="px-4 py-3 text-sm">
                  <button
                    @click="deleteEnquiry(row.id)"
                    :disabled="deletingId === row.id"
                    class="px-3 py-1.5 rounded-md bg-error-500 text-white text-xs font-medium hover:bg-error-600 disabled:opacity-50"
                  >
                    {{ deletingId === row.id ? "Deleting..." : "Delete" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="enquiries.length === 0" class="py-10 text-center text-gray-500 dark:text-gray-400">
            No enquiries yet.
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

const currentPageTitle = ref("Enquiry");

const enquiries = ref([]);
const loading = ref(true);
const error = ref(null);
const deletingId = ref(null);

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/enquiries");
    const data = await res.json();

    if (data.success) {
      enquiries.value = data.data;
    } else {
      error.value = data.error || "Failed to load enquiries.";
    }
  } catch (e) {
    error.value = "Unable to connect to the server.";
  } finally {
    loading.value = false;
  }
});

async function deleteEnquiry(id) {
  if (!confirm("Are you sure you want to delete this enquiry?")) return;

  deletingId.value = id;
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/enquiries/${id}`, {
      method: "DELETE",
    });
    const data = await res.json();

    if (data.success) {
      enquiries.value = enquiries.value.filter((row) => row.id !== id);
    } else {
      alert(data.error || "Failed to delete enquiry.");
    }
  } catch (e) {
    alert("Unable to connect to the server.");
  } finally {
    deletingId.value = null;
  }
}
</script>