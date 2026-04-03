import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import SportMeetView from "../views/SportMeetView.vue";
import SportsFestivalView from "../views/SportsFestivalView.vue";

const routes = [
  { path: "/", name: "login", component: LoginView },
  { path: "/dashboard", name: "dashboard", component: DashboardView },
  { path: "/sport-meet", name: "sport-meet", component: SportMeetView },
  { path: "/sports-festival", name: "sports-festival", component: SportsFestivalView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
