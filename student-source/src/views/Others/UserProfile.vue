<template>
  <admin-layout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="grid grid-cols-1 items-stretch gap-6 lg:grid-cols-2">
      <!-- LEFT HALF: profile -->
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

        <template v-else-if="profile">
          <!-- Add college: only while the student's college is still "Other".
               Disappears after saving, and the other menus unlock. -->
          <div
            v-if="!profile.has_college"
            class="mb-8 rounded-xl border border-warning-200 bg-warning-50 p-5 dark:border-warning-500/30 dark:bg-warning-500/10"
          >
            <h4 class="mb-1 text-base font-semibold text-gray-800 dark:text-white/90">
              Add your college
            </h4>
            <p class="mb-4 text-sm text-gray-600 dark:text-gray-400">
              Choose your college to unlock the rest of the student panel.
            </p>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div class="sm:col-span-2">
                <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                  College Name
                </label>
                <select
                  v-model="form.college_name"
                  @change="form.other_college = ''"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                >
                  <option value="" disabled>
                    {{ colleges.length ? 'Select your college' : 'No colleges available' }}
                  </option>
                  <option v-for="c in colleges" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>

              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                  City (optional)
                </label>
                <input
                  v-model="form.city"
                  type="text"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                />
              </div>

              <div>
                <label class="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                  Not in the list? Type your college
                </label>
                <input
                  v-model="form.other_college"
                  @input="form.college_name = ''"
                  placeholder="Enter your college name"
                  type="text"
                  class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm text-gray-800 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                />
              </div>
            </div>

            <p v-if="saveError" class="mt-3 text-sm text-error-500">{{ saveError }}</p>

            <button
              @click="saveCollege"
              :disabled="saving"
              class="mt-4 rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Save College' }}
            </button>
          </div>

          <!-- Profile details -->
          <div class="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
            <div v-for="f in fields" :key="f.label">
              <p class="mb-1 text-xs text-gray-500 dark:text-gray-400">{{ f.label }}</p>
              <p class="break-words text-sm font-medium text-gray-800 dark:text-white/90">
                {{ f.value || '-' }}
              </p>
            </div>
          </div>
        </template>
      </div>

      <!-- RIGHT HALF: news ticker -->
      <div class="h-full">
        <NewsTicker />
      </div>
    </div>
  </admin-layout>
</template>

<script setup>
import AdminLayout from '../../components/layout/AdminLayout.vue'
import PageBreadcrumb from '@/components/common/PageBreadcrumb.vue'
import NewsTicker from '@/components/NewsTicker.vue'
import { ref, reactive, computed, onMounted } from 'vue'
import { useStudentSession } from '@/composables/useStudentSession'

const API = 'http://127.0.0.1:5000'
const { loadStudentSession } = useStudentSession()

const currentPageTitle = ref('User Profile')

const profile = ref(null)
const loading = ref(true)
const error = ref(null)

const colleges = ref([])
const form = reactive({ college_name: '', other_college: '', city: '' })
const saving = ref(false)
const saveError = ref('')

const fields = computed(() => {
  const p = profile.value || {}
  return [
    { label: 'Name', value: p.name },
    { label: 'Email', value: p.email },
    { label: 'Mobile Number', value: p.mobile },
    { label: 'College', value: p.has_college ? p.college_name : (p.other_college ? `${p.other_college} (not registered yet)` : '') },
    { label: 'City', value: p.city },
    { label: 'Registered On', value: p.registered_on },
  ]
})

async function loadProfile() {
  try {
    const res = await fetch(`${API}/api/student/profile`, { credentials: 'include' })
    const data = await res.json()

    if (data.success) {
      profile.value = data.data
      error.value = null
    } else {
      error.value = data.error || 'Failed to load profile.'
    }
  } catch (e) {
    error.value = 'Unable to connect to the server.'
  }
}

async function loadColleges() {
  try {
    const res = await fetch(`${API}/api/colleges`)
    const data = await res.json()
    colleges.value = data.success ? data.data : []
  } catch (e) {
    colleges.value = []
  }
}

async function saveCollege() {
  saveError.value = ''

  // Typed name (college not in the list) wins over the dropdown.
  const chosen = form.other_college.trim() || form.college_name

  if (!chosen) {
    saveError.value = 'Please choose your college or type its name.'
    return
  }

  saving.value = true
  try {
    const res = await fetch(`${API}/api/student/profile`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ college_name: chosen, city: form.city }),
    })
    const data = await res.json()

    if (data.success) {
      // Reload shared session so the sidebar unlocks the other menus,
      // then refresh this page's data (the form disappears).
      await loadStudentSession(true)
      await loadProfile()
    } else {
      saveError.value = data.error || 'Failed to save college.'
    }
  } catch (e) {
    saveError.value = 'Unable to connect to the server.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadProfile()
  if (profile.value && !profile.value.has_college) {
    await loadColleges()
  }
  loading.value = false
})
</script>