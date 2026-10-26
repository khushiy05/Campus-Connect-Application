<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div
      class="min-h-[480px] rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <!-- ============ LIST VIEW ============ -->
      <div v-if="!selected">
        <div
          class="flex items-center border-b border-gray-200 px-5 py-3 dark:border-gray-800"
        >
          <h3 class="text-sm font-semibold text-gray-800 dark:text-white/90">
            Experts you can connect with
          </h3>
        </div>

        <div v-if="loading" class="p-10 text-center text-sm text-gray-400">
          Loading experts...
        </div>

        <div v-else-if="error" class="p-10 text-center text-sm text-error-500">
          {{ error }}
          <button class="ml-2 underline" @click="loadExpertise">Try again</button>
        </div>

        <div
          v-else-if="!expertiseList.length"
          class="p-10 text-center text-sm text-gray-400"
        >
          No experts have been added yet.
        </div>

        <div
          v-else
          class="grid grid-cols-1 gap-5 p-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
        >
          <div
            v-for="exp in expertiseList"
            :key="exp.id"
            class="flex flex-col items-center rounded-xl border border-gray-200 p-5 text-center dark:border-gray-800"
          >
            <img
              v-if="exp.photo_url"
              :src="API_ORIGIN + exp.photo_url"
              :alt="exp.name"
              class="h-28 w-28 rounded-full object-cover"
            />
            <div
              v-else
              class="flex h-28 w-28 items-center justify-center rounded-full bg-brand-500 text-3xl font-semibold text-white"
            >
              {{ exp.name?.charAt(0) }}
            </div>

            <h4 class="mt-4 text-base font-semibold text-gray-800 dark:text-white/90">
              {{ exp.name }}
            </h4>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ exp.role || exp.domain }}</p>

            <button
              class="mt-4 w-full rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600"
              @click="openExpert(exp)"
            >
              Connect
            </button>
          </div>
        </div>
      </div>

      <!-- ============ DETAIL + MESSAGE VIEW ============ -->
      <div v-else>
        <div
          class="flex items-center gap-3 border-b border-gray-200 px-5 py-3 dark:border-gray-800"
        >
          <button
            class="text-sm text-gray-500 hover:text-gray-800 dark:hover:text-white"
            @click="closeExpert"
          >
            &larr; Back to experts
          </button>
        </div>

        <div class="grid grid-cols-1 gap-8 p-6 lg:grid-cols-2">
          <!-- Left: photo + all info -->
          <div class="space-y-5">
            <img
              v-if="selected.photo_url"
              :src="API_ORIGIN + selected.photo_url"
              :alt="selected.name"
              class="h-64 w-full rounded-xl object-cover"
            />
            <div
              v-else
              class="flex h-64 w-full items-center justify-center rounded-xl bg-brand-500 text-6xl font-semibold text-white"
            >
              {{ selected.name?.charAt(0) }}
            </div>

            <div class="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
              <h3 class="text-lg font-semibold text-gray-800 dark:text-white/90">
                {{ selected.name }}
              </h3>

              <dl class="mt-4 space-y-3 text-sm">
                <div v-for="row in infoRows" :key="row.label">
                  <dt class="text-gray-500 dark:text-gray-400">{{ row.label }}</dt>
                  <dd class="mt-0.5 text-gray-800 dark:text-white/90">
                    <a v-if="row.href" :href="row.href" target="_blank" rel="noopener" class="text-brand-500 underline">{{ row.value }}</a>
                    <span v-else>{{ row.value }}</span>
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <!-- Right: email form -->
          <form class="space-y-5" @submit.prevent="sendMessage">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Your email
              </label>
              <input
                v-model="form.email"
                type="email"
                required
                placeholder="you@example.com"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:text-white/90"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Subject
              </label>
              <input
                v-model="form.subject"
                type="text"
                required
                placeholder="What is this about?"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:text-white/90"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                Message
              </label>
              <textarea
                v-model="form.message"
                required
                rows="7"
                placeholder="Write your message..."
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-3 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:text-white/90"
              ></textarea>
            </div>

            <p v-if="sendStatus" :class="sendOk ? 'text-success-600' : 'text-error-500'" class="text-sm">
              {{ sendStatus }}
            </p>

            <button
              type="submit"
              :disabled="sending"
              class="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-60"
            >
              {{ sending ? "Sending..." : "Send" }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("Connect");

/* ------------------------------------------------------------------
   1. FETCH EXPERTISE (same data that the Home/Dashboard page uses)
   Change API_BASE / the two endpoints below to match your backend.
------------------------------------------------------------------- */
const API_ORIGIN = "http://127.0.0.1:5000"; // Flask server
const EXPERTISE_URL = `${API_ORIGIN}/api/experts`;
const SEND_URL = `${API_ORIGIN}/api/connect/send`;

const expertiseList = ref([]);
const loading = ref(false);
const error = ref("");

const loadExpertise = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await fetch(EXPERTISE_URL, { credentials: "include" });
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      throw new Error(`Server returned ${res.status} (not JSON) for ${EXPERTISE_URL}`);
    }
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error || "Request failed");
    // same endpoint + field names the admin Expertise page uses
    expertiseList.value = (data.data || []).map((e) => ({
      id: e.ID,
      name: e.Name,
      role: e.Role,
      domain: e.Domain,
      city: e.City,
      about: e.About,
      linkedin: e.LinkedinURL,
      photo_url: e.Photo ? `/static/uploads/experts/${e.Photo}` : null,
    }));
  } catch (e) {
    error.value = e.message === "Failed to fetch" ? "Cannot reach the server. Is Flask running on port 5000?" : (e.message || "Could not load experts.");
  } finally {
    loading.value = false;
  }
};

onMounted(loadExpertise);

/* ------------------------------------------------------------------
   2. OPEN ONE EXPERT -> show all info
------------------------------------------------------------------- */
const selected = ref(null);

const openExpert = (exp) => {
  selected.value = exp;
  form.value = { email: "", subject: "", message: "" };
  sendStatus.value = "";
};
const closeExpert = () => (selected.value = null);

// Edit this list to match the fields your expertise object really has.
const infoRows = computed(() => {
  const s = selected.value;
  if (!s) return [];
  return [
    { label: "Role", value: s.role },
    { label: "Expertise", value: s.domain },
    { label: "About", value: s.about },
    { label: "City", value: s.city },
    { label: "LinkedIn", value: s.linkedin ? "View profile" : "", href: s.linkedin },
  ].filter((r) => r.value);
});

/* ------------------------------------------------------------------
   3. SEND MESSAGE
------------------------------------------------------------------- */
const form = ref({ email: "", subject: "", message: "" });
const sending = ref(false);
const sendStatus = ref("");
const sendOk = ref(false);

const sendMessage = async () => {
  sending.value = true;
  sendStatus.value = "";
  try {
    const res = await fetch(SEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        expert_id: selected.value.id,
        from_email: form.value.email,
        subject: form.value.subject,
        message: form.value.message,
      }),
    });
    const out = await res.json();
    if (!res.ok || !out.success) throw new Error(out.error || "Request failed");
    sendOk.value = true;
    sendStatus.value = "Message sent.";
    form.value = { email: "", subject: "", message: "" };
  } catch (e) {
    sendOk.value = false;
    sendStatus.value = e.message || "Message could not be sent. Please try again.";
  } finally {
    sending.value = false;
  }
};
</script>