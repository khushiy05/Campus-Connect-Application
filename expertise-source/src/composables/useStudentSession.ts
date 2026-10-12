import { ref } from 'vue'

const API = 'http://127.0.0.1:5000'

const loaded = ref(false)
const loggedIn = ref(false)
const hasCollege = ref(false)
const name = ref('')
const email = ref('')
const collegeName = ref('')

let inflight: Promise<void> | null = null

export function loadStudentSession(force = false): Promise<void> {
  if (loaded.value && !force) return Promise.resolve()
  if (inflight) return inflight

  inflight = (async () => {
    try {
      const res = await fetch(`${API}/api/student/session`, { credentials: 'include' })
      const data = await res.json()

      const ok = !!(data.success && data.logged_in && data.approved && !data.blocked)
      loggedIn.value = ok
      hasCollege.value = ok && !!data.has_college
      name.value = ok ? data.name || '' : ''
      email.value = ok ? data.email || '' : ''
      collegeName.value = ok ? data.college_name || '' : ''
    } catch (e) {
      loggedIn.value = false
      hasCollege.value = false
    } finally {
      loaded.value = true
      inflight = null
    }
  })()

  return inflight
}

export function useStudentSession() {
  return { loaded, loggedIn, hasCollege, name, email, collegeName, loadStudentSession }
}