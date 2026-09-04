<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="News">
        <div class="p-6">
          <h4 class="mb-6 text-lg font-semibold text-gray-800 dark:text-white/90">
            Add News
          </h4>

          <form @submit.prevent="submitForm" class="grid grid-cols-1 gap-y-5">

            <!-- Title -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Title
              </label>
              <input
                v-model="form.title"
                type="text"
                placeholder="Enter news title"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Description
              </label>
              <textarea
                v-model="form.description"
                rows="5"
                placeholder="Enter news description"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              ></textarea>
            </div>

            <!-- Upload File -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Upload File
              </label>
              <input
                ref="fileInputRef"
                type="file"
                @change="handleFileChange"
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white file:mr-4 file:rounded-md file:border-0 file:bg-orange-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-orange-600 hover:file:bg-orange-100"
              />
              <p class="mt-1 text-xs text-gray-400">
                Any file type (image, PDF, or document) — optional
              </p>
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-2">
              <button
                type="submit"
                :disabled="submitting"
                class="rounded-lg bg-orange-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-60"
              >
                {{ submitting ? 'Submitting...' : 'Submit' }}
              </button>
              <button
                type="button"
                @click="showTable = !showTable"
                class="rounded-lg bg-gray-800 px-6 py-2.5 text-sm font-medium text-white hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                {{ showTable ? 'Hide' : 'Show' }}
              </button>
            </div>

            <p v-if="statusMessage" class="text-sm" :class="statusOk ? 'text-green-600' : 'text-red-600'">
              {{ statusMessage }}
            </p>

          </form>
        </div>

        <!-- Submitted News Table -->
        <div v-if="showTable" class="border-t border-gray-100 p-6 dark:border-gray-800">
          <h4 class="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">
            Submitted News ({{ newsList.length }})
          </h4>

          <div v-if="!newsList.length" class="py-6 text-center text-sm text-gray-400">
            No news submitted yet.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full min-w-[700px] text-left text-sm">
              <thead>
                <tr class="border-b border-gray-200 text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  <th class="px-3 py-2 font-medium">Title</th>
                  <th class="px-3 py-2 font-medium">Description</th>
                  <th class="px-3 py-2 font-medium">File</th>
                  <th class="px-3 py-2 font-medium">Posted On</th>
                  <th class="px-3 py-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in newsList"
                  :key="item.NewsId"
                  class="border-b border-gray-100 text-gray-700 dark:border-gray-800 dark:text-gray-300"
                >
                  <td class="px-3 py-2">{{ item.Title }}</td>
                  <td class="px-3 py-2 max-w-[300px] truncate" :title="item.Description">
                    {{ item.Description }}
                  </td>
                  <td class="px-3 py-2">
                    <a
                      v-if="item.FilePath"
                      :href="`${API_BASE}/static/uploads/news/${item.FilePath}`"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-orange-500 hover:underline"
                    >
                      View
                    </a>
                    <span v-else class="text-gray-400">—</span>
                  </td>
                  <td class="px-3 py-2">{{ item.PostedOn }}</td>
                  <td class="px-3 py-2">
                    <button
                      type="button"
                      @click="removeNews(item.NewsId)"
                      class="text-xs font-medium text-red-500 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
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

const currentPageTitle = ref("Add News");

// Base URL of the Flask API. Vue (Vite) runs on :5173, Flask runs on :5000 —
// change this if your Flask server runs somewhere else.
const API_BASE = "http://127.0.0.1:5000";

const form = ref({
  title: "",
  description: "",
});

const selectedFile = ref(null);
const fileInputRef = ref(null);

function handleFileChange(event) {
  selectedFile.value = event.target.files[0] || null;
}

const newsList = ref([]);
const showTable = ref(false);
const submitting = ref(false);
const statusMessage = ref("");
const statusOk = ref(false);

async function fetchNews() {
  try {
    const res = await fetch(`${API_BASE}/api/news`);
    const result = await res.json();

    if (result.success) {
      newsList.value = result.data;
    } else {
      console.error("Could not load news:", result.error);
    }
  } catch (err) {
    console.error("Failed to load news:", err);
  }
}

async function submitForm() {
  submitting.value = true;
  statusMessage.value = "";

  try {
    const formData = new FormData();
    formData.append("title", form.value.title);
    formData.append("description", form.value.description);
    if (selectedFile.value) {
      formData.append("file", selectedFile.value);
    }

    // NOTE: Do NOT set a Content-Type header here — the browser sets the
    // correct multipart/form-data boundary automatically when the body
    // is a FormData object. Setting it manually breaks the upload.
    const res = await fetch(`${API_BASE}/api/news`, {
      method: "POST",
      body: formData,
    });

    const result = await res.json();

    if (!result.success) {
      statusOk.value = false;
      statusMessage.value = result.error || "Something went wrong.";
      return;
    }

    statusOk.value = true;
    statusMessage.value = "News posted successfully!";

    // Reset form
    form.value.title = "";
    form.value.description = "";
    selectedFile.value = null;
    if (fileInputRef.value) fileInputRef.value.value = "";

    // Refresh table
    await fetchNews();

  } catch (err) {
    statusOk.value = false;
    statusMessage.value = "Could not connect to server.";
    console.error(err);
  } finally {
    submitting.value = false;
  }
}

async function removeNews(id) {
  if (!confirm("Delete this news item?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/news/${id}`, {
      method: "DELETE",
    });
    const result = await res.json();
    if (result.success) {
      newsList.value = newsList.value.filter((n) => n.NewsId !== id);
    } else {
      alert(result.error || "Could not delete.");
    }
  } catch (err) {
    console.error(err);
    alert("Could not connect to server.");
  }
}

onMounted(() => {
  fetchNews();
});
</script>