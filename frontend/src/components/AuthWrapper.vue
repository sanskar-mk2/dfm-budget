<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import LoginForm from "./LoginForm.vue";

const authStore = useAuthStore();
const loading = ref(true);

const { isAuthenticated } = authStore;

onMounted(() => {
    // Check if user is already authenticated
    loading.value = false;
});
</script>

<template>
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
        <div class="loading loading-spinner loading-lg"></div>
    </div>

    <div v-else-if="!isAuthenticated" class="min-h-screen">
        <LoginForm />
    </div>

    <div v-else class="min-h-screen bg-base-100">
        <slot />
    </div>
</template>
