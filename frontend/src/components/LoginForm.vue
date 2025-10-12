<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const handleLogin = async () => {
    if (!username.value || !password.value) {
        error.value = "Please fill in all fields";
        return;
    }

    loading.value = true;
    error.value = "";

    try {
        await authStore.login(username.value, password.value);
        // Redirect to home page after successful login
        router.push("/");
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <div class="min-h-screen flex items-center justify-center bg-base-200">
        <div class="card w-96 bg-base-100 shadow-xl">
            <div class="card-body">
                <h2 class="card-title justify-center text-2xl font-bold mb-6">
                    Login
                </h2>

                <form @submit.prevent="handleLogin" class="space-y-4">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Username</span>
                        </label>
                        <input
                            v-model="username"
                            type="text"
                            placeholder="Enter username"
                            class="input input-bordered w-full"
                            :class="{ 'input-error': error }"
                            required
                        />
                    </div>

                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Password</span>
                        </label>
                        <input
                            v-model="password"
                            type="password"
                            placeholder="Enter password"
                            class="input input-bordered w-full"
                            :class="{ 'input-error': error }"
                            required
                        />
                    </div>

                    <div v-if="error" class="alert alert-error">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="stroke-current shrink-0 h-6 w-6"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <span>{{ error }}</span>
                    </div>

                    <div class="form-control mt-6">
                        <button
                            type="submit"
                            class="btn btn-primary w-full"
                            :class="{ loading: loading }"
                            :disabled="loading"
                        >
                            <span v-if="!loading">Login</span>
                            <span v-else>Logging in...</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
