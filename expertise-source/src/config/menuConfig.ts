import { GridIcon } from "../icons";

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
        icon: GridIcon,
        name: "Connect",
        path: "/connect",
        component: () => import("../views/Others/Connect.vue"),

      },
    ],
  },
];

export default menuConfig;