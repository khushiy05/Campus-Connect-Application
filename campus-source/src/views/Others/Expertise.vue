<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Add Expertise">
        <form @submit.prevent="submitForm" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Name</label>
            <input v-model="form.name" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Email</label>
            <input v-model="form.email" type="email" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Mobile</label>
            <input v-model="form.mobile" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div class="relative">
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">City</label>
            <input
              v-model="citySearch"
              @input="onCityInput"
              @focus="showCityDropdown = true"
              @blur="hideCityDropdown"
              required
              autocomplete="off"
              placeholder="Select your city"
              class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm"
            />
            <div
              v-if="showCityDropdown"
              class="absolute z-20 mt-1 w-full max-h-72 overflow-y-auto rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg"
            >
              <template v-for="group in filteredCityGroups" :key="group.state">
                <div class="sticky top-0 px-3 py-2 text-sm font-semibold bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-gray-100 border-b border-gray-100 dark:border-gray-700">
                  {{ group.state }}
                </div>
                <div
                  v-for="c in group.cities"
                  :key="c"
                  @mousedown.prevent="pickCity(c)"
                  class="px-5 py-2 text-sm cursor-pointer hover:bg-orange-50 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300"
                >
                  {{ c }}
                </div>
              </template>
              <div v-if="filteredCityGroups.length === 0" class="px-3 py-3 text-sm text-gray-400">
                No cities found
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Domain</label>
            <select v-model="form.domain_select" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm">
              <option value="">Select domain</option>
              <option>Web Development</option>
              <option>AI/ML</option>
              <option>Data Science</option>
              <option>UI/UX Design</option>
              <option value="Other">Other (type below)</option>
            </select>
          </div>
          <div v-if="form.domain_select === 'Other'">
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Specify Domain</label>
            <input v-model="form.domain_other" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">LinkedIn URL</label>
            <input v-model="form.linkedin" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Photo</label>
            <input type="file" @change="onPhotoChange" accept=".jpg,.jpeg,.png" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>

          <div class="sm:col-span-2 border-t border-gray-100 dark:border-gray-800 pt-4 mt-1">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">Plan Details</p>
          </div>

          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Plan</label>
            <select v-model="form.plan_type" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm">
              <option>Yearly</option>
            </select>
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Amount</label>
            <input :value="form.amount" readonly class="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Transaction ID</label>
            <input v-model="form.transaction_id" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Registration Date</label>
            <input v-model="form.payment_date" type="date" required class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-1 text-gray-700 dark:text-gray-300">Expiry Date</label>
            <input v-model="form.expiry_date" type="date" readonly class="w-full rounded-md border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 dark:text-gray-200 px-3 py-2 text-sm" />
          </div>

<div class="sm:col-span-2 flex gap-3">
            <button type="submit" class="px-5 py-2 rounded-md bg-orange-500 text-white text-sm font-medium hover:bg-orange-600">
              Submit
            </button>
            <button type="button" @click="showTable = !showTable" class="px-5 py-2 rounded-md bg-gray-700 text-white text-sm font-medium hover:bg-gray-800">
              {{ showTable ? "Hide" : "Show" }}
            </button>
          </div>
        </form>
      </ComponentCard>

      <ComponentCard v-if="showTable" title="Submitted Experts">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-gray-100 dark:border-gray-800">
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Photo</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Name</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Domain</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">City</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Plan</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Amount</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Expiry</th>
                <th class="px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in experts" :key="e.ID" class="border-b border-gray-100 dark:border-gray-800">
                <td class="px-4 py-3">
                  <img v-if="e.Photo" :src="`http://127.0.0.1:5000/static/uploads/experts/${e.Photo}`" class="w-8 h-8 rounded-full object-cover" />
                </td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.Name }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.Domain }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.City }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.PlanType }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.Amount }}</td>
                <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{{ e.ExpiryDate }}</td>
                <td class="px-4 py-3">
                  <button
                    @click="deleteExpert(e.ID)"
                    :disabled="deletingId === e.ID"
                    class="text-error-500 hover:text-error-600 text-sm font-medium disabled:opacity-50"
                    >
                    {{ deletingId === e.ID ? "Deleting..." : "Delete" }}
                    </button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="experts.length === 0" class="py-10 text-center text-gray-500 dark:text-gray-400">
            No experts yet.
          </div>
        </div>
      </ComponentCard>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Expertise");
