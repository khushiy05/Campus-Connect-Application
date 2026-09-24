<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Review">
        <div class="p-6">
          <h4 class="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
            Share a Review
          </h4>
          <p class="mb-6 text-sm text-gray-500 dark:text-gray-400">
            Tell us what you think about Campus Panel
          </p>

          <form @submit.prevent="submitForm" class="grid grid-cols-1 gap-y-5 max-w-xl">

            <!-- Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Name
              </label>
              <input
                v-model="form.name"
                type="text"
                placeholder="Your name"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              />
            </div>

            <!-- Message -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Message
              </label>
              <textarea
                v-model="form.message"
                rows="4"
                placeholder="Write your feedback here..."
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              ></textarea>
            </div>

            <!-- Rating -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Rating
              </label>
              <div class="flex gap-1">
                <button
                  v-for="star in 5"
                  :key="star"
                  type="button"
                  class="text-2xl leading-none"
                  :class="star <= (hoverRating || form.rating) ? 'text-orange-500' : 'text-gray-300 dark:text-gray-600'"
                  @click="form.rating = star"
                  @mouseenter="hoverRating = star"
                  @mouseleave="hoverRating = 0"
                  :aria-label="`Rate ${star} star${star > 1 ? 's' : ''}`"
                >
                  ★
                </button>
              </div>
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-2">
              <button
                type="submit"
                :disabled="submitting"
                class="rounded-lg bg-orange-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-60"
              >
                {{ submitting ? 'Submitting...' : 'Submit Review' }}
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

        <!-- Submitted Reviews Table -->
        <div v-if="showTable" class="border-t border-gray-100 p-6 dark:border-gray-800">
          <h4 class="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">
            Submitted Reviews ({{ reviews.length }})
          </h4>

          <div v-if="!reviews.length" class="py-6 text-center text-sm text-gray-400">
            No reviews submitted yet.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full min-w-[700px] text-left text-sm">
              <thead>
                <tr class="border-b border-gray-200 text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  <th class="px-3 py-2 font-medium">Name</th>
                  <th class="px-3 py-2 font-medium">Message</th>
                  <th class="px-3 py-2 font-medium">Rating</th>
                  <th class="px-3 py-2 font-medium">Posted On</th>
                  <th class="px-3 py-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in reviews"
                  :key="item.ReviewId"
                  class="border-b border-gray-100 text-gray-700 dark:border-gray-800 dark:text-gray-300"
                >
                  <td class="px-3 py-2">{{ item.Name }}</td>
                  <td class="px-3 py-2">{{ item.Message }}</td>
                  <td class="px-3 py-2 text-orange-500">{{ '★'.repeat(item.Rating) }}</td>
                  <td class="px-3 py-2">{{ item.PostedOn }}</td>
                  <td class="px-3 py-2">
                    <button
                      type="button"
                      @click="removeReview(item.ReviewId)"
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
import { ref, reactive, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Review");

// Base URL of the Flask API. Vue (Vite) runs on :5174, Flask runs on :5000 —
// change this if your Flask server runs somewhere else.
const API_BASE = "http://127.0.0.1:5000";

const form = reactive({
  name: "",
  message: "",
  rating: 0,
});
const hoverRating = ref(0);

// ---- Submissions table ----
const reviews = ref([]);
const showTable = ref(false);
const submitting = ref(false);
const statusMessage = ref("");
const statusOk = ref(false);

async function fetchReviews() {
  try {
    const res = await fetch(`${API_BASE}/api/reviews`);
    const result = await res.json();

    if (result.success) {
      reviews.value = result.data;
    } else {
      console.error("Could not load reviews:", result.error);
    }
  } catch (err) {
    console.error("Failed to load reviews:", err);
  }
}

async function submitForm() {
  if (!form.rating) {
    statusOk.value = false;
    statusMessage.value = "Please select a rating before submitting.";
    return;
  }

  submitting.value = true;
  statusMessage.value = "";

  try {
    const res = await fetch(`${API_BASE}/api/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const result = await res.json();

    if (result.success) {
      statusOk.value = true;
      statusMessage.value = "Thanks for your review!";
      form.name = "";
      form.message = "";
      form.rating = 0;

      // Refresh table
      await fetchReviews();
    } else {
      statusOk.value = false;
      statusMessage.value = result.error || "Something went wrong.";
    }
  } catch (err) {
    statusOk.value = false;
    statusMessage.value = "Could not connect to server.";
    console.error(err);
  } finally {
    submitting.value = false;
  }
}

async function removeReview(id) {
  if (!confirm("Delete this review?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/reviews/${id}`, {
      method: "DELETE",
    });
    const result = await res.json();
    if (result.success) {
      reviews.value = reviews.value.filter((r) => r.ReviewId !== id);
    } else {
      alert(result.error || "Could not delete.");
    }
  } catch (err) {
    console.error(err);
    alert("Could not connect to server.");
  }
}

onMounted(() => {
  fetchReviews();
});
</script>