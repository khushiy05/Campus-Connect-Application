<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12 text-sm text-gray-500 dark:text-gray-400">
        Welcome to your Campus Panel<span v-if="userName">,
          <span class="font-semibold text-indigo-600 dark:text-indigo-400">{{ userName }}</span>!
        </span><span v-else>.</span>
      </div>

      <router-link
        v-for="card in cards"
        :key="card.label"
        :to="card.to"
        class="col-span-12 sm:col-span-6 lg:col-span-4 xl:col-span-3 rounded-2xl border border-gray-200 bg-white p-5 transition hover:shadow-md dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
      >
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-800">
          <svg
            class="h-6 w-6 text-gray-800 dark:text-white/90"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path v-for="(d, i) in card.icon" :key="i" :d="d" />
          </svg>
        </div>

        <div class="mt-5">
          <span class="text-sm text-gray-500 dark:text-gray-400">{{ card.label }}</span>
          <h4 class="mt-2 text-3xl font-bold text-gray-800 dark:text-white/90">
            {{ card.count }}
          </h4>
        </div>
      </router-link>

    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'

const API_BASE = 'http://127.0.0.1:5000'
const CACHE_KEY = 'student_cache'

const readCachedName = () => {
  try {
    return JSON.parse(sessionStorage.getItem(CACHE_KEY))?.name || ''
  } catch {
    return ''
  }
}

const userName = ref(readCachedName()) // shows instantly on refresh

// Adjust `to` paths to match student-source/src/router/index.js
const cards = ref([
  {
    label: 'Services',
    count: 0,
    to: '/services',
    icon: ['M3 7h18v13H3z', 'M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2', 'M3 13h18'],
  },
  {
    label: 'RojgarSetu',
    count: 0,
    to: '/rojgarsetu',
    icon: ['M3 3h18v18H3z', 'M3 9h18', 'M3 15h18', 'M9 3v18', 'M15 3v18'],
  },
  {
    label: 'Expertise',
    count: 0,
    to: '/expertise',
    icon: ['M22 9 12 4 2 9l10 5 10-5z', 'M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5'],
  },
  {
    label: 'Review',
    count: 0,
    to: '/review',
    icon: ['m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z'],
  },
])

const loadUser = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/student/session`, {
      credentials: 'include',
    })
    const data = await res.json()
    if (data.success && data.logged_in) {
      userName.value = data.name || ''
    }
  } catch (error) {
    console.error('Failed to load student session:', error)
  }
}

const loadCounts = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/student/dashboard-counts`, {
      credentials: 'include',
    })
    if (!res.ok) return
    const data = await res.json()
    cards.value[0].count = data.services ?? 0
    cards.value[1].count = data.rojgarsetu ?? 0
    cards.value[2].count = data.expertise ?? 0
    cards.value[3].count = data.review ?? 0
  } catch (error) {
    console.error('Failed to load dashboard counts:', error)
  }
}

onMounted(() => {
  loadUser()
  loadCounts()

  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>