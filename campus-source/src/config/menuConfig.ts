import {
  GridIcon,
  ListIcon,
  PageIcon,
  UserCircleIcon,
} from "../icons";

// Add a new page here ONLY — sidebar + router both update automatically.
// For a top-level item: icon, name, path, component
// For a dropdown item (like Campus Admin): icon, name, subItems: [{ name, path, component }]
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
        name: "News and Event",
        path: "/news-and-event",
        component: () => import("../views/Others/AddNews.vue"),
      },
      {
        icon: UserCircleIcon,
        name: "Profile",
        path: "/profile",
        component: () => import("../views/Others/UserProfile.vue"),
      },
      {
        name: "Campus Admin",
        icon: PageIcon,
        subItems: [
          {
            name: "RojgarSetu",
            path: "/rojgarsetu",
            component: () => import("../views/Others/RojgarSetu.vue"),
          },
        ],
      },
    ],
  },
];

export default menuConfig;