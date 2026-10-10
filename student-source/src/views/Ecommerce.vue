<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12 text-center text-gray-400 dark:text-gray-500 py-12">
        Welcome to your Campus Panel<span v-if="userName">,
          <span class="font-semibold text-indigo-600 dark:text-indigo-400">{{ userName }}</span>!
        </span><span v-else>.</span>
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

onMounted(() => {
  loadUser()

  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>