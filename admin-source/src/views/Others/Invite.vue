<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Invite">

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

          <!-- LEFT: ID / EMAIL LIST -->
          <div class="lg:col-span-2 rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-800">
              <h3 class="font-semibold text-gray-800 dark:text-white/90">Recipients</h3>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ selectedEmails.length }} selected
              </span>
            </div>

            <!-- ADD EMAIL MANUALLY -->
            <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-200 dark:border-gray-800">
              <input
                v-model="manualEmail"
                type="email"
                placeholder="Add an email not in the list..."
                @keyup.enter="addManualEmail"
                class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-transparent dark:text-white/90"
              />
              <button
                @click="addManualEmail"
                :disabled="!manualEmail.trim()"
                class="rounded-lg bg-gray-800 px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-900 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/10 dark:hover:bg-white/20"
              >
                Add
              </button>
            </div>
            <p v-if="manualEmailError" class="px-5 pb-2 text-xs text-red-600">{{ manualEmailError }}</p>

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
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in recipients"
                    :key="item.id"
                    class="border-b border-gray-100 last:border-0 dark:border-gray-800"
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
import { ref, computed, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Invite");

const recipients = ref([]);
const selectedEmails = ref([]);
const manualEmail = ref("");
const manualEmailError = ref("");
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

function addManualEmail() {
  const email = manualEmail.value.trim();
  manualEmailError.value = "";

  if (!email) return;

  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!isValid) {
    manualEmailError.value = "Enter a valid email address.";
    return;
  }

  if (recipients.value.some((r) => r.email === email)) {
    manualEmailError.value = "That email is already in the list.";
    return;
  }

  recipients.value.push({ id: "manual", email });
  selectedEmails.value.push(email); // auto-select it since you just added it to invite
  manualEmail.value = "";
}

function toggleSelectAll(e) {
  selectedEmails.value = e.target.checked
    ? recipients.value.map((r) => r.email)
    : [];
}

onMounted(async () => {
  try {
    // Adjust this endpoint if your ID/email list should come from
    // /api/enquiries instead of /api/registrations
    const res = await fetch("http://127.0.0.1:5000/api/registrations");
    const data = await res.json();

    if (data.success) {
      recipients.value = data.data
        .filter((r) => r.email) // skip rows with no email
        .map((r) => ({ id: r.id, email: r.email }));
    }
  } catch (error) {
    console.error("Failed to load recipients:", error);
  } finally {
    loading.value = false;
  }
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