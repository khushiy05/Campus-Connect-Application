<template>
  <div class="news-card">
    <h5 class="news-title">📢 Events 2026</h5>
    <p class="news-sub">Latest announcements and upcoming events.</p>

    <div class="news-wrap" ref="wrapRef">
      <div v-if="loading" class="news-msg">Loading updates...</div>
      <div v-else-if="error" class="news-msg">Could not load updates.</div>
      <div v-else-if="!items.length" class="news-msg">No updates yet.</div>

      <div
        v-else
        ref="trackRef"
        class="news-track"
        :class="{ scrolling }"
        :style="{ '--dur': duration + 's' }"
      >
        <div
          v-for="(n, i) in displayItems"
          :key="i"
          class="news-item"
          :aria-hidden="i >= items.length"
        >
          <a
            v-if="n.FilePath"
            :href="`${API_BASE}/static/uploads/news/${encodeURIComponent(n.FilePath)}`"
            target="_blank"
            rel="noopener"
            class="news-link"
          >📢 {{ n.Title }}</a>
          <span v-else class="news-head">📢 {{ n.Title }}</span>
          <span v-if="n.Description" class="news-desc">{{ n.Description }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const API_BASE = 'http://127.0.0.1:5000'
const SPEED = 35 // px per second, higher = faster

const items = ref([])
const loading = ref(true)
const error = ref(false)
const scrolling = ref(false)
const duration = ref(30)
const wrapRef = ref(null)
const trackRef = ref(null)

// Doubled list = seamless loop (animation moves -50%)
const displayItems = computed(() =>
  scrolling.value ? [...items.value, ...items.value] : items.value
)

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/api/news`)
    const result = await res.json()
    items.value = result.success ? result.data : []
  } catch (e) {
    console.error('Failed to load news:', e)
    error.value = true
  } finally {
    loading.value = false
  }

  await nextTick()
  if (trackRef.value && wrapRef.value) {
    const h = trackRef.value.scrollHeight
    if (h > wrapRef.value.clientHeight) {
      duration.value = h / SPEED
      scrolling.value = true
    }
  }
})
</script>

<style scoped>
.news-card {
  border: 1px solid rgba(128, 128, 128, 0.25);
  border-radius: 12px;
  padding: 24px;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.news-title { margin: 0 0 4px; font-size: 18px; font-weight: 600; }
.news-sub { margin: 0 0 12px; font-size: 13px; opacity: 0.7; }

.news-wrap {
  flex: 1 1 0;
  min-height: 360px;
  overflow: hidden;
  position: relative;
  border-top: 1px solid rgba(128, 128, 128, 0.25);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 6%, #000 94%, transparent 100%);
          mask-image: linear-gradient(to bottom, transparent 0, #000 6%, #000 94%, transparent 100%);
}
.news-msg { padding: 16px 0; opacity: 0.6; font-size: 14px; }

.news-track { will-change: transform; }
.news-track.scrolling { animation: news-scroll var(--dur, 30s) linear infinite; }
.news-wrap:hover .news-track.scrolling { animation-play-state: paused; }

.news-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(128, 128, 128, 0.15);
  font-size: 14px;
}
.news-head, .news-link { font-weight: 500; }
.news-link { color: inherit; text-decoration: underline; }
.news-desc { display: block; margin-top: 2px; font-size: 12px; opacity: 0.7; }

@keyframes news-scroll {
  from { transform: translateY(0); }
  to   { transform: translateY(-50%); }
}
@media (prefers-reduced-motion: reduce) {
  .news-track.scrolling { animation: none; }
  .news-wrap { overflow-y: auto; }
}
</style>