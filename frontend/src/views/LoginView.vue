<template>
  <div class="login-card">
    <h1>校体育管理系统</h1>
    <div v-if="mode === 'login'">
      <div class="form-row">
        <label>学校</label>
        <input v-model="login.school" placeholder="输入学校名称" />
      </div>
      <div class="form-row">
        <label>密码</label>
        <input v-model="login.password" type="password" placeholder="输入密码" />
      </div>
      <button class="btn" @click="handleLogin">登录</button>
      <p class="muted">
        首次登录请先
        <a href="#" @click.prevent="mode = 'register'">邮箱注册</a>
        或
        <a href="#" @click.prevent="mode = 'reset'">修改密码</a>
      </p>
    </div>

    <div v-else-if="mode === 'register'">
      <div class="form-row">
        <label>学校</label>
        <input v-model="register.school" placeholder="输入学校名称" />
      </div>
      <div class="form-row">
        <label>邮箱</label>
        <input v-model="register.email" placeholder="输入邮箱" />
      </div>
      <div class="form-row">
        <label>密码</label>
        <input v-model="register.password" type="password" placeholder="设置密码" />
      </div>
      <button class="btn" @click="handleRegister">注册</button>
      <p class="muted">
        已有账号?
        <a href="#" @click.prevent="mode = 'login'">返回登录</a>
      </p>
    </div>

    <div v-else>
      <div class="form-row">
        <label>邮箱</label>
        <input v-model="reset.email" placeholder="输入邮箱" />
      </div>
      <div class="form-row">
        <label>新密码</label>
        <input v-model="reset.new_password" type="password" placeholder="设置新密码" />
      </div>
      <button class="btn" @click="handleReset">修改密码</button>
      <p class="muted">
        <a href="#" @click.prevent="mode = 'login'">返回登录</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();
const mode = ref("login");

const login = reactive({
  school: "",
  password: "",
});

const register = reactive({
  school: "",
  email: "",
  password: "",
});

const reset = reactive({
  email: "",
  new_password: "",
});

const handleLogin = async () => {
  const { data } = await api.post("/auth/login", login);
  if (data?.message === "ok") {
    router.push("/dashboard");
  }
};

const handleRegister = async () => {
  await api.post("/auth/register", register);
  mode.value = "login";
};

const handleReset = async () => {
  await api.post("/auth/reset-password", reset);
  mode.value = "login";
};
</script>
