<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12 text-sm text-gray-500 dark:text-gray-400">
        Welcome to your Student Panel<span v-if="userName">,
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

      <!-- UrbanWash animated button -->
      <div class="col-span-12 flex justify-center mt-6">
        <button class="urban-btn" @click="openUrbanWash">
          <span class="urban-btn__icon">🧺</span>
          <span class="urban-btn__text">
            <strong>UrbanWash</strong>
            <small>FRESHNESS AT YOUR DOORSTEP.</small>
          </span>
          <span class="urban-btn__arrow">→</span>
        </button>
      </div>

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

const openUrbanWash = () => {
  // TODO: set destination
  // router.push('/urbanwash')  or  window.open('https://your-link', '_blank')
}

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

<style scoped>
.urban-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 16px 28px;
  border: none;
  border-radius: 16px;
  color: #fff;
  cursor: pointer;
  overflow: hidden;
  background: linear-gradient(120deg, #465fff, #06b6d4, #465fff);
  background-size: 200% 200%;
  animation: urbanGradient 5s ease infinite, urbanPulse 2.5s ease-in-out infinite;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.urban-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -75%;
  width: 50%;
  height: 100%;
  background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.55), transparent);
  transform: skewX(-25deg);
  animation: urbanShine 3s infinite;
}
.urban-btn:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 14px 30px rgba(70, 95, 255, 0.45);
}
.urban-btn:active { transform: scale(0.97); }
.urban-btn__icon { font-size: 28px; animation: urbanBounce 2s ease-in-out infinite; }
.urban-btn__text { display: flex; flex-direction: column; text-align: left; line-height: 1.2; }
.urban-btn__text strong { font-size: 20px; letter-spacing: 0.5px; }
.urban-btn__text small { font-size: 11px; letter-spacing: 1.5px; opacity: 0.9; }
.urban-btn__arrow { font-size: 22px; transition: transform 0.25s ease; }
.urban-btn:hover .urban-btn__arrow { transform: translateX(6px); }

@keyframes urbanGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes urbanPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(70, 95, 255, 0.5); }
  50% { box-shadow: 0 0 0 14px rgba(70, 95, 255, 0); }
}
@keyframes urbanShine {
  0% { left: -75%; }
  60%, 100% { left: 125%; }
}
@keyframes urbanBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
</style>