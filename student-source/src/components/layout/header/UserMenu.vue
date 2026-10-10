<template>
  <div class="relative" ref="dropdownRef">
    <button
      class="flex items-center text-gray-700 dark:text-gray-400"
      @click.prevent="toggleDropdown"
    >
      <span class="mr-3 flex h-11 w-11 items-center justify-center overflow-hidden rounded-full bg-indigo-600 text-white">
        <img v-if="avatar" :src="avatar" alt="User" class="h-full w-full object-cover" />
        <span v-else class="text-lg font-semibold">{{ initial }}</span>
      </span>

      <span class="block mr-1 font-medium text-theme-sm">{{ displayName }}</span>

      <svg
        :class="{ 'rotate-180': dropdownOpen }"
        class="transition-transform duration-200"
        width="18" height="20" viewBox="0 0 18 20" fill="none"
      >
        <path d="M4.3125 8.65625L9 13.3437L13.6875 8.65625"
          stroke="currentColor" stroke-width="1.5"
          stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div
      v-if="dropdownOpen"
      class="absolute right-0 mt-[17px] w-[260px] rounded-2xl border border-gray-200 bg-white p-3 shadow-lg dark:border-gray-800 dark:bg-gray-dark"
    >
      <div class="px-2 pb-2">
        <span class="block font-medium text-gray-700 text-theme-sm dark:text-gray-400">{{ displayName }}</span>
        <span class="mt-0.5 block text-theme-xs text-gray-500 dark:text-gray-400">{{ email }}</span>
      </div>

      <router-link
        to="/profile"
        @click="closeDropdown"
        class="block rounded-lg px-3 py-2 text-theme-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-white/5"
      >
        Profile
      </router-link>

      <button
        @click="signOut"
        class="mt-1 block w-full rounded-lg px-3 py-2 text-left text-theme-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-white/5"
      >
        Sign out
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const API_BASE = 'http://127.0.0.1:5000'
const CACHE_KEY = 'student_cache'

const readCache = () => {
  try {
    return JSON.parse(sessionStorage.getItem(CACHE_KEY)) || {}
  } catch {
    return {}
  }
}

const dropdownOpen = ref(false)
const dropdownRef = ref(null)
const user = ref(readCache()) // starts with cached name, so no flash on refresh
const loaded = ref(false)

// Loads the logged-in student from the Flask session cookie
const loadUser = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/student/session`, {
      credentials: 'include',
    })
    const data = await res.json()

    if (data.success && data.logged_in) {
      user.value = { name: data.name, email: data.email, photo: data.photo }
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(user.value))
    } else {
      user.value = {}
      sessionStorage.removeItem(CACHE_KEY)
    }
  } catch (error) {
    console.error('Failed to load student session:', error)
  } finally {
    loaded.value = true
  }
}

// "Student" only appears if the fetch finished and no name exists
const displayName = computed(() => user.value.name || (loaded.value ? 'Student' : ''))
const email = computed(() => user.value.email || '')
const avatar = computed(() => user.value.photo || '')
const initial = computed(() => displayName.value.charAt(0).toUpperCase())

const toggleDropdown = () => (dropdownOpen.value = !dropdownOpen.value)
const closeDropdown = () => (dropdownOpen.value = false)

const signOut = async () => {
  try {
    await fetch(`${API_BASE}/api/logout`, {
      method: 'POST',
      credentials: 'include',
    })
  } catch (error) {
    console.error('Logout request failed:', error)
  }
  localStorage.removeItem('user')
  localStorage.removeItem('student')
  localStorage.removeItem('token')
  sessionStorage.clear()
  window.location.href = `${API_BASE}/`
}

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) closeDropdown()
}

onMounted(() => {
  loadUser()
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>