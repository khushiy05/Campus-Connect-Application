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
  icon: GridIcon,   // use whatever icon Dashboard uses
  name: 'Connect',
  path: '/connect',
},
    ],
  },
];

export default menuConfig;