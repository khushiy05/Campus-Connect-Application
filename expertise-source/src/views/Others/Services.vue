<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="mx-auto max-w-5xl py-6">
      <!-- Section heading -->
      <div class="mb-10 text-center">
    <h2 class="mt-2 text-3xl font-bold text-gray-800 dark:text-white/90">
          Our Services
        </h2>
      </div>

      <!-- Cards -->
      <div class="grid grid-cols-1 gap-7 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="service in services"
          :key="service.title"
          class="overflow-hidden rounded-lg bg-gray-50 p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md dark:bg-gray-900"
        >
          <!-- Meta tags -->
          <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span class="flex items-center gap-1.5">
              <svg class="h-3.5 w-3.5 text-orange-500" viewBox="0 0 20 20" :fill="service.tag1.stroke ? 'none' : 'currentColor'" :stroke="service.tag1.stroke ? 'currentColor' : 'none'" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path fill-rule="evenodd" clip-rule="evenodd" :d="service.tag1.icon" />
              </svg>
              {{ service.tag1.label }}
            </span>
            <span class="flex items-center gap-1.5">
              <svg class="h-3.5 w-3.5 text-orange-500" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" clip-rule="evenodd" :d="icons.clock" />
              </svg>
              {{ service.tag2 }}
            </span>
          </div>

          <h3 class="mt-3 text-lg font-medium text-gray-800 dark:text-white/90">
            {{ service.title }}
          </h3>

          <div class="my-3 border-t border-gray-200 dark:border-gray-700"></div>

          <p class="text-sm leading-relaxed text-gray-500 dark:text-gray-400">
            {{ service.description }}
          </p>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref } from "vue";
import PageBreadcrumb from "@/components/common/PageBreadcrumb.vue";
import AdminLayout from "@/components/layout/AdminLayout.vue";

const currentPageTitle = ref("Services");

const icons = {
  pin: "M9.69 18.933l.003.001C9.89 19.02 10 19 10 19s.11.02.308-.066l.002-.001.006-.003.018-.008a5.741 5.741 0 00.281-.14c.186-.096.446-.24.757-.433.62-.384 1.445-.966 2.274-1.765C15.302 14.988 17 12.493 17 9A7 7 0 103 9c0 3.492 1.698 5.988 3.355 7.584a13.731 13.731 0 002.273 1.765 11.842 11.842 0 00.976.544l.062.029.018.008.006.003zM10 11.25a2.25 2.25 0 100-4.5 2.25 2.25 0 000 4.5z",
  clock: "M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z",
  users: "M7 8a3 3 0 100-6 3 3 0 000 6zM14.5 9a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM1.615 16.428a1.224 1.224 0 01-.569-1.175 6.002 6.002 0 0111.908 0c.058.467-.172.92-.57 1.174A9.953 9.953 0 017 18a9.953 9.953 0 01-5.385-1.572zM14.5 16h-.106c.07-.297.088-.611.048-.933a7.47 7.47 0 00-1.588-3.755 4.502 4.502 0 015.874 2.636.818.818 0 01-.36.98A7.465 7.465 0 0114.5 16z",
  user: "M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z",
  car: "M3 9l1.3-3.5A1.5 1.5 0 015.7 4.5h8.6a1.5 1.5 0 011.4 1L17 9M3 9h14v5a.5.5 0 01-.5.5H15M3 9v5a.5.5 0 00.5.5H5m0 0a1.5 1.5 0 003 0m-3 0a1.5 1.5 0 013 0m4 0a1.5 1.5 0 003 0m-3 0a1.5 1.5 0 013 0m-7 0h4",
};

const services = [
  {
    title: "Mess & Tiffin Finder",
    tag1: { label: "Google Maps", icon: icons.pin },
    tag2: "Live Updates",
    description: "Find the best mess and tiffin options near your hostel instantly.",
  },
  {
    title: "Hostel Near Me",
    tag1: { label: "Google Maps", icon: icons.pin },
    tag2: "Real-Time",
    description: "Locate verified hostels close to your campus in seconds.",
  },
  {
    title: "Library Locator",
    tag1: { label: "Google Maps", icon: icons.pin },
    tag2: "Open Hours",
    description: "Find the nearest library along with its timings and availability.",
  },
  {
    title: "Vehicle Rental",
    tag1: { label: "Available Vehicles", icon: icons.car, stroke: true },
    tag2: "24/7 Service",
    description: "Rent vehicles for your transportation needs around campus.",
  },
  {
    title: "Verified Chat",
    tag1: { label: "Verified Students", icon: icons.users },
    tag2: "Secure",
    description: "Chat safely with approved students — only genuine connections.",
  },
  {
    title: "Mentors",
    tag1: { label: "Skilled Guidance", icon: icons.user },
    tag2: "1-on-1",
    description: "Connect with skilled mentors to guide your learning journey.",
  },
];
</script>