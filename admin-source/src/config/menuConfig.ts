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
            name: "Invite",
            path: "/invite",
            component: () => import("../views/Others/Invite.vue"),
          },
          {
            name: "Advertisement",
            path: "/advertisement",
            component: () => import("../views/Others/Advertisement.vue"),
          },
          {
            name: "Internship",
            path: "/internship",
            component: () => import("../views/Others/Internship.vue"),
          },
          {
            name: "RojgarSetu",
            path: "/rojgarsetu",
            component: () => import("../views/Others/RojgarSetu.vue"),
          },
          {
            name: "Add News",
            path: "/add-news",
            component: () => import("../views/Others/AddNews.vue"),
          },
        ],
      },
    ],
  },
];

export default menuConfig;