const API_BASE = "http://127.0.0.1:5000";

const form = ref({
  name: "", email: "", mobile: "", city: "",
  domain_select: "", domain_other: "", linkedin: "",
  plan_type: "Yearly", amount: 1200,
  transaction_id: "", payment_date: "", expiry_date: ""
});
const photoFile = ref(null);
const experts = ref([]);
const showTable = ref(false);
const deletingId = ref(null);

// ---- City dropdown state (grouped by state) ----
const citiesByState = ref({});   // raw { "State Name": ["City1", "City2", ...], ... } from /api/cities
const citySearch = ref("");      // text shown in the City input
const showCityDropdown = ref(false);

// Groups shown in the dropdown, filtered by whatever's typed in citySearch.
// - No search text: show every state with all of its cities.
// - Search text: keep a state's group if the state name matches, OR keep
//   just the matching cities within a state whose name doesn't match.
const filteredCityGroups = computed(() => {
  const query = citySearch.value.trim().toLowerCase();
  const states = Object.keys(citiesByState.value).sort();

  return states
    .map((state) => {
      const cities = citiesByState.value[state] || [];
      if (!query) return { state, cities };

      if (state.toLowerCase().includes(query)) {
        return { state, cities };
      }
      const matchingCities = cities.filter((c) => c.toLowerCase().includes(query));
      return matchingCities.length ? { state, cities: matchingCities } : null;
    })
    .filter(Boolean);
});

watch(() => form.value.payment_date, (newDate) => {
  if (newDate) {
    const d = new Date(newDate);
    d.setFullYear(d.getFullYear() + 1);
    form.value.expiry_date = d.toISOString().split("T")[0];
  }
});

function onPhotoChange(e) {
  photoFile.value = e.target.files[0];
}

async function fetchExperts() {
  const res = await fetch(`${API_BASE}/api/experts`);
  const data = await res.json();
  if (data.success) experts.value = data.data;
}

// ---- City dropdown logic ----
async function fetchCities() {
  try {
    const res = await fetch(`${API_BASE}/api/cities`);
    const data = await res.json();
    // /api/cities returns cities grouped by state, e.g. { "Andhra Pradesh": ["Adilabad", "Anantapur", ...], ... }
    citiesByState.value = data;
  } catch (e) {
    console.error("Failed to load cities:", e);
  }
}

function onCityInput() {
  form.value.city = citySearch.value; // keep the submitted value in sync with what's typed
  showCityDropdown.value = true;
}

function pickCity(city) {
  citySearch.value = city;
  form.value.city = city;
  showCityDropdown.value = false;
}

function hideCityDropdown() {
  // small delay so the @mousedown on a suggestion fires before the list is hidden
  setTimeout(() => (showCityDropdown.value = false), 150);
}

async function submitForm() {
  const fd = new FormData();
  Object.entries(form.value).forEach(([key, val]) => fd.append(key, val));
  if (photoFile.value) fd.append("photo", photoFile.value);

  const res = await fetch(`${API_BASE}/api/experts`, { method: "POST", body: fd });
  const data = await res.json();

  if (data.success) {
    alert("Expert added");
    form.value = {
      name: "", email: "", mobile: "", city: "",
      domain_select: "", domain_other: "", linkedin: "",
      plan_type: "Yearly", amount: 1200,
      transaction_id: "", payment_date: "", expiry_date: ""
    };
    citySearch.value = "";
    showCityDropdown.value = false;
    photoFile.value = null;
    fetchExperts();
  } else {
    alert(data.error || "Something went wrong");
  }
}

async function deleteExpert(id) {
  if (!confirm("Are you sure you want to delete this expert?")) return;

  deletingId.value = id;
  try {
    const res = await fetch(`${API_BASE}/api/experts/${id}`, { method: "DELETE" });
    const data = await res.json();

    if (data.success) {
      experts.value = experts.value.filter((e) => e.ID !== id);
    } else {
      alert(data.error || "Failed to delete expert.");
    }
  } catch (e) {
    alert("Unable to connect to the server.");
  } finally {
    deletingId.value = null;
  }
}

onMounted(() => {
  fetchExperts();
  fetchCities();
});
</script>