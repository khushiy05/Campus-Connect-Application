<template>
  <admin-layout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] lg:p-6"
    >
      <h3 class="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-7">Profile</h3>

      <div v-if="loading" class="py-10 text-center text-gray-500 dark:text-gray-400">
        Loading profile...
      </div>
      <div v-else-if="error" class="py-10 text-center text-error-500">
        {{ error }}
      </div>
      <template v-else>
        <profile-card :profile="profile" />
        <personal-info-card :profile="profile" />
      </template>
    </div>
  </admin-layout>
</template>

<script setup>
import AdminLayout from '../../components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import { ref, onMounted } from 'vue'
import ProfileCard from '../../components/profile/ProfileCard.vue'
import PersonalInfoCard from '../../components/profile/PersonalInfoCard.vue'

const currentPageTitle = ref('User Profile')

const profile = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/campus/profile', {
      credentials: 'include',
    })
    const data = await res.json()

    if (data.success) {
      profile.value = data.data
    } else {
      error.value = data.error || 'Failed to load profile.'
    }
  } catch (e) {
    error.value = 'Unable to connect to the server.'
  } finally {
    loading.value = false
  }
})
</script>
