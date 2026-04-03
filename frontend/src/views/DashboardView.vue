<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <h2>仪表盘</h2>
      <div class="nav-group">
        <button class="nav-item" @click="go('/sport-meet')">运动会管理系统</button>
        <button class="nav-item" @click="go('/sports-festival')">体育节管理系统</button>
      </div>
    </aside>
    <main class="content-area">
      <h3>请选择左侧模块进入系统</h3>
      <p class="muted">可在此进入运动会或体育节管理系统。</p>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const go = (path) => router.push(path);
</script>
