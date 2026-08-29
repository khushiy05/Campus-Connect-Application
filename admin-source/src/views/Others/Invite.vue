<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Invite">

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

          <!-- LEFT: ID / EMAIL LIST -->
          <div class="lg:col-span-2 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-800">
              <div>
                <h3 class="font-semibold text-gray-800 dark:text-white/90">Recipients</h3>
                <p class="text-[11px] text-gray-400 dark:text-gray-500">Auto-refreshes every 15s</p>
              </div>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ selectedEmails.length }} selected
              </span>
            </div>

            <div v-if="loading" class="p-5 text-sm text-gray-500 dark:text-gray-400">
              Loading recipients...
            </div>

            <div v-else-if="recipients.length === 0" class="p-5 text-sm text-gray-500 dark:text-gray-400">
              No recipients found.
            </div>

            <div v-else class="overflow-x-auto">
              <table class="w-full text-left">
                <thead>
                  <tr class="border-b border-gray-200 dark:border-gray-800">
                    <th class="w-10 px-5 py-3">
                      <input
                        type="checkbox"
                        :checked="allSelected"
                        @change="toggleSelectAll"
                        class="w-4 h-4 rounded border-gray-300 dark:border-gray-700"
                      />
                    </th>
                    <th class="px-5 py-3 text-xs font-medium text-gray-500 dark:text-gray-400">ID</th>
                    <th class="px-5 py-3 text-xs font-medium text-gray-500 dark:text-gray-400">Email</th>
                    <th class="px-5 py-3 text-xs font-medium text-gray-500 dark:text-gray-400">Source</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in recipients"
                    :key="item.source + '-' + item.id"
                    class="border-b border-gray-100 last:border-0 dark:border-gray-800 transition-colors"
                    :class="newlyArrived.has(item.email.toLowerCase()) ? 'bg-yellow-50 dark:bg-yellow-500/10' : ''"
                  >
                    <td class="px-5 py-3">
                      <input
                        type="checkbox"
                        :value="item.email"
                        v-model="selectedEmails"
                        class="w-4 h-4 rounded border-gray-300 dark:border-gray-700"
                      />
                    </td>
                    <td class="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{{ item.id }}</td>
                    <td class="px-5 py-3 text-sm text-gray-700 dark:text-gray-300">{{ item.email }}</td>
                    <td class="px-5 py-3 text-xs text-gray-500 dark:text-gray-400 capitalize">{{ item.source }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- RIGHT: MESSAGE + SEND -->
          <div class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] h-fit">
            <h3 class="mb-4 font-semibold text-gray-800 dark:text-white/90">Compose Message</h3>

            <label class="block mb-1 text-xs text-gray-500 dark:text-gray-400">Subject</label>
            <input
              v-model="subject"
              type="text"
              placeholder="Subject"
              class="w-full mb-4 rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-transparent dark:text-white/90"
            />

            <label class="block mb-1 text-xs text-gray-500 dark:text-gray-400">Message</label>
            <textarea
              v-model="message"
              rows="8"
              placeholder="Type your message..."
              class="w-full mb-4 rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-transparent dark:text-white/90"
            ></textarea>

            <button
              @click="sendInvite"
              :disabled="sending || selectedEmails.length === 0 || !message.trim()"
              class="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ sending ? "Sending..." : `Send to ${selectedEmails.length} recipient(s)` }}
            </button>

            <p v-if="statusMessage" class="mt-3 text-sm" :class="statusSuccess ? 'text-green-600' : 'text-red-600'">
              {{ statusMessage }}
            </p>
          </div>

        </div>

      </ComponentCard>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Invite");

const recipients = ref([]);
const selectedEmails = ref([]);
const subject = ref("");
const message = ref("");
const loading = ref(true);
const sending = ref(false);
const statusMessage = ref("");
const statusSuccess = ref(false);

const allSelected = computed(() =>
  recipients.value.length > 0 &&
  selectedEmails.value.length === recipients.value.length
);

