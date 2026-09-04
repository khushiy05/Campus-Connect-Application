<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="space-y-5 sm:space-y-6">
      <ComponentCard title="Internship">
        <div class="p-6">
          <h4 class="mb-6 text-lg font-semibold text-gray-800 dark:text-white/90">
            Add Internship
          </h4>

          <form @submit.prevent="submitForm" class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">

            <!-- Company Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Company
              </label>
              <input
                v-model="form.company"
                type="text"
                placeholder="Enter company name"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
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
                placeholder="Enter email"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
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
                placeholder="Enter mobile number"
                required
                pattern="[0-9]{10}"
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              />
            </div>

            <!-- Company Type -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Company Type
              </label>
              <select
                v-model="form.companyType"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              >
                <option value="" disabled>Select company type</option>
                <option v-for="type in companyTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>

            <!-- Internship Duration -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Internship Duration
              </label>
              <select
                v-model="form.duration"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              >
                <option value="" disabled>Select duration</option>
                <option v-for="d in durations" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>

            <!-- Stipend -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Stipend
              </label>
              <select
                v-model="form.stipend"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              >
                <option value="" disabled>Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>

            <!-- Application Link -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Application Link
              </label>
              <input
                v-model="form.link"
                type="url"
                placeholder="https://example.com/apply"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              />
            </div>

            <!-- City (searchable) -->
            <!--
              NOTE: `required` was removed from this input on purpose.
              It's bound to `citySearch` (the visible text), not `form.location`
              (the actual value we submit). Validating the wrong variable let
              the browser silently block submission. We now validate
              `form.location` explicitly inside submitForm() instead.
            -->
            <div class="relative" ref="cityFieldRef">
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                City
              </label>
              <input
                v-model="citySearch"
                type="text"
                autocomplete="off"
                placeholder="Select your city"
                @focus="cityDropdownOpen = true"
                @input="cityDropdownOpen = true"
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white placeholder:text-gray-400"
              />

              <div
                v-if="cityDropdownOpen"
                class="absolute z-20 mt-1 w-full max-h-72 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900"
              >
                <template v-for="state in filteredCityStates" :key="state.name">
                  <div
                    v-if="state.cities.length"
                    class="border-b border-gray-100 bg-gray-50 px-4 py-2 text-sm font-bold text-gray-700 dark:border-gray-800 dark:bg-gray-800 dark:text-gray-200"
                  >
                    {{ state.name }}
                  </div>
                  <div
                    v-for="city in state.cities"
                    :key="city"
                    @mousedown.prevent="selectCity(city)"
                    class="cursor-pointer border-b border-gray-50 px-6 py-2.5 text-sm text-gray-600 hover:bg-orange-50 dark:border-gray-800 dark:text-gray-300 dark:hover:bg-gray-800"
                  >
                    {{ city }}
                  </div>
                </template>

                <div v-if="!filteredCityStates.some(s => s.cities.length)" class="px-4 py-3 text-sm text-gray-400">
                  No matching cities
                </div>
              </div>
            </div>

            <!-- Branch (searchable) -->
            <!-- Same fix as City: `required` removed, validated in JS instead. -->
            <div class="relative md:col-span-2" ref="branchFieldRef">
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Branch
              </label>
              <input
                v-model="branchSearch"
                type="text"
                autocomplete="off"
                placeholder="Select or search branch"
                @focus="branchDropdownOpen = true"
                @input="branchDropdownOpen = true"
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white placeholder:text-gray-400"
              />

              <div
                v-if="branchDropdownOpen"
                class="absolute z-20 mt-1 w-full max-h-72 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900"
              >
                <div
                  v-for="branch in filteredBranches"
                  :key="branch"
                  @mousedown.prevent="selectBranch(branch)"
                  class="cursor-pointer border-b border-gray-50 px-4 py-2.5 text-sm text-gray-600 hover:bg-orange-50 dark:border-gray-800 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                  {{ branch }}
                </div>

                <div v-if="!filteredBranches.length" class="px-4 py-3 text-sm text-gray-400">
                  No matching branches
                </div>
              </div>
            </div>

            <!-- Status -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Status
              </label>
              <select
                v-model="form.status"
                required
                class="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 outline-none focus:border-primary dark:border-gray-700 dark:text-white"
              >
                <option value="" disabled>Select status</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
              </select>
            </div>

            <!-- Buttons -->
            <div class="md:col-span-2 flex gap-3 pt-2">
              <button
                type="submit"
                :disabled="submitting"
                class="rounded-lg bg-orange-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-60"
              >
                {{ submitting ? 'Submitting...' : 'Submit' }}
              </button>
              <button
                type="button"
                @click="showTable = !showTable"
                class="rounded-lg bg-gray-800 px-6 py-2.5 text-sm font-medium text-white hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                {{ showTable ? 'Hide' : 'Show' }}
              </button>
            </div>

            <p v-if="statusMessage" class="md:col-span-2 text-sm" :class="statusOk ? 'text-green-600' : 'text-red-600'">
              {{ statusMessage }}
            </p>

          </form>
        </div>

        <!-- Submitted Internships Table -->
        <div v-if="showTable" class="border-t border-gray-100 p-6 dark:border-gray-800">
          <h4 class="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">
            Submitted Internships ({{ submissions.length }})
          </h4>

          <div v-if="!submissions.length" class="py-6 text-center text-sm text-gray-400">
            No internships submitted yet.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full min-w-[900px] text-left text-sm">
              <thead>
                <tr class="border-b border-gray-200 text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  <th class="px-3 py-2 font-medium">Company</th>
                  <th class="px-3 py-2 font-medium">Email</th>
                  <th class="px-3 py-2 font-medium">Mobile</th>
                  <th class="px-3 py-2 font-medium">Type</th>
                  <th class="px-3 py-2 font-medium">Duration</th>
                  <th class="px-3 py-2 font-medium">Stipend</th>
                  <th class="px-3 py-2 font-medium">City</th>
                  <th class="px-3 py-2 font-medium">Branch</th>
                  <th class="px-3 py-2 font-medium">Status</th>
                  <th class="px-3 py-2 font-medium">Link</th>
                  <th class="px-3 py-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in submissions"
                  :key="item.InternshipId"
                  class="border-b border-gray-100 text-gray-700 dark:border-gray-800 dark:text-gray-300"
                >
                  <td class="px-3 py-2">{{ item.company }}</td>
                  <td class="px-3 py-2">{{ item.email }}</td>
                  <td class="px-3 py-2">{{ item.mobile }}</td>
                  <td class="px-3 py-2">{{ item.companyType }}</td>
                  <td class="px-3 py-2">{{ item.duration }}</td>
                  <td class="px-3 py-2">{{ item.stipend }}</td>
                  <td class="px-3 py-2">{{ item.location }}</td>
                  <td class="px-3 py-2">{{ item.branch }}</td>

                  <!-- Status: Open/Close toggle buttons -->
                  <td class="px-3 py-2">
                    <div class="inline-flex overflow-hidden rounded-full border border-gray-200 dark:border-gray-700">
                      <button
                        type="button"
                        :disabled="updatingStatusId === item.InternshipId"
                        @click="toggleStatus(item, 'Open')"
                        class="px-2.5 py-1 text-xs font-medium transition-colors disabled:opacity-50"
                        :class="item.status === 'Open'
                          ? 'bg-green-500 text-white'
                          : 'bg-transparent text-gray-500 hover:bg-green-50 dark:text-gray-400'"
                      >
                        Open
                      </button>
                      <button
                        type="button"
                        :disabled="updatingStatusId === item.InternshipId"
                        @click="toggleStatus(item, 'Closed')"
                        class="px-2.5 py-1 text-xs font-medium transition-colors disabled:opacity-50"
                        :class="item.status === 'Closed'
                          ? 'bg-red-500 text-white'
                          : 'bg-transparent text-gray-500 hover:bg-red-50 dark:text-gray-400'"
                      >
                        Close
                      </button>
                    </div>
                  </td>

                  <td class="px-3 py-2">
                    <a :href="item.link" target="_blank" class="text-orange-500 hover:underline">Link</a>
                  </td>
                  <td class="px-3 py-2">
                    <button
                      type="button"
                      @click="removeInternship(item.InternshipId)"
                      class="text-xs font-medium text-red-500 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
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
import { ref, reactive, computed, onMounted, onBeforeUnmount } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";
import ComponentCard from "@/components/common/ComponentCard.vue";

