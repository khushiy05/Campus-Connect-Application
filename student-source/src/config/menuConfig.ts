import {
  GridIcon,
  UserCircleIcon,
  ListIcon,
  TableIcon,
  PageIcon,
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
      {
        icon: ListIcon,
        name: "Services",
        path: "/services",
        component: () => import("../views/Others/Services.vue"),
      },
      {
        icon: TableIcon,
        name: "RojgarSetu",
        path: "/rojgarsetu",
        component: () => import("../views/Others/RojgarSetu.vue"),
      },
      {
        icon: PageIcon,
        name: "Expertise",
        path: "/expertise",
        component: () => import("../views/Others/Expertise.vue"),
      },
      {
        icon: PageIcon,
        name: "Review",
        path: "/review",
        component: () => import("../views/Others/Review.vue"),
      },
      {
        icon: PageIcon,
        name: "FACEOFF",
        path: "/faceoff",
        component: () => import("../views/Others/FaceOff.vue"),
      },
    ],
  },
];

export default menuConfig;