function toggleSelectAll(e) {
  selectedEmails.value = e.target.checked
    ? recipients.value.map((r) => r.email)
    : [];
}

// Every source we pull emails from.
// idField/emailField let us handle sources whose API returns different
// casing — e.g. /api/experts returns raw DB column names (ID, Email),
// not lowercase like the other sources.
// "Campus Registration" in the sidebar uses the same /api/registrations
// endpoint as "registration" below, so it isn't listed separately here —
// listing it again would just re-add the same rows.
// If "Campus" (Admin) turns out to be a distinct data source with its own
// endpoint, add it here the same way.
const EMAIL_SOURCES = [
  { key: "registration", url: "http://127.0.0.1:5000/api/registrations", idField: "id", emailField: "email" },
  { key: "enquiry", url: "http://127.0.0.1:5000/api/enquiries", idField: "id", emailField: "email" },
  { key: "expertise", url: "http://127.0.0.1:5000/api/experts", idField: "ID", emailField: "Email" },
  { key: "subscriber", url: "http://127.0.0.1:5000/api/subscribers", idField: "id", emailField: "email" },
];

// How often to re-check the sources for new emails, in milliseconds.
const POLL_INTERVAL_MS = 15000;

const newlyArrived = ref(new Set()); // emails added by the most recent poll
let pollTimer = null;

async function fetchRecipients({ isBackgroundPoll = false } = {}) {
  try {
    const results = await Promise.allSettled(
      EMAIL_SOURCES.map((s) => fetch(s.url).then((r) => r.json()))
    );

    const combined = [];

    results.forEach((result, i) => {
      const { key, idField, emailField } = EMAIL_SOURCES[i];

      if (result.status === "rejected") {
        console.error(`Failed to load ${key}:`, result.reason);
        return;
      }

      const data = result.value;
      if (!data || !data.success || !Array.isArray(data.data)) {
        console.error(`Unexpected response shape from ${key}:`, data);
        return;
      }

      data.data
        .filter((r) => r[emailField])
        .forEach((r) => combined.push({ id: r[idField], email: r[emailField], source: key }));
    });

    // de-dupe by email, keeping the first occurrence
    const seen = new Set();
    const deduped = combined.filter((r) => {
      const key = r.email.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });

    if (isBackgroundPoll) {
      const previousEmails = new Set(recipients.value.map((r) => r.email.toLowerCase()));
      const freshlyAdded = deduped.filter((r) => !previousEmails.has(r.email.toLowerCase()));
      newlyArrived.value = new Set(freshlyAdded.map((r) => r.email.toLowerCase()));

      // clear the "new" highlight after a few seconds
      if (freshlyAdded.length > 0) {
        setTimeout(() => {
          newlyArrived.value = new Set();
        }, 5000);
      }
    }

    recipients.value = deduped;
  } catch (error) {
    console.error("Failed to load recipients:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchRecipients();
  pollTimer = setInterval(() => fetchRecipients({ isBackgroundPoll: true }), POLL_INTERVAL_MS);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});

async function sendInvite() {
  sending.value = true;
  statusMessage.value = "";

  try {
    const res = await fetch("http://127.0.0.1:5000/api/invite/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        emails: selectedEmails.value,
        subject: subject.value,
        message: message.value,
      }),
    });

    const data = await res.json();

    if (data.success) {
      statusSuccess.value = true;
      statusMessage.value = `Message sent to ${selectedEmails.value.length} recipient(s).`;
      selectedEmails.value = [];
      subject.value = "";
      message.value = "";
    } else {
      statusSuccess.value = false;
      statusMessage.value = data.message || "Failed to send invite.";
    }
  } catch (error) {
    console.error("Failed to send invite:", error);
    statusSuccess.value = false;
    statusMessage.value = "Something went wrong while sending.";
  } finally {
    sending.value = false;
  }
}
</script>