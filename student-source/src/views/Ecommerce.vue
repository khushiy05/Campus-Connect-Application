<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">

      <div class="col-span-12 text-center text-gray-400 dark:text-gray-500 py-12">
        Welcome to your Campus Panel,
        <span class="font-semibold text-indigo-600 dark:text-indigo-400">{{ userName }}</span>!
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '../components/layout/AdminLayout.vue'

const userName = ref('Student')

const loadUserName = () => {
  const keys = ['user', 'userData', 'student', 'currentUser']
  for (const key of keys) {
    try {
      const raw = localStorage.getItem(key)
      if (!raw) continue
      const user = JSON.parse(raw)
      const name =
        user?.name ||
        user?.full_name ||
        user?.fullName ||
        [user?.first_name, user?.last_name].filter(Boolean).join(' ') ||
        user?.username
      if (name) {
        userName.value = name
        return
      }
    } catch (e) {
      // not JSON, try the next key
    }
  }

  // Some apps store the name as a plain string
  const plain = localStorage.getItem('userName') || localStorage.getItem('name')
  if (plain) userName.value = plain
}

onMounted(() => {
  loadUserName()

  history.pushState(null, null, location.href)

  window.addEventListener('popstate', () => {
    history.pushState(null, null, location.href)
  })
})
</script>