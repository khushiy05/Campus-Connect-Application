<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div
      class="grid h-[calc(100vh-13rem)] min-h-[480px] grid-cols-1 overflow-hidden rounded-2xl border border-gray-200 bg-white lg:grid-cols-[1fr_280px] dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <!-- LEFT: inbox + composer -->
      <section class="flex min-h-0 flex-col">
        <div
          class="flex items-center justify-between border-b border-gray-200 px-5 py-3 dark:border-gray-800"
        >
          <span
            class="rounded-lg border border-gray-300 px-4 py-1.5 text-sm font-semibold tracking-wide text-gray-800 dark:border-gray-700 dark:text-white/90"
          >
            INBOX
          </span>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ messages.length }} messages
          </span>
        </div>

        <div ref="messageList" class="flex-1 space-y-3 overflow-y-auto px-5 py-4">
          <p
            v-if="!messages.length"
            class="py-10 text-center text-sm text-gray-400"
          >
            No messages yet. Say hi!
          </p>

          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex"
            :class="isMine(msg) ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[80%] rounded-xl border px-4 py-2.5"
              :class="[
                isMine(msg)
                  ? 'border-brand-500 bg-brand-500 text-white'
                  : 'border-gray-200 bg-gray-50 text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-white/90',
                repliedToMe(msg) ? 'ring-2 ring-amber-400' : '',
              ]"
            >
              <p
                v-if="repliedToMe(msg)"
                class="mb-1 text-[11px] font-semibold text-amber-600 dark:text-amber-400"
              >
                ↩ Replied to your message
              </p>

              <p
                class="mb-1 text-xs font-semibold"
                :class="isMine(msg) ? 'text-white/80' : 'text-brand-500'"
              >
                {{ isMine(msg) ? "You" : msg.sender }}
              </p>

              <!-- Quoted message -->
              <div
                v-if="msg.replyTo"
                class="mb-1.5 border-l-2 pl-2 text-xs opacity-80"
                :class="isMine(msg) ? 'border-white/60' : 'border-gray-400'"
              >
                <span class="font-semibold">
                  {{ msg.replyTo.senderId === me?.id ? "You" : msg.replyTo.sender }}:
                </span>
                {{ msg.replyTo.text }}
              </div>

              <p class="text-sm break-words whitespace-pre-wrap">{{ msg.text }}</p>

              <div class="mt-1.5 flex items-center justify-between gap-4">
                <span
                  class="text-[11px]"
                  :class="isMine(msg) ? 'text-white/70' : 'text-gray-400'"
                >
                  {{ formatTime(msg.time) }}
                </span>
                <button
                  v-if="!isMine(msg)"
                  type="button"
                  class="bg-brand-500 hover:bg-brand-600 rounded-md px-3 py-1 text-xs font-medium text-white transition"
                  @click="startReply(msg)"
                >
                  REPLY
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Composer -->
        <div class="border-t border-gray-200 p-4 dark:border-gray-800">
          <div
            v-if="replyingTo"
            class="mb-2 flex items-center justify-between rounded-lg bg-gray-100 px-3 py-2 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-300"
          >
            <span class="truncate">
              Replying to <b>{{ replyingTo.sender }}</b
              >: {{ replyingTo.text }}
            </span>
            <button
              type="button"
              class="ml-3 text-base leading-none hover:text-red-500"
              @click="replyingTo = null"
            >
              ×
            </button>
          </div>

          <div
            class="flex items-end gap-3 rounded-xl border border-gray-300 p-2 dark:border-gray-700"
          >
            <textarea
              ref="inputBox"
              v-model="draft"
              rows="2"
              placeholder="Your message"
              class="flex-1 resize-none bg-transparent px-2 py-1 text-sm text-gray-800 outline-none placeholder:text-gray-400 dark:text-white/90"
              @keydown.enter.exact.prevent="sendMessage"
            ></textarea>
            <button
              type="button"
              :disabled="!draft.trim()"
              class="bg-brand-500 hover:bg-brand-600 rounded-lg px-5 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
              @click="sendMessage"
            >
              SEND
            </button>
          </div>
        </div>
      </section>

      <!-- RIGHT: students currently logged in -->
      <aside
        class="hidden min-h-0 flex-col border-l border-gray-200 lg:flex dark:border-gray-800"
      >
        <div
          class="border-b border-gray-200 px-5 py-3 text-sm font-semibold text-gray-800 dark:border-gray-800 dark:text-white/90"
        >
          Online students
          <span class="ml-1 text-xs font-normal text-gray-500">({{ onlineStudents.length }})</span>
        </div>

        <ul class="flex-1 space-y-1 overflow-y-auto p-3">
          <li
            v-for="s in onlineStudents"
            :key="s.id"
            class="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            <div class="relative">
              <div
                class="bg-brand-500 flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white"
              >
                {{ initials(s.name) }}
              </div>
              <span
                class="absolute right-0 bottom-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-green-500 dark:border-gray-900"
              ></span>
            </div>
            <span class="truncate text-sm text-gray-700 dark:text-gray-300">
              {{ s.name }}<span v-if="s.id === me?.id" class="text-gray-400"> (You)</span>
            </span>
          </li>
        </ul>
      </aside>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("Chatbook");

// Same Flask server (:5000) and same session cookie your other student pages use
const API = "http://127.0.0.1:5000/api/chatbook";
const POLL_MS = 3000;

const me = ref(null);
const onlineStudents = ref([]);
const messages = ref([]);
const draft = ref("");
const replyingTo = ref(null);
const messageList = ref(null);
const inputBox = ref(null);

let lastId = 0;
let timer = null;
let syncing = false;

const isMine = (msg) => msg.senderId === me.value?.id;
const repliedToMe = (msg) =>
  !isMine(msg) && msg.replyTo && msg.replyTo.senderId === me.value?.id;

const initials = (name) =>
  (name || "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");

const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const isNearBottom = () => {
  const el = messageList.value;
  if (!el) return true;
  return el.scrollHeight - el.scrollTop - el.clientHeight < 120;
};

const scrollToBottom = async () => {
  await nextTick();
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight;
  }
};

const sync = async () => {
  if (syncing) return;
  syncing = true;
  try {
    const res = await fetch(`${API}/sync?after_id=${lastId}`, {
      credentials: "include",
    });
    if (!res.ok) return;
    const data = await res.json();
    if (!data.success) return;

    me.value = data.me;
    onlineStudents.value = data.online;

    if (data.messages.length) {
      const stick = isNearBottom();
      const hasMine = data.messages.some((m) => m.senderId === data.me.id);
      messages.value.push(...data.messages);
      lastId = data.messages[data.messages.length - 1].id;
      if (stick || hasMine) scrollToBottom();
    }
  } catch (err) {
    console.error("Chatbook sync failed:", err);
  } finally {
    syncing = false;
  }
};

const startReply = (msg) => {
  replyingTo.value = { id: msg.id, sender: msg.sender, text: msg.text };
  inputBox.value?.focus();
};

const sendMessage = async () => {
  const text = draft.value.trim();
  if (!text) return;

  const body = { text, reply_to_id: replyingTo.value?.id ?? null };
  draft.value = "";
  replyingTo.value = null;

  try {
    await fetch(`${API}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });
    await sync();
  } catch (err) {
    console.error("Send failed:", err);
  }
};

onMounted(async () => {
  await sync();
  scrollToBottom();
  timer = setInterval(sync, POLL_MS);
});

onBeforeUnmount(() => clearInterval(timer));
</script>