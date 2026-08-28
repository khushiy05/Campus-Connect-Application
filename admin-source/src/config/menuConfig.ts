import {
  GridIcon,
  ListIcon,
  TableIcon,
  PageIcon,
} from "../icons"; 

// Add a new page here ONLY — sidebar + router both update automatically.
// For a top-level item: icon, name, path, component
// For a dropdown item (like Admin): icon, name, subItems: [{ name, path, component }]
const menuConfig = [
  {
    title: "Menu",
    items: [
      {
        icon: GridIcon,
        name: "Dashboard",
        path: "/",
        component: () => import("../views/Ecommerce.vue"),
      },
      {
        icon: ListIcon,
        name: "Enquiry",
        path: "/enquiry",
        component: () => import("../views/Others/Enquiry.vue"),
      },
      {
        icon: TableIcon,
        name: "Campus Registration",
        path: "/campus-registration",
        component: () => import("../views/Others/CampusRegistration.vue"),
      },
      {
        name: "Admin",
        icon: PageIcon,
        subItems: [
          {
            name: "Expertise",
            path: "/expertise",
            component: () => import("../views/Others/Expertise.vue"),
          },
          {
            name: "Campus",
            path: "/campus",
            component: () => import("../views/Others/Campus.vue"),
          },
          {
            name: "Invite",
            path: "/invite",
            component: () => import("../views/Others/Invite.vue"),
          },
        ],
      },
    ],
  },
];

export default menuConfig;