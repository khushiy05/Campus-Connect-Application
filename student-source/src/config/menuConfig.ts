import {
  GridIcon,
  UserCircleIcon,
} from "../icons";

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
        icon: UserCircleIcon,
        name: "Profile",
        path: "/profile",
        component: () => import("../views/Others/UserProfile.vue"),
      },
    ],
  },
];

export default menuConfig;