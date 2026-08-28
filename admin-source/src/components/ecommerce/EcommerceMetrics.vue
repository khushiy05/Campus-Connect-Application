<template>
  <div class="grid grid-cols-2 gap-4 sm:max-w-md">

    <!-- ENQUIRY BOX -->
    <div
      class="h-[150px] rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <div
        class="flex items-center justify-center w-9 h-9 bg-gray-100 rounded-lg dark:bg-gray-800"
      >
        <!-- Enquiry icon -->
        <svg
          class="fill-gray-800 dark:fill-white/90"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M8.80443 5.60156C7.59109 5.60156 6.60749 6.58517 6.60749 7.79851C6.60749 9.01185 7.59109 9.99545 8.80443 9.99545C10.0178 9.99545 11.0014 9.01185 11.0014 7.79851C11.0014 6.58517 10.0178 5.60156 8.80443 5.60156ZM5.10749 7.79851C5.10749 5.75674 6.76267 4.10156 8.80443 4.10156C10.8462 4.10156 12.5014 5.75674 12.5014 7.79851C12.5014 9.84027 10.8462 11.4955 8.80443 11.4955C6.76267 11.4955 5.10749 9.84027 5.10749 7.79851Z"
            fill=""
          />
        </svg>
      </div>

      <div class="flex items-end justify-between mt-3">
        <div>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            Enquiry
          </span>

          <h4 class="mt-1 font-bold text-gray-800 text-lg dark:text-white/90">
            {{ enquiryCount }}
          </h4>
        </div>

        <span
          class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
          :class="enquiryChange >= 0
            ? 'bg-green-50 text-green-600 dark:bg-green-500/15 dark:text-green-400'
            : 'bg-red-50 text-red-600 dark:bg-red-500/15 dark:text-red-400'"
        >
          <svg v-if="enquiryChange >= 0" class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 5l7 7-1.4 1.4L13 8.8V19h-2V8.8l-4.6 4.6L5 12z" fill="currentColor" />
          </svg>
          <svg v-else class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 19l-7-7 1.4-1.4L11 15.2V5h2v10.2l4.6-4.6L19 12z" fill="currentColor" />
          </svg>
          {{ Math.abs(enquiryChange) }}%
        </span>
      </div>
    </div>


    <!-- CAMPUS REGISTRATION BOX -->
    <div
      class="h-[150px] rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]"
    >
      <div
        class="flex items-center justify-center w-9 h-9 bg-gray-100 rounded-lg dark:bg-gray-800"
      >
        <!-- Registration icon -->
        <svg
          class="fill-gray-800 dark:fill-white/90"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M11.665 3.75621C11.8762 3.65064 12.1247 3.65064 12.3358 3.75621L18.7807 6.97856L12.3358 10.2009C12.1247 10.3065 11.8762 10.3065 11.665 10.2009L5.22014 6.97856L11.665 3.75621ZM4.29297 8.19203V16.0946C4.29297 16.3787 4.45347 16.6384 4.70757 16.7654L11.25 20.0366V11.6513C11.1631 11.6205 11.0777 11.5843 10.9942 11.5426L4.29297 8.19203ZM12.75 20.037L19.2933 16.7654C19.5474 16.6384 19.7079 16.3787 19.7079 16.0946V8.19202L13.0066 11.5426C12.9229 11.5844 12.8377 11.6208 12.75 11.6516V20.037Z"
            fill=""
          />
        </svg>
      </div>

      <div class="flex items-end justify-between mt-3">
        <div>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            Campus Registration
          </span>

          <h4 class="mt-1 font-bold text-gray-800 text-lg dark:text-white/90">
            {{ registrationCount }}
          </h4>
        </div>

        <span
          class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
          :class="registrationChange >= 0
            ? 'bg-green-50 text-green-600 dark:bg-green-500/15 dark:text-green-400'
            : 'bg-red-50 text-red-600 dark:bg-red-500/15 dark:text-red-400'"
        >
          <svg v-if="registrationChange >= 0" class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 5l7 7-1.4 1.4L13 8.8V19h-2V8.8l-4.6 4.6L5 12z" fill="currentColor" />
          </svg>
          <svg v-else class="w-3 h-3" viewBox="0 0 24 24" fill="none">
            <path d="M12 19l-7-7 1.4-1.4L11 15.2V5h2v10.2l4.6-4.6L19 12z" fill="currentColor" />
          </svg>
          {{ Math.abs(registrationChange) }}%
        </span>
      </div>
    </div>

  </div>
</template>


<script setup>
import { ref, onMounted } from "vue";

const enquiryCount = ref(0);
const registrationCount = ref(0);

// Placeholder % change values — replace with real data from your API when available
const enquiryChange = ref(11.01);
const registrationChange = ref(-9.05);

onMounted(async () => {
  try {

    // GET ENQUIRIES
    const enquiryRes = await fetch(
      "http://127.0.0.1:5000/api/enquiries"
    );

    const enquiryData = await enquiryRes.json();

    if (enquiryData.success) {
      enquiryCount.value = enquiryData.data.length;
    }


    // GET CAMPUS REGISTRATIONS
    const registrationRes = await fetch(
      "http://127.0.0.1:5000/api/registrations"
    );

    const registrationData = await registrationRes.json();

    if (registrationData.success) {
      registrationCount.value = registrationData.data.length;
    }

  } catch (error) {
    console.error(
      "Failed to load dashboard counts:",
      error
    );
  }
});
</script>