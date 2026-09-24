<template>
  <div>
    <div class="p-5 mb-6 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="w-full">
          <h4 class="text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-6">
            Personal Information
          </h4>

          <p v-if="message" class="mb-4 text-sm text-green-600">{{ message }}</p>

          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-7 2xl:gap-x-32">
            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">Name</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.name }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">Email address</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.email }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">Mobile</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.mobile }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">City</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.city }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">College Name</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.college_name }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">College Code</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">{{ current.college_code }}</p>
            </div>

            <div>
              <p class="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">Password</p>
              <p class="text-sm font-medium text-gray-800 dark:text-white/90">••••••••</p>
            </div>
          </div>
        </div>

        <div class="flex gap-3">
          <button class="edit-button" @click="openProfileModal">Edit</button>
          <button class="edit-button" @click="openPasswordModal">Change password</button>
        </div>
      </div>
    </div>

    <!-- Edit mobile + city -->
    <Modal v-if="isProfileInfoModal" @close="isProfileInfoModal = false">
      <template #body>
        <div
          class="no-scrollbar relative w-full max-w-[700px] overflow-y-auto rounded-3xl bg-white p-4 dark:bg-gray-900 lg:p-11"
        >
          <button
            @click="isProfileInfoModal = false"
            class="transition-color absolute right-5 top-5 z-999 flex h-11 w-11 items-center justify-center rounded-full bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600 dark:bg-gray-700 dark:bg-white/[0.05] dark:text-gray-400 dark:hover:bg-white/[0.07] dark:hover:text-gray-300"
          >
            <svg class="fill-current" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M6.04289 16.5418C5.65237 16.9323 5.65237 17.5655 6.04289 17.956C6.43342 18.3465 7.06658 18.3465 7.45711 17.956L11.9987 13.4144L16.5408 17.9565C16.9313 18.347 17.5645 18.347 17.955 17.9565C18.3455 17.566 18.3455 16.9328 17.955 16.5423L13.4129 12.0002L17.955 7.45808C18.3455 7.06756 18.3455 6.43439 17.955 6.04387C17.5645 5.65335 16.9313 5.65335 16.5408 6.04387L11.9987 10.586L7.45711 6.04439C7.06658 5.65386 6.43342 5.65386 6.04289 6.04439C5.65237 6.43491 5.65237 7.06808 6.04289 7.4586L10.5845 12.0002L6.04289 16.5418Z"
                fill=""
              />
            </svg>
          </button>

          <div class="px-2 pr-14">
            <h4 class="mb-2 text-2xl font-semibold text-gray-800 dark:text-white/90">
              Edit Personal Information
            </h4>
            <p class="mb-6 text-sm text-gray-500 dark:text-gray-400 lg:mb-7">
              You can update your mobile number and city.
            </p>
          </div>

          <form class="flex flex-col" @submit.prevent="saveProfile">
            <div class="grid grid-cols-1 gap-x-6 gap-y-5 p-2 lg:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Mobile</label>
                <input v-model="form.mobile" type="text" :class="inputClass" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">City</label>
                <input v-model="form.city" type="text" :class="inputClass" />
              </div>
            </div>

            <p v-if="error" class="px-2 mt-3 text-sm text-red-600">{{ error }}</p>

            <div class="flex items-center gap-3 px-2 mt-6 lg:justify-end">
              <button
                @click="isProfileInfoModal = false"
                type="button"
                class="flex w-full justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] sm:w-auto"
              >
                Close
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="flex w-full justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 sm:w-auto"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>

    <!-- Change password -->
    <Modal v-if="isPasswordModal" @close="isPasswordModal = false">
      <template #body>
        <div
          class="no-scrollbar relative w-full max-w-[500px] overflow-y-auto rounded-3xl bg-white p-4 dark:bg-gray-900 lg:p-11"
        >
          <button
            @click="isPasswordModal = false"
            class="transition-color absolute right-5 top-5 z-999 flex h-11 w-11 items-center justify-center rounded-full bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600 dark:bg-gray-700 dark:bg-white/[0.05] dark:text-gray-400 dark:hover:bg-white/[0.07] dark:hover:text-gray-300"
          >
            <svg class="fill-current" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M6.04289 16.5418C5.65237 16.9323 5.65237 17.5655 6.04289 17.956C6.43342 18.3465 7.06658 18.3465 7.45711 17.956L11.9987 13.4144L16.5408 17.9565C16.9313 18.347 17.5645 18.347 17.955 17.9565C18.3455 17.566 18.3455 16.9328 17.955 16.5423L13.4129 12.0002L17.955 7.45808C18.3455 7.06756 18.3455 6.43439 17.955 6.04387C17.5645 5.65335 16.9313 5.65335 16.5408 6.04387L11.9987 10.586L7.45711 6.04439C7.06658 5.65386 6.43342 5.65386 6.04289 6.04439C5.65237 6.43491 5.65237 7.06808 6.04289 7.4586L10.5845 12.0002L6.04289 16.5418Z"
                fill=""
              />
            </svg>
          </button>

          <div class="px-2 pr-14">
            <h4 class="mb-6 text-2xl font-semibold text-gray-800 dark:text-white/90">Change Password</h4>
          </div>

          <form class="flex flex-col gap-5 p-2" @submit.prevent="savePassword">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Current password</label>
              <input v-model="pwd.current_password" type="password" :class="inputClass" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">New password</label>
              <input v-model="pwd.new_password" type="password" placeholder="Minimum 6 characters" :class="inputClass" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Confirm new password</label>
              <input v-model="pwd.confirm" type="password" :class="inputClass" />
            </div>

            <p v-if="pwdError" class="text-sm text-red-600">{{ pwdError }}</p>

            <div class="flex items-center gap-3 mt-2 lg:justify-end">
              <button
                @click="isPasswordModal = false"
                type="button"
                class="flex w-full justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] sm:w-auto"
              >
                Close
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="flex w-full justify-center rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 sm:w-auto"
              >
                {{ saving ? 'Updating...' : 'Update Password' }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Modal from './Modal.vue'

const props = defineProps({
  profile: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['updated'])

const inputClass =
  'dark:bg-dark-900 h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent bg-none px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800'

// Local copy so the card updates immediately after saving
const current = ref({ ...props.profile })
watch(
  () => props.profile,
  (p) => {
    current.value = { ...p }
  },
  { deep: true },
)

const isProfileInfoModal = ref(false)
const isPasswordModal = ref(false)
const saving = ref(false)
const message = ref('')
const error = ref('')
const pwdError = ref('')

const form = ref({ mobile: '', city: '' })
const pwd = ref({ current_password: '', new_password: '', confirm: '' })

const openProfileModal = () => {
  form.value = { mobile: current.value.mobile || '', city: current.value.city || '' }
  error.value = ''
  isProfileInfoModal.value = true
}

const openPasswordModal = () => {
  pwd.value = { current_password: '', new_password: '', confirm: '' }
  pwdError.value = ''
  isPasswordModal.value = true
}

const saveProfile = async () => {
  error.value = ''
  saving.value = true
  try {
    const res = await fetch('/api/campus/profile', {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const json = await res.json()
    if (json.success) {
      current.value = { ...current.value, mobile: form.value.mobile, city: form.value.city }
      isProfileInfoModal.value = false
      message.value = 'Profile updated successfully.'
      emit('updated')
    } else {
      error.value = json.error || 'Could not update profile.'
    }
  } catch (e) {
    error.value = 'Unable to reach the server.'
  } finally {
    saving.value = false
  }
}

const savePassword = async () => {
  pwdError.value = ''
  if (pwd.value.new_password !== pwd.value.confirm) {
    pwdError.value = 'New passwords do not match.'
    return
  }
  saving.value = true
  try {
    const res = await fetch('/api/campus/password', {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: pwd.value.current_password,
        new_password: pwd.value.new_password,
      }),
    })
    const json = await res.json()
    if (json.success) {
      isPasswordModal.value = false
      message.value = 'Password changed successfully.'
    } else {
      pwdError.value = json.error || 'Could not change password.'
    }
  } catch (e) {
    pwdError.value = 'Unable to reach the server.'
  } finally {
    saving.value = false
  }
}
</script>
