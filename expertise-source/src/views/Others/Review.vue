<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Leave a Review">
        <div v-if="submitted" class="py-6 text-center text-success-600 dark:text-success-500">
          Thank you! Your review has been submitted.
        </div>

        <form v-else @submit.prevent="submitReview" class="flex flex-col gap-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Name
            </label>
            <input
              v-model="name"
              type="text"
              required
              placeholder="Your name"
              class="dark:bg-dark-900 h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Rating
            </label>
            <div class="flex items-center gap-1">
              <button
                v-for="star in 5"
                :key="star"
                type="button"
                @click="rating = star"
                class="text-2xl leading-none"
                :class="star <= rating ? 'text-warning-400' : 'text-gray-300 dark:text-gray-700'"
              >
                ★
              </button>
            </div>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
              Message
            </label>
            <textarea
              v-model="message"
              required
              rows="4"
              placeholder="Share your feedback..."
              class="dark:bg-dark-900 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
            ></textarea>
          </div>

          <div v-if="error" class="text-sm text-error-500">{{ error }}</div>

          <button
            type="submit"
            :disabled="submitting || rating === 0"
            class="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 sm:w-auto"
          >
            {{ submitting ? "Submitting..." : "Submit" }}
          </button>
        </form>
      </ComponentCard>

      <ComponentCard title="Recent Reviews">
        <div v-if="loadingReviews" class="py-10 text-center text-gray-500 dark:text-gray-400">
          Loading reviews...
        </div>
        <div v-else-if="reviews.length === 0" class="py-10 text-center text-gray-500 dark:text-gray-400">
          No reviews yet.
        </div>
        <div v-else class="flex flex-col divide-y divide-gray-100 dark:divide-gray-800">
          <div v-for="r in reviews" :key="r.ReviewId" class="py-4">
            <div class="flex items-center justify-between">
              <span class="font-medium text-gray-800 dark:text-white/90">{{ r.Name }}</span>
              <span class="text-warning-400">{{ "★".repeat(r.Rating) }}{{ "☆".repeat(5 - r.Rating) }}</span>
            </div>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">{{ r.Message }}</p>
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

const currentPageTitle = ref("Review");

const name = ref("");
const message = ref("");
const rating = ref(0);
const submitting = ref(false);
const submitted = ref(false);
const error = ref(null);

const reviews = ref([]);
const loadingReviews = ref(true);

onMounted(async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/reviews", { credentials: "include" });
    const data = await res.json();
    if (data.success) {
      reviews.value = data.data;
    }
  } catch (e) {
    console.error("Failed to load reviews:", e);
  } finally {
    loadingReviews.value = false;
  }
});

async function submitReview() {
  if (rating.value === 0) {
    error.value = "Please select a rating.";
    return;
  }

  error.value = null;
  submitting.value = true;

  try {
    const res = await fetch("http://127.0.0.1:5000/api/reviews", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name.value,
        message: message.value,
        rating: rating.value,
      }),
    });
    const data = await res.json();

    if (data.success) {
      submitted.value = true;
    } else {
      error.value = data.error || "Failed to submit review.";
    }
  } catch (e) {
    error.value = "Unable to connect to the server.";
  } finally {
    submitting.value = false;
  }
}
</script>