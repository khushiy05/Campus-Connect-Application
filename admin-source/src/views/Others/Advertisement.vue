<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Advertisement">
        <form @submit.prevent="handleSubmit" class="p-6">
          <h3 class="mb-6 text-lg font-semibold text-gray-800 dark:text-white/90">
            Add Advertisement
          </h3>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Name
              </label>
              <input
                v-model="form.name"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="Enter name"
                required
              />
            </div>

            <!-- Email -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <input
                v-model="form.email"
                type="email"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="Enter email"
                required
              />
            </div>

            <!-- Mobile -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Mobile
              </label>
              <input
                v-model="form.mobile"
                type="tel"
                maxlength="10"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                placeholder="Enter mobile number"
                required
              />
            </div>

            <!-- Logo Upload -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Logo
              </label>
              <input
                ref="logoInput"
                type="file"
                accept="image/*"
                @change="handleLogoUpload"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2 text-sm text-gray-800 file:mr-4 file:rounded-md file:border-0 file:bg-brand-500 file:px-3 file:py-1.5 file:text-sm file:text-white hover:file:bg-brand-600 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
              />
            </div>
          </div>

          <div class="my-6 border-t border-gray-200 dark:border-gray-800"></div>

          <h4 class="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">
            Plan Details
          </h4>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Cost (fixed) -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Cost
              </label>
              <input
                :value="form.cost"
                type="text"
                disabled
                class="h-11 w-full cursor-not-allowed rounded-lg border border-gray-300 bg-gray-100 px-4 py-2.5 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
              />
            </div>

            <!-- Duration (fixed) -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Duration
              </label>
              <input
                :value="form.duration"
                type="text"
                disabled
                class="h-11 w-full cursor-not-allowed rounded-lg border border-gray-300 bg-gray-100 px-4 py-2.5 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
              />
            </div>

            <!-- Registration Date (admin picks) -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Registration Date
              </label>
              <input
                v-model="form.registrationDate"
                type="date"
                class="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
                required
              />
            </div>

            <!-- Expiry Date (auto, derived from Registration Date) -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Expiry Date
              </label>
              <input
                :value="expiryDateDisplay"
                type="text"
                disabled
                class="h-11 w-full cursor-not-allowed rounded-lg border border-gray-300 bg-gray-100 px-4 py-2.5 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
                placeholder="Auto-calculated"
              />
            </div>
          </div>

          <div class="mt-6 flex gap-3">
            <button
              type="submit"
              class="rounded-lg bg-orange-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-orange-600"
            >
              Submit
            </button>
            <button
              type="button"
              @click="showList = !showList"
              class="rounded-lg bg-gray-800 px-6 py-2.5 text-sm font-medium text-white hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600"
            >
              Show
            </button>
          </div>
        </form>

        <!-- Show list table -->
        <div v-if="showList" class="border-t border-gray-200 p-6 dark:border-gray-800">
          <div v-if="advertisements.length === 0" class="py-6 text-center text-gray-500 dark:text-gray-400">
            No advertisements added yet.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="border-b border-gray-200 text-gray-600 dark:border-gray-800 dark:text-gray-300">
                  <th class="py-2 pr-4">Name</th>
                  <th class="py-2 pr-4">Email</th>
                  <th class="py-2 pr-4">Mobile</th>
                  <th class="py-2 pr-4">Logo</th>
                  <th class="py-2 pr-4">Cost</th>
                  <th class="py-2 pr-4">Duration</th>
                  <th class="py-2 pr-4">Reg. Date</th>
                  <th class="py-2 pr-4">Expiry Date</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(ad, index) in advertisements"
                  :key="index"
                  class="border-b border-gray-100 text-gray-700 dark:border-gray-800 dark:text-gray-300"
                >
                  <td class="py-2 pr-4">{{ ad.name }}</td>
                  <td class="py-2 pr-4">{{ ad.email }}</td>
                  <td class="py-2 pr-4">{{ ad.mobile }}</td>
                  <td class="py-2 pr-4">
                    <img
                      v-if="ad.logoPreview"
                      :src="ad.logoPreview"
                      alt="logo"
                      class="h-8 w-8 rounded object-cover"
                    />
                    <span v-else>—</span>
                  </td>
                  <td class="py-2 pr-4">{{ ad.cost }}</td>
                  <td class="py-2 pr-4">{{ ad.duration }}</td>
                  <td class="py-2 pr-4">{{ ad.registrationDateDisplay }}</td>
                  <td class="py-2 pr-4">{{ ad.expiryDateDisplay }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </ComponentCard>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Advertisement");

// Format a Date object as dd-mm-yyyy
const formatDate = (date) => {
  const dd = String(date.getDate()).padStart(2, "0");
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const yyyy = date.getFullYear();
  return `${dd}-${mm}-${yyyy}`;
};

const form = ref({
  name: "",
  email: "",
  mobile: "",
  cost: 1200,
  duration: "6 Months",
  registrationDate: "", // yyyy-mm-dd from <input type="date">
  logoFile: null,
  logoPreview: null,
});

// Auto-calculate expiry = registrationDate + 6 months
const expiryDateDisplay = computed(() => {
  if (!form.value.registrationDate) return "";
  const regDate = new Date(form.value.registrationDate);
  const expiry = new Date(regDate);
  expiry.setMonth(expiry.getMonth() + 6);
  return formatDate(expiry);
});

const logoInput = ref(null);
const advertisements = ref([]);
const showList = ref(false);

const handleLogoUpload = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  form.value.logoFile = file;
  form.value.logoPreview = URL.createObjectURL(file);
};

const resetForm = () => {
  form.value.name = "";
  form.value.email = "";
  form.value.mobile = "";
  form.value.registrationDate = "";
  form.value.logoFile = null;
  form.value.logoPreview = null;
  if (logoInput.value) logoInput.value.value = "";
};

const handleSubmit = async () => {
  const regDateFormatted = formatDate(new Date(form.value.registrationDate));

  // Build multipart payload for file upload + fields
  const payload = new FormData();
  payload.append("name", form.value.name);
  payload.append("email", form.value.email);
  payload.append("mobile", form.value.mobile);
  payload.append("cost", form.value.cost);
  payload.append("duration", form.value.duration);
  payload.append("registrationDate", form.value.registrationDate); // yyyy-mm-dd, best for SQL DATE column
  payload.append("expiryDate", computeExpiryISO(form.value.registrationDate)); // yyyy-mm-dd
  if (form.value.logoFile) payload.append("logo", form.value.logoFile);

  try {
    // Replace with your actual API endpoint that inserts into the SQL Server table
    const res = await fetch("/api/advertisements", {
      method: "POST",
      body: payload,
    });
    if (!res.ok) throw new Error("Failed to save advertisement");
    const saved = await res.json();

    advertisements.value.push({
      name: form.value.name,
      email: form.value.email,
      mobile: form.value.mobile,
      logoPreview: form.value.logoPreview,
      cost: form.value.cost,
      duration: form.value.duration,
      registrationDateDisplay: regDateFormatted,
      expiryDateDisplay: expiryDateDisplay.value,
    });

    resetForm();
  } catch (err) {
    console.error(err);
    alert("Something went wrong while saving. Please try again.");
  }
};

// Returns yyyy-mm-dd expiry, for sending to backend in ISO/SQL-friendly format
const computeExpiryISO = (registrationDateStr) => {
  const regDate = new Date(registrationDateStr);
  const expiry = new Date(regDate);
  expiry.setMonth(expiry.getMonth() + 6);
  return expiry.toISOString().split("T")[0];
};
</script>