const currentPageTitle = ref("Internship");

// Base URL of the Flask API. Vue (Vite) runs on :5173, Flask runs on :5000 —
// change this if your Flask server runs somewhere else.
const API_BASE = "http://127.0.0.1:5000";

const companyTypes = [
  "Private",
  "Public",
  "Government (Gov)",
  "NGO",
  "Startup",
  "MNC",
  "Non-Profit Organization",
  "Educational Institution",
  "Public Sector Undertaking (PSU)",
  "Partnership",
  "Other"
];

const durations = ["2 Months", "3 Months", "6 Months"];

const branches = [
  "Computer Science Engineering (CSE)",
  "Information Technology (IT)",
  "Computer Engineering",
  "Computer Science & Engineering (AI)",
  "Computer Science & Engineering (AI & ML)",
  "Artificial Intelligence (AI)",
  "Artificial Intelligence & Machine Learning (AI/ML)",
  "Data Science",
  "Data Engineering",
  "Cyber Security",
  "Information Security",
  "Software Engineering",
  "Cloud Computing",
  "Cloud Technology",
  "Internet of Things (IoT)",
  "Blockchain Technology",
  "Computer Science & Business Systems (CSBS)",
  "Computer Science & Design",
  "Computer Science & Information Technology",
  "Electronics & Telecommunication Engineering (ENTC)",
  "Electronics & Communication Engineering (ECE)",
  "Electronics Engineering",
  "Electrical Engineering (EE)",
  "Electrical & Electronics Engineering (EEE)",
  "Instrumentation Engineering",
  "Instrumentation & Control Engineering",
  "VLSI Design",
  "Embedded Systems",
  "Robotics & Automation",
  "Mechanical Engineering",
  "Mechatronics Engineering",
  "Automobile Engineering",
  "Production Engineering",
  "Industrial Engineering",
  "Manufacturing Engineering",
  "Robotics Engineering",
  "Aerospace Engineering",
  "Civil Engineering",
  "Construction Engineering",
  "Structural Engineering",
  "Environmental Engineering",
  "Transportation Engineering",
  "Geotechnical Engineering",
  "Water Resources Engineering",
  "Urban & Regional Planning",
  "Chemical Engineering",
  "Biotechnology",
  "Biomedical Engineering",
  "Biochemical Engineering",
  "Food Technology",
  "Pharmaceutical Engineering",
  "Materials Engineering",
  "Metallurgical Engineering",
  "Ceramic Engineering",
  "Polymer Engineering",
  "Information Science & Engineering",
  "Software Technology",
  "Multimedia & Animation",
  "Computer Applications",
  "Digital Technology",
  "FinTech",
  "Cyber Forensics",
  "Game Technology",
  "Mobile Application Development",
  "Web Technology"
];

