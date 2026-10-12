<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div
      class="grid h-[calc(100vh-13rem)] min-h-[480px] grid-cols-1 overflow-hidden rounded-2xl border border-gray-200 bg-white lg:grid-cols-[1fr_280px] dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <!-- LEFT -->
      <section class="flex min-h-0 flex-col">
        <!-- Tabs -->
        <div
          class="flex items-center gap-2 border-b border-gray-200 px-5 py-3 dark:border-gray-800"
        >
          <button
            type="button"
            class="rounded-lg border px-4 py-1.5 text-sm font-semibold tracking-wide transition"
            :class="
              tab === 'chat'
                ? 'border-brand-500 bg-brand-500 text-white'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-white/90 dark:hover:bg-white/5'
            "
            @click="tab = 'chat'"
          >
            CHAT
          </button>

          <button
            type="button"
            class="relative rounded-lg border px-4 py-1.5 text-sm font-semibold tracking-wide transition"
            :class="
              tab === 'inbox'
                ? 'border-brand-500 bg-brand-500 text-white'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-white/90 dark:hover:bg-white/5'
            "
            @click="tab = 'inbox'"
          >
            INBOX
            <span
              v-if="totalUnread > 0 && tab !== 'inbox'"
              class="absolute -top-2 -right-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[11px] font-bold text-white"
            >
              {{ totalUnread }}
            </span>
          </button>

          <span class="ml-auto text-xs text-gray-500 dark:text-gray-400">
            {{ tab === "chat" ? `${chatMessages.length} messages` : `${convos.length} chats` }}
          </span>
        </div>

        <!-- CHAT (Meet style) -->
        <div
          v-show="tab === 'chat'"
          ref="messageList"
          class="flex-1 space-y-1 overflow-y-auto px-4 py-3"
        >
          <p v-if="!chatMessages.length" class="py-10 text-center text-sm text-gray-400">
            No messages yet. Say hi!
          </p>

          <div
            v-for="msg in chatMessages"
            :key="msg.id"
            class="group rounded-lg px-3 py-2 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            <div class="flex items-baseline gap-2">
              <span
                class="text-sm font-semibold"
                :class="isMine(msg) ? 'text-gray-900 dark:text-white' : 'text-brand-500'"
              >
                {{ isMine(msg) ? "You" : msg.sender }}
              </span>
              <span class="text-[11px] text-gray-400">{{ formatTime(msg.time) }}</span>

              <button
                v-if="!isMine(msg)"
                type="button"
                class="text-brand-500 ml-auto text-xs font-semibold opacity-0 transition group-hover:opacity-100 focus:opacity-100"
                @click="openThread(msg.senderId, msg.sender, msg)"
              >
                REPLY
              </button>
            </div>

            <p class="text-sm break-words whitespace-pre-wrap text-gray-800 dark:text-white/90">
              {{ msg.text }}
            </p>
          </div>
        </div>

        <!-- CHAT composer -->
        <div
          v-show="tab === 'chat'"
          class="border-t border-gray-200 p-4 dark:border-gray-800"
        >
          <div
            class="flex items-end gap-3 rounded-xl border border-gray-300 p-2 dark:border-gray-700"
          >
            <textarea
              v-model="draft"
              rows="2"
              placeholder="Your message"
              class="flex-1 resize-none bg-transparent px-2 py-1 text-sm text-gray-800 outline-none placeholder:text-gray-400 dark:text-white/90"
              @keydown.enter.exact.prevent="sendChat"
            ></textarea>
            <button
              type="button"
              :disabled="!draft.trim()"
              class="bg-brand-500 hover:bg-brand-600 rounded-lg px-5 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
              @click="sendChat"
            >
              SEND
            </button>
          </div>
        </div>

        <!-- INBOX (WhatsApp style) -->
        <div v-show="tab === 'inbox'" class="flex min-h-0 flex-1 flex-col">
          <!-- Conversation list -->
          <div v-if="!activeConvo" class="flex-1 overflow-y-auto">
            <p v-if="!convos.length" class="py-10 text-center text-sm text-gray-400">
              No conversations yet. When someone replies to your message, they show up here.
            </p>

            <button
              v-for="c in convos"
              :key="c.id"
              type="button"
              class="flex w-full items-center gap-3 border-b border-gray-100 px-5 py-3 text-left hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-white/5"
              @click="openThread(c.id, c.name)"
            >
              <div
                class="bg-brand-500 flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white"
              >
                {{ initials(c.name) }}
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-baseline justify-between gap-2">
                  <span class="truncate text-sm font-semibold text-gray-800 dark:text-white/90">
                    {{ c.name }}
                  </span>
                  <span class="shrink-0 text-[11px] text-gray-400">
                    {{ formatTime(c.last.time) }}
                  </span>
                </div>
                <div class="flex items-center justify-between gap-2">
                  <p class="truncate text-xs text-gray-500 dark:text-gray-400">
                    <span v-if="c.last.senderId === me?.id">You: </span>{{ c.last.text }}
                  </p>
                  <span
                    v-if="c.unread > 0"
                    class="bg-brand-500 flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full px-1.5 text-[11px] font-bold text-white"
                  >
                    {{ c.unread }}
                  </span>
                </div>
              </div>
            </button>
          </div>

          <!-- Open conversation -->
          <template v-else>
            <div
              class="flex items-center gap-3 border-b border-gray-200 px-4 py-2.5 dark:border-gray-800"
            >
              <button
                type="button"
                class="rounded-full px-2 py-1 text-lg leading-none text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/10"
                @click="closeThread"
              >
                ←
              </button>
              <div class="relative">
                <div
                  class="bg-brand-500 flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold text-white"
                >
                  {{ initials(activeConvo.name) }}
                </div>
                <span
                  v-if="isOnline(activeConvo.id)"
                  class="absolute right-0 bottom-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-green-500 dark:border-gray-900"
                ></span>
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-800 dark:text-white/90">
                  {{ activeConvo.name }}
                </p>
                <p class="text-[11px] text-gray-400">
                  {{ isOnline(activeConvo.id) ? "online" : "offline" }}
                </p>
              </div>
            </div>

            <div
              ref="threadList"
              class="flex-1 space-y-2 overflow-y-auto bg-gray-50 px-5 py-4 dark:bg-transparent"
            >
              <p
                v-if="!activeConvo.messages.length && !pendingTarget"
                class="py-10 text-center text-sm text-gray-400"
              >
                No messages yet.
              </p>

              <div
                v-for="m in activeConvo.messages"
                :key="m.id"
                class="flex"
                :class="isMine(m) ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[75%] rounded-2xl px-3.5 py-2"
                  :class="
                    isMine(m)
                      ? 'bg-brand-500 rounded-br-sm text-white'
                      : 'rounded-bl-sm border border-gray-200 bg-white text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-white/90'
                  "
                >
                  <!-- Original chat message this conversation started from -->
                  <div
                    v-if="originalOf(m)"
                    class="mb-1.5 rounded-md border-l-2 px-2 py-1 text-xs"
                    :class="
                      isMine(m)
                        ? 'border-white/70 bg-white/15 text-white/90'
                        : 'border-gray-400 bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-300'
                    "
                  >
                    <span class="font-semibold">
                      {{ originalOf(m).senderId === me?.id ? "You" : originalOf(m).sender }}
                    </span>
                    <br />
                    {{ originalOf(m).text }}
                  </div>

                  <p class="text-sm break-words whitespace-pre-wrap">{{ m.text }}</p>
                  <p
                    class="mt-0.5 text-right text-[10px]"
                    :class="isMine(m) ? 'text-white/70' : 'text-gray-400'"
                  >
                    {{ formatTime(m.time) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Thread composer -->
            <div class="border-t border-gray-200 p-4 dark:border-gray-800">
              <div
                v-if="pendingTarget"
                class="mb-2 flex items-center justify-between rounded-lg bg-gray-100 px-3 py-2 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-300"
              >
                <span class="truncate">
                  Replying to <b>{{ pendingTarget.sender }}</b
                  >: {{ pendingTarget.text }}
                </span>
                <button
                  type="button"
                  class="ml-3 text-base leading-none hover:text-red-500"
                  @click="pendingTarget = null"
                >
                  ×
                </button>
              </div>

              <div
                class="flex items-end gap-3 rounded-xl border border-gray-300 p-2 dark:border-gray-700"
              >
                <textarea
                  ref="threadInput"
                  v-model="threadDraft"
                  rows="2"
                  :placeholder="`Message ${activeConvo.name}`"
                  class="flex-1 resize-none bg-transparent px-2 py-1 text-sm text-gray-800 outline-none placeholder:text-gray-400 dark:text-white/90"
                  @keydown.enter.exact.prevent="sendThread"
                ></textarea>
                <button
                  type="button"
                  :disabled="!threadDraft.trim()"
                  class="bg-brand-500 hover:bg-brand-600 rounded-lg px-5 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
                  @click="sendThread"
                >
                  SEND
                </button>
              </div>
            </div>
          </template>
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
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("Chatbook");

const API = "http://127.0.0.1:5000/api/chatbook";
const POLL_MS = 3000;

const tab = ref("chat");
const me = ref(null);
const onlineStudents = ref([]);
const messages = ref([]);

const draft = ref("");
const threadDraft = ref("");
const messageList = ref(null);
const threadList = ref(null);
const threadInput = ref(null);

const activeId = ref(null);
const activeName = ref("");
const pendingTarget = ref(null);
const readMap = ref({});

let lastId = 0;
let timer = null;
let syncing = false;

const isMine = (msg) => msg.senderId === me.value?.id;
const isOnline = (id) => onlineStudents.value.some((s) => s.id === id);

// CHAT = only normal (non-reply) messages
const chatMessages = computed(() => messages.value.filter((m) => !m.replyTo));

// Private conversations: one per person, built from replies between me and them
const convos = computed(() => {
  const myId = me.value?.id;
  if (!myId) return [];

  const map = new Map();
  for (const m of messages.value) {
    if (!m.replyTo) continue;

    let otherId;
    let otherName;
    if (m.senderId === myId && m.replyTo.senderId !== myId) {
      otherId = m.replyTo.senderId;
      otherName = m.replyTo.sender;
    } else if (m.replyTo.senderId === myId && m.senderId !== myId) {
      otherId = m.senderId;
      otherName = m.sender;
    } else {
      continue;
    }

    if (!map.has(otherId)) map.set(otherId, { id: otherId, name: otherName, messages: [] });
    map.get(otherId).messages.push(m);
  }

  return [...map.values()]
    .map((c) => {
      const last = c.messages[c.messages.length - 1];
      const readId = readMap.value[c.id] || 0;
      const unread = c.messages.filter((m) => m.senderId === c.id && m.id > readId).length;
      return { ...c, last, unread };
    })
    .sort((a, b) => b.last.id - a.last.id);
});

const totalUnread = computed(() => convos.value.reduce((n, c) => n + c.unread, 0));

const activeConvo = computed(() => {
  if (activeId.value === null) return null;
  return (
    convos.value.find((c) => c.id === activeId.value) || {
      id: activeId.value,
      name: activeName.value,
      messages: [],
      last: null,
      unread: 0,
    }
  );
});

// If a reply was made to a normal chat message, show that message as a quote
const originalOf = (m) => {
  const parent = messages.value.find((p) => p.id === m.replyTo?.id);
  return parent && !parent.replyTo ? parent : null;
};

const readKey = () => `chatbook_read_${me.value?.id}`;

const markRead = () => {
  if (tab.value !== "inbox" || !activeConvo.value || !activeConvo.value.messages.length) return;
  const newest = Math.max(...activeConvo.value.messages.map((m) => m.id));
  if ((readMap.value[activeId.value] || 0) >= newest) return;
  readMap.value = { ...readMap.value, [activeId.value]: newest };
  try {
    localStorage.setItem(readKey(), JSON.stringify(readMap.value));
  } catch {}
};

watch([tab, activeId, convos], markRead);

watch(tab, (t) => {
  if (t === "chat") scrollToBottom();
  if (t === "inbox" && activeId.value !== null) scrollThread();
});

watch(
  () => activeConvo.value?.messages.length,
  () => scrollThread()
);

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
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight;
};

const scrollThread = async () => {
  await nextTick();
  if (threadList.value) threadList.value.scrollTop = threadList.value.scrollHeight;
};

const sync = async () => {
  if (syncing) return;
  syncing = true;
  try {
    const res = await fetch(`${API}/sync?after_id=${lastId}`, { credentials: "include" });
    if (!res.ok) return;
    const data = await res.json();
    if (!data.success) return;

    const firstLoad = !me.value;
    me.value = data.me;
    onlineStudents.value = data.online;

    if (firstLoad) {
      try {
        readMap.value = JSON.parse(localStorage.getItem(readKey()) || "{}");
      } catch {
        readMap.value = {};
      }
    }

    if (data.messages.length) {
      const stick = isNearBottom();
      const hasMine = data.messages.some((m) => m.senderId === data.me.id && !m.replyTo);
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

const post = async (text, replyToId) => {
  await fetch(`${API}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ text, reply_to_id: replyToId ?? null }),
  });
  await sync();
};

// Normal message in the CHAT tab
const sendChat = async () => {
  const text = draft.value.trim();
  if (!text) return;
  draft.value = "";
  try {
    await post(text, null);
  } catch (err) {
    console.error("Send failed:", err);
  }
};

// Open a conversation (from the inbox list, or from REPLY on a chat message)
const openThread = (otherId, name, target = null) => {
  activeId.value = otherId;
  activeName.value = name;
  pendingTarget.value = target
    ? { id: target.id, sender: target.sender, text: target.text }
    : null;
  threadDraft.value = "";
  tab.value = "inbox";
  scrollThread();
  nextTick(() => threadInput.value?.focus());
};

const closeThread = () => {
  activeId.value = null;
  pendingTarget.value = null;
  threadDraft.value = "";
};

// Message inside a conversation
const sendThread = async () => {
  const text = threadDraft.value.trim();
  const c = activeConvo.value;
  if (!text || !c) return;

  // Which of THEIR messages are we answering? (this is what routes it to their inbox)
  let replyToId = pendingTarget.value?.id;
  if (!replyToId) {
    const theirs = [...c.messages].reverse().find((m) => m.senderId === c.id);
    const mineLast = [...c.messages].reverse().find((m) => m.senderId === me.value?.id);
    replyToId = theirs?.id ?? mineLast?.replyTo?.id;
  }
  if (!replyToId) return;

  threadDraft.value = "";
  pendingTarget.value = null;
  try {
    await post(text, replyToId);
    scrollThread();
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