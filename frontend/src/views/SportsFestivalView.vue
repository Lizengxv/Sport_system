<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <h2>体育节管理</h2>
      <div class="nav-group">
        <button class="nav-item" @click="goBack">返回仪表盘</button>
      </div>
    </aside>
    <main class="content-area">
      <h3>体育节管理系统</h3>
      <p class="muted">该模块预留，可按需求扩展。</p>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const goBack = () => router.push("/dashboard");
</script>