// Cities grouped by state — embedded directly (same data as RojgarSetu.vue)
const CITY_DATA = {
  "Andaman And Nicobar Islands": [
    "Nicobars",
    "North And Middle Andaman",
    "South Andaman"
  ],
  "Andhra Pradesh": [
    "Adilabad",
    "Anantapur",
    "Chittoor",
    "East Godavari",
    "Guntur",
    "Hyderabad",
    "Karimnagar",
    "Khammam",
    "Krishna",
    "Kurnool",
    "Mahbubnagar",
    "Medak",
    "Nalgonda",
    "Nizamabad",
    "Prakasam",
    "Rangareddy",
    "Sri Potti Sriramulu Nellore",
    "Srikakulam",
    "Visakhapatnam",
    "Vizianagaram",
    "Warangal",
    "West Godavari",
    "YSR"
  ],
  "Arunachal Pradesh": [
    "Anjaw",
    "Changlang",
    "Dibang Valley",
    "East Kameng",
    "East Siang",
    "Kurung Kumey",
    "Lohit",
    "Lower Dibang Valley",
    "Lower Subansiri",
    "Papumpare",
    "Tawang",
    "Tirap",
    "Upper Siang",
    "Upper Subansiri",
    "West Kameng",
    "West Siang"
  ],
  "Assam": [
    "Baksa",
    "Barpeta",
    "Bongaigaon",
    "Cachar",
    "Chirang",
    "Darrang",
    "Dhemaji",
    "Dhubri",
    "Dibrugarh",
    "Dima Hasao",
    "Goalpara",
    "Golaghat",
    "Hailakandi",
    "Jorhat",
    "Kamrup",
    "Kamrup Metropolitan",
    "Karbi Anglong",
    "Karimganj",
    "Kokrajhar",
    "Lakhimpur",
    "Morigaon",
    "Nagaon",
    "Nalbari",
    "Sivasagar",
    "Sonitpur",
    "Tinsukia",
    "Udalguri"
  ],
  "Bihar": [
    "Araria",
    "Arwal",
    "Aurangabad",
    "Banka",
    "Begusarai",
    "Bhagalpur",
    "Bhojpur",
    "Buxar",
    "Darbhanga",
    "Gaya",
    "Gopalganj",
    "Jamui",
    "Jehanabad",
    "Kaimur",
    "Katihar",
    "Khagaria",
    "Kishanganj",
    "Lakhisarai",
    "Madhepura",
    "Madhubani",
    "Munger",
    "Muzaffarpur",
    "Nalanda",
    "Nawada",
    "Pashchim Champaran",
    "Patna",
    "Purbi Champaran",
    "Purnia",
    "Rohtas",
    "Saharsa",
    "Samastipur",
    "Saran",
    "Sheikhpura",
    "Sheohar",
    "Sitamarhi",
    "Siwan",
    "Supaul",
    "Vaishali"
  ],
  "Chandigarh": [
    "Chandigarh"
  ],
  "Chhattisgarh": [
    "Bastar",
    "Bijapur",
    "Bilaspur",
    "Dantewada",
    "Dhamtari",
    "Durg",
    "Janjgir Champa",
    "Jashpur",
    "Kabirdham",
    "Kanker",
    "Korba",
    "Korea",
    "Mahasamund",
    "Narayanpur",
    "Raigarh",
    "Raipur",
    "Rajnandgaon",
    "Surguja"
  ],
  "Dadra and Nagar Haveli": [
    "Dadra and Nagar Haveli"
  ],
  "Daman and Diu": [
    "Daman",
    "Diu"
  ],
  "Delhi": [
    "Central Delhi",
    "East Delhi",
    "New Delhi",
    "North Delhi",
    "North East Delhi",
    "North West Delhi",
    "South Delhi",
    "South West Delhi",
    "West Delhi"
  ],
  "Goa": [
    "North Goa",
    "South Goa"
  ],
  "Gujarat": [
    "Ahmadabad",
    "Amreli",
    "Anand",
    "Banaskantha",
    "Bharuch",
    "Bhavnagar",
    "Dohad",
    "Gandhinagar",
    "Jamnagar",
    "Junagadh",
    "Kachchh",
    "Kheda",
    "Mahesana",
    "Narmada",
    "Navsari",
    "PanchMahal",
    "Patan",
    "Porbandar",
    "Rajkot",
    "Sabarkantha",
    "Surat",
    "Surendranagar",
    "Tapi",
    "The Dangs",
    "Vadodara",
    "Valsad"
  ],
  "Haryana": [
    "Ambala",
    "Bhiwani",
    "Faridabad",
    "Fatehabad",
    "Gurgaon",
    "Hisar",
    "Jhajjar",
    "Jind",
    "Kaithal",
    "Karnal",
    "Kurukshetra",
    "Mahendragarh",
    "Mewat",
    "Palwal",
    "Panchkula",
    "Panipat",
    "Rewari",
    "Rohtak",
    "Sirsa",
    "Sonipat",
    "Yamunanagar"
  ],
  "Himachal Pradesh": [
    "Bilaspur",
    "Chamba",
    "Hamirpur",
    "Kangra",
    "Kinnaur",
    "Kullu",
    "Lahul and Spiti",
    "Mandi",
    "Shimla",
    "Sirmaur",
    "Solan",
    "Una"
  ],
  "Jammu and Kashmir": [
    "Anantnag",
    "Badgam",
    "Bandipora",
    "Baramula",
    "Doda",
    "Ganderbal",
    "Jammu",
    "Kargil",
    "Kathua",
    "Kishtwar",
    "Kulgam",
    "Kupwara",
    "Leh",
    "Pulwama",
    "Punch",
    "Rajouri",
    "Ramban",
    "Reasi",
    "Samba",
    "Shupiyan",
    "Srinagar",
    "Udhampur"
  ],
  "Jharkhand": [
    "Bokaro",
    "Chatra",
    "Deoghar",
    "Dhanbad",
    "Dumka",
    "Garhwa",
    "Giridih",
    "Godda",
    "Gumla",
    "Hazaribagh",
    "Jamshedpur",
    "Jamtara",
    "Khunti",
    "Kodarma",
    "Latehar",
    "Lohardaga",
    "Pakur",
    "Palamu",
    "Pashchimi Singhbhum",
    "Purbi Singhbhum",
    "Ramgarh",
    "Ranchi",
    "Sahibganj",
    "Saraikela Kharsawan",
    "Simdega"
  ],
  "Karnataka": [
    "Bagalkot",
    "Bangalore",
    "Bangalore Rural",
    "Belgaum",
    "Bellary",
    "Bidar",
    "Bijapur",
    "Chamarajanagar",
    "Chikkaballapura",
    "Chikmagalur",
    "Chitradurga",
    "Dakshina Kannada",
    "Davanagere",
    "Dharwad",
    "Gadag",
    "Gulbarga",
    "Hassan",
    "Haveri",
    "Kodagu",
    "Kolar",
    "Koppal",
    "Mandya",
    "Mysore",
    "Raichur",
    "Ramanagara",
    "Shimoga",
    "Tumkur",
    "Udupi",
    "Uttara Kannada",
    "Yadgir"
  ],
  "Kerala": [
    "Alappuzha",
    "Ernakulam",
    "Idukki",
    "Kannur",
    "Kasaragod",
    "Kollam",
    "Kottayam",
    "Kozhikode",
    "Malappuram",
    "Palakkad",
    "Pathanamthitta",
    "Thiruvananthapuram",
    "Thrissur",
    "Wayanad"
  ],
  "Lakshadweep": [
    "Lakshadweep"
  ],
  "Madhya Pradesh": [
    "Alirajpur",
    "Anuppur",
    "Ashoknagar",
    "Balaghat",
    "Barwani",
    "Betul",
    "Bhind",
    "Bhopal",
    "Burhanpur",
    "Chhattarpur",
    "Chhindwara",
    "Damoh",
    "Datia",
    "Dewas",
    "Dhar",
    "Dindori",
    "East Nimar",
    "Guna",
    "Gwalior",
    "Harda",
    "Hoshangabad",
    "Indore",
    "Jabalpur",
    "Jhabua",
    "Katni",
    "Mandla",
    "Mandsaur",
    "Morena",
    "Narsimhapur",
    "Neemuch",
    "Panna",
    "Raisen",
    "Rajgarh",
    "Ratlam",
    "Rewa",
    "Sagar",
    "Satna",
    "Sehore",
    "Seoni",
    "Shahdol",
    "Shajapur",
    "Sheopur",
    "Shivpuri",
    "Sidhi",
    "Singrauli",
    "Tikamgarh",
    "Ujjain",
    "Umaria",
    "Vidisha",
    "West Nimar"
  ],
  "Maharashtra": [
    "Ahmadnagar",
    "Akola",
    "Amravati",
    "Aurangabad",
    "Bhandara",
    "Bid",
    "Buldana",
    "Chandrapur",
    "Dhule",
    "Gadchiroli",
    "Gondiya",
    "Hingoli",
    "Jalgaon",
    "Jalna",
    "Kolhapur",
    "Latur",
    "Mumbai City",
    "Mumbai Suburban",
    "Nagpur",
    "Nanded",
    "Nandurbar",
    "Nashik",
    "Osmanabad",
    "Parbhani",
    "Pune",
    "Raigarh",
    "Ratnagiri",
    "Sangli",
    "Satara",
    "Sindhudurg",
    "Solapur",
    "Thane",
    "Wardha",
    "Washim",
    "Yavatmal"
  ],
  "Manipur": [
    "Bishnupur",
    "Chandel",
    "Churachandpur",
    "Imphal East",
    "Imphal West",
    "Senapati",
    "Tamenglong",
    "Thoubal",
    "Ukhrul"
  ],
  "Meghalaya": [
    "East Garo Hills",
    "East Khasi Hills",
    "Jaintia Hills",
    "Ri Bhoi",
    "South Garo Hills",
    "West Garo Hills",
    "West Khasi Hills"
  ],
  "Mizoram": [
    "Aizawl",
    "Champhai",
    "Kolasib",
    "Lawngtlai",
    "Lunglei",
    "Mamit",
    "Saiha",
    "Serchhip"
  ],
  "Nagaland": [
    "Dimapur",
    "Kiphire",
    "Kohima",
    "Longleng",
    "Mokokchung",
    "Mon",
    "Peren",
    "Phek",
    "Tuensang",
    "Wokha",
    "Zunheboto"
  ],
  "Orissa": [
    "Anugul",
    "Balangir",
    "Baleshwar",
    "Bargarh",
    "Baudh",
    "Bhadrak",
    "Cuttack",
    "Debagarh",
    "Dhenkanal",
    "Gajapati",
    "Ganjam",
    "Jagatsinghapur",
    "Jajapur",
    "Jharsuguda",
    "Kalahandi",
    "Kandhamal",
    "Kendrapara",
    "Kendujhar",
    "Khordha",
    "Koraput",
    "Malkangiri",
    "Mayurbhanj",
    "Nabarangapur",
    "Nayagarh",
    "Nuapada",
    "Puri",
    "Rayagada",
    "Sambalpur",
    "Subarnapur",
    "Sundargarh"
  ],
  "Puducherry": [
    "Karaikal",
    "Mahe",
    "Puducherry",
    "Yanam"
  ],
  "Punjab": [
    "Amritsar",
    "Barnala",
    "Bathinda",
    "Faridkot",
    "Fatehgarh Sahib",
    "Firozpur",
    "Gurdaspur",
    "Hoshiarpur",
    "Jalandhar",
    "Kapurthala",
    "Ludhiana",
    "Mansa",
    "Moga",
    "Mohali",
    "Muktsar",
    "Patiala",
    "Rupnagar",
    "Sangrur",
    "Shahid Bhagat Singh Nagar",
    "Tarn Taran"
  ],
  "Rajasthan": [
    "Ajmer",
    "Alwar",
    "Banswara",
    "Baran",
    "Barmer",
    "Bharatpur",
    "Bhilwara",
    "Bikaner",
    "Bundi",
    "Chittaurgarh",
    "Churu",
    "Dausa",
    "Dhaulpur",
    "Dungarpur",
    "Ganganagar",
    "Hanumangarh",
    "Jaipur",
    "Jaisalmer",
    "Jalor",
    "Jhalawar",
    "Jhunjhunun",
    "Jodhpur",
    "Karauli",
    "Kota",
    "Nagaur",
    "Pali",
    "Pratapgarh",
    "Rajsamand",
    "Sawai Madhopur",
    "Sikar",
    "Sirohi",
    "Tonk",
    "Udaipur"
  ],
  "Sikkim": [
    "East Sikkim",
    "North Sikkim",
    "South Sikkim",
    "West Sikkim"
  ],
  "Tamil Nadu": [
    "Ariyalur",
    "Chennai",
    "Coimbatore",
    "Cuddalore",
    "Dharmapuri",
    "Dindigul",
    "Erode",
    "Kancheepuram",
    "Kanniyakumari",
    "Karur",
    "Krishnagiri",
    "Madurai",
    "Nagapattinam",
    "Namakkal",
    "Perambalur",
    "Pudukkottai",
    "Ramanathapuram",
    "Salem",
    "Sivaganga",
    "Thanjavur",
    "The Nilgiris",
    "Theni",
    "Thiruvallur",
    "Thiruvarur",
    "Thoothukkudi",
    "Tiruchirappalli",
    "Tirunelveli",
    "Tiruppur",
    "Tiruvannamalai",
    "Vellore",
    "Viluppuram",
    "Virudhunagar"
  ],
  "Tripura": [
    "Dhalai",
    "North Tripura",
    "South Tripura",
    "West Tripura"
  ],
  "Uttar Pradesh": [
    "Agra",
    "Aligarh",
    "Allahabad",
    "Ambedkar Nagar",
    "Auraiya",
    "Azamgarh",
    "Baghpat",
    "Bahraich",
    "Ballia",
    "Balrampur",
    "Banda",
    "Barabanki",
    "Bareilly",
    "Basti",
    "Bijnor",
    "Budaun",
    "Bulandshahar",
    "Chandauli",
    "Chitrakoot",
    "Deoria",
    "Etah",
    "Etawah",
    "Faizabad",
    "Farrukhabad",
    "Fatehpur",
    "Firozabad",
    "Gautam Buddha Nagar",
    "Ghaziabad",
    "Ghazipur",
    "Gonda",
    "Gorakhpur",
    "Hamirpur",
    "Hardoi",
    "Jalaun",
    "Jaunpur",
    "Jhansi",
    "Jyotiba Phule Nagar",
    "Kannauj",
    "Kanpur Nagar",
    "Kanshiram Nagar",
    "Kaushambi",
    "Kheri",
    "Kushinagar",
    "Lalitpur",
    "Lucknow",
    "Mahamaya Nagar",
    "Maharajganj",
    "Mahoba",
    "Mainpuri",
    "Mathura",
    "Mau",
    "Meerut",
    "Mirzapur",
    "Moradabad",
    "Muzaffarnagar",
    "Noida",
    "Pilibhit",
    "Pratapgarh",
    "Rae Bareli",
    "Ramabai Nagar",
    "Rampur",
    "Saharanpur",
    "Sant Kabir Nagar",
    "Sant Ravidas Nagar",
    "Shahjahanpur",
    "Shrawasti",
    "Siddharth Nagar",
    "Sitapur",
    "Sonbhadra",
    "Sultanpur",
    "Unnao",
    "Varanasi"
  ],
  "Uttarakhand": [
    "Almora",
    "Bageshwar",
    "Chamoli",
    "Champawat",
    "Dehradun",
    "Haridwar",
    "Nainital",
    "Pauri Garhwal",
    "Pithoragarh",
    "Rudraprayag",
    "Tehri Garhwal",
    "Udham Singh Nagar",
    "Uttarkashi"
  ],
  "West Bengal": [
    "Bankura",
    "Barddhaman",
    "Birbhum",
    "Dakshin Dinajpur",
    "Darjiling",
    "Haora",
    "Hugli",
    "Jalpaiguri",
    "Koch Bihar",
    "Kolkata",
    "Maldah",
    "Murshidabad",
    "Nadia",
    "North Twenty Four Parganas",
    "Paschim Medinipur",
    "Purba Medinipur",
    "Puruliya",
    "South Twenty Four Parganas",
    "Uttar Dinajpur"
  ]
};

