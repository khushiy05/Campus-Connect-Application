<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">

    <!-- ENQUIRY BOX -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
    >
      <div
        class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl dark:bg-gray-800"
      >
        <svg
          class="fill-gray-800 dark:fill-white/90"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M8.80443 5.60156C7.59109 5.60156 6.60749 6.58517 6.60749 7.79851C6.60749 9.01185 7.59109 9.99545 8.80443 9.99545C10.0178 9.99545 11.0014 9.01185 11.0014 7.79851C11.0014 6.58517 10.0178 5.60156 8.80443 5.60156ZM5.10749 7.79851C5.10749 5.75674 6.76267 4.10156 8.80443 4.10156C10.8462 4.10156 12.5014 5.75674 12.5014 7.79851C12.5014 9.84027 10.8462 11.4955 8.80443 11.4955C6.76267 11.4955 5.10749 9.84027 5.10749 7.79851ZM4.86252 15.3208C4.08769 16.0881 3.70377 17.0608 3.51705 17.8611C3.48384 18.0034 3.5211 18.1175 3.60712 18.2112C3.70161 18.3141 3.86659 18.3987 4.07591 18.3987H13.4249C13.6343 18.3987 13.7992 18.3141 13.8937 18.2112C13.9797 18.1175 14.017 18.0034 13.9838 17.8611C13.7971 17.0608 13.4132 16.0881 12.6383 15.3208C11.8821 14.572 10.6899 13.955 8.75042 13.955C6.81096 13.955 5.61877 14.572 4.86252 15.3208ZM3.8071 14.2549C4.87163 13.2009 6.45602 12.455 8.75042 12.455C11.0448 12.455 12.6292 13.2009 13.6937 14.2549C14.7397 15.2906 15.2207 16.5607 15.4446 17.5202C15.7658 18.8971 14.6071 19.8987 13.4249 19.8987H4.07591C2.89369 19.8987 1.73504 18.8971 2.05628 17.5202C2.28015 16.5607 2.76117 15.2906 3.8071 14.2549ZM15.3042 11.4955C14.4702 11.4955 13.7006 11.2193 13.0821 10.7533C13.3742 10.3314 13.6054 9.86419 13.7632 9.36432C14.1597 9.75463 14.7039 9.99545 15.3042 9.99545C16.5176 9.99545 17.5012 9.01185 17.5012 7.79851C17.5012 6.58517 16.5176 5.60156 15.3042 5.60156C14.7039 5.60156 14.1597 5.84239 13.7632 6.23271C13.6054 5.73284 13.3741 5.26561 13.082 4.84371C13.7006 4.37777 14.4702 4.10156 15.3042 4.10156C17.346 4.10156 19.0012 5.75674 19.0012 7.79851C19.0012 9.84027 17.346 11.4955 15.3042 11.4955ZM19.9248 19.8987H16.3901C16.7014 19.4736 16.9159 18.969 16.9827 18.3987H19.9248C20.1341 18.3987 20.2991 18.3141 20.3936 18.2112C20.4796 18.1175 20.5169 18.0034 20.4837 17.861C20.2969 17.0607 19.913 16.088 19.1382 15.3208C18.4047 14.5945 17.261 13.9921 15.4231 13.9566C15.2232 13.6945 14.9995 13.437 14.7491 13.1891C14.5144 12.9566 14.262 12.7384 13.9916 12.5362C14.3853 12.4831 14.8044 12.4549 15.2503 12.4549C17.5447 12.4549 19.1291 13.2008 20.1936 14.2549C21.2395 15.2906 21.7206 16.5607 21.9444 17.5202C22.2657 18.8971 21.107 19.8987 19.9248 19.8987Z"
            fill=""
          />
        </svg>
      </div>

      <div class="mt-5">
        <span class="text-sm text-gray-500 dark:text-gray-400">Enquiry</span>
        <h4 class="mt-2 font-bold text-gray-800 text-title-sm dark:text-white/90">
          {{ enquiryCount }}
        </h4>
      </div>
    </div>


    <!-- CAMPUS REGISTRATION BOX -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
    >
      <div
        class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl dark:bg-gray-800"
      >
        <svg
          class="fill-gray-800 dark:fill-white/90"
          width="24"
          height="24"
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

      <div class="mt-5">
        <span class="text-sm text-gray-500 dark:text-gray-400">Campus Registration</span>
        <h4 class="mt-2 font-bold text-gray-800 text-title-sm dark:text-white/90">
          {{ registrationCount }}
        </h4>
      </div>
    </div>


    <!-- NEWS BOX -->
    <div
      class="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6"
    >
      <div
        class="flex items-center justify-center w-12 h-12 bg-gray-100 rounded-xl dark:bg-gray-800"
      >
        <!-- News/document icon -->
        <svg
          class="fill-gray-800 dark:fill-white/90"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M5 3.75C5 3.33579 5.33579 3 5.75 3H14.25C14.4489 3 14.6397 3.07902 14.7803 3.21967L18.7803 7.21967C18.921 7.36032 19 7.55109 19 7.75V20.25C19 20.6642 18.6642 21 18.25 21H5.75C5.33579 21 5 20.6642 5 20.25V3.75ZM6.5 4.5V19.5H17.5V8.5H14.25C13.8358 8.5 13.5 8.16421 13.5 7.75V4.5H6.5ZM15 5.56066V7H16.4393L15 5.56066ZM8 12C8 11.5858 8.33579 11.25 8.75 11.25H15.25C15.6642 11.25 16 11.5858 16 12C16 12.4142 15.6642 12.75 15.25 12.75H8.75C8.33579 12.75 8 12.4142 8 12ZM8.75 14.75C8.33579 14.75 8 15.0858 8 15.5C8 15.9142 8.33579 16.25 8.75 16.25H15.25C15.6642 16.25 16 15.9142 16 15.5C16 15.0858 15.6642 14.75 15.25 14.75H8.75Z"
            fill=""
          />
        </svg>
      </div>

      <div class="mt-5">
        <span class="text-sm text-gray-500 dark:text-gray-400">News</span>
        <h4 class="mt-2 font-bold text-gray-800 text-title-sm dark:text-white/90">
          {{ newsCount }}
        </h4>
      </div>
    </div>

  </div>
</template>


<script setup>
import { ref, onMounted } from "vue";

const enquiryCount = ref(0);
const registrationCount = ref(0);
const newsCount = ref(0);

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


    // GET NEWS
    const newsRes = await fetch(
      "http://127.0.0.1:5000/api/news"
    );

    const newsData = await newsRes.json();

    if (newsData.success) {
      newsCount.value = newsData.data.length;
    }

  } catch (error) {
    console.error(
      "Failed to load dashboard counts:",
      error
    );
  }
});
</script>