const cityStates = ref(
  Object.entries(CITY_DATA).map(([name, cities]) => ({ name, cities }))
);

const form = reactive({
  company: "",
  email: "",
  mobile: "",
  companyType: "",
  duration: "",
  stipend: "",
  link: "",
  location: "",
  branch: "",
  status: "",
});

// ---- City searchable dropdown ----
const citySearch = ref("");
const cityDropdownOpen = ref(false);
const cityFieldRef = ref(null);

const filteredCityStates = computed(() => {
  const q = citySearch.value.trim().toLowerCase();
  if (!q) return cityStates.value;

  return cityStates.value
    .map((state) => ({
      name: state.name,
      cities: state.cities.filter((city) => city.toLowerCase().includes(q)),
    }))
    .filter((state) => state.cities.length > 0);
});

function selectCity(city) {
  form.location = city;
  citySearch.value = city;
  cityDropdownOpen.value = false;


// ---- Branch searchable dropdown ----
const branchSearch = ref("");
const branchDropdownOpen = ref(false);
const branchFieldRef = ref(null);

const filteredBranches = computed(() => {
  const q = branchSearch.value.trim().toLowerCase();
  if (!q) return branches;
  return branches.filter((b) => b.toLowerCase().includes(q));
});

function selectBranch(branch) {
  form.branch = branch;
  branchSearch.value = branch;
  branchDropdownOpen.value = false;
}

// ---- Close dropdowns on outside click ----
function handleClickOutside(event) {
  if (cityFieldRef.value && !cityFieldRef.value.contains(event.target)) {
    cityDropdownOpen.value = false;
    if (citySearch.value !== form.location) {
      citySearch.value = form.location;
    }
  }
  if (branchFieldRef.value && !branchFieldRef.value.contains(event.target)) {
    branchDropdownOpen.value = false;
    if (branchSearch.value !== form.branch) {
      branchSearch.value = form.branch;
    }
  }
}

// ---- Submissions (loaded from the database via the API) ----
// ---- Submissions — now backed by Flask + SQL Server via /api/internships ----

const submissions = ref([]);
const showTable = ref(false);
const submitting = ref(false);
const statusMessage = ref("");
const statusOk = ref(false);

// Tracks which row's status is currently being updated (used to disable
// the Open/Close buttons for that row while the request is in flight).
const updatingStatusId = ref(null);

async function fetchInternships() {
  try {
    const res = await fetch(`${API_BASE}/api/internships`);
    const result = await res.json();

    if (result.success) {
      submissions.value = result.data;
    } else {
      console.error("Could not load internships:", result.error);
    }
  } catch (err) {
    console.error("Could not load internships:", err);
    console.error("Failed to load internships:", err);
  }
}

async function submitForm() {
  // Validate city
  if (!form.location) {
    statusOk.value = false;
    statusMessage.value = "Please select a city from the dropdown list.";
    return;
  }

  // Validate branch
  if (!form.branch) {
    statusOk.value = false;
    statusMessage.value = "Please select a branch from the dropdown list.";
    return;
  }

  submitting.value = true;
  statusMessage.value = "";
  try {
    const res = await fetch(`${API_BASE}/api/internships`, {
      method: "POST",

      headers: { "Content-Type": "application/json" },

      body: JSON.stringify(form),
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    });

    const result = await res.json();

    if (!result.success) {
      statusOk.value = false;
      statusMessage.value = result.error || "Something went wrong.";
      return;
    }

    statusOk.value = true;
    statusMessage.value = "Internship posted successfully!";

    // Reset form
    Object.keys(form).forEach((key) => {
      form[key] = "";
    });

    citySearch.value = "";
    branchSearch.value = "";

    // Refresh table
    await fetchInternships();

  } catch (err) {
    statusOk.value = false;
    statusMessage.value = "Could not connect to server.";
    console.error(err);
  } finally {
    submitting.value = false;
  }
}

// Toggles a single internship's status between "Open" and "Closed" using
// the PATCH /api/internships/<id>/status endpoint. Updates optimistically
// so the button feels instant, and rolls back if the request fails.
async function toggleStatus(item, newStatus) {
  if (item.status === newStatus) return; // already in this state, nothing to do

  updatingStatusId.value = item.InternshipId;
  const previousStatus = item.status;
  item.status = newStatus; // optimistic update

  try {
    const res = await fetch(`${API_BASE}/api/internships/${item.InternshipId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    const result = await res.json();

    if (!result.success) {
      item.status = previousStatus; // revert on failure
      alert(result.error || "Could not update status.");
    }
  } catch (err) {
    item.status = previousStatus; // revert on failure
    console.error(err);
    alert("Could not connect to server.");
  } finally {
    updatingStatusId.value = null;
  }
}

async function removeInternship(id) {
  if (!confirm("Delete this internship?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/internships/${id}`, {
      method: "DELETE",
    });
    const result = await res.json();
    if (result.success) {
      submissions.value = submissions.value.filter((s) => s.InternshipId !== id);
    } else {
      alert(result.error || "Could not delete.");
    }
  } catch (err) {
    console.error(err);
    alert("Could not connect to server.");

  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
  fetchInternships();
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>