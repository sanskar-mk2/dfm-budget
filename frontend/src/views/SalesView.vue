<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const sales = ref([]);
const loading = ref(false);
const error = ref("");

const {
    currentUser,
    currentSalesperson,
    logout: authLogout,
    apiCall,
} = authStore;

const fetchSales = async () => {
    loading.value = true;
    error.value = "";

    try {
        const response = await apiCall("http://localhost:8000/sales");

        if (!response.ok) {
            throw new Error("Failed to fetch sales data");
        }

        const data = await response.json();
        sales.value = data;
    } catch (err) {
        error.value = err.message;
        console.error("Error fetching sales:", err);
    } finally {
        loading.value = false;
    }
};

const logout = () => {
    authLogout();
    router.push("/login");
};

const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
};

onMounted(() => {
    fetchSales();
});
</script>

<template>
    <div class="container mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold">Sales Data</h1>
            <button @click="logout" class="btn btn-outline btn-error">
                Logout
            </button>
        </div>

        <div v-if="loading" class="flex justify-center">
            <div class="loading loading-spinner loading-lg"></div>
        </div>

        <div v-else-if="error" class="alert alert-error">
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

        <div v-else-if="sales.length === 0" class="text-center py-8">
            <p class="text-lg text-base-content/70">No sales data found</p>
        </div>

        <div v-else class="overflow-x-auto">
            <table class="table table-zebra w-full">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Customer</th>
                        <th>Salesperson</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="sale in sales" :key="sale.id">
                        <td>{{ sale.id }}</td>
                        <td>{{ formatDate(sale.date) }}</td>
                        <td>${{ sale.amount?.toFixed(2) || "0.00" }}</td>
                        <td>{{ sale.customer_name || "N/A" }}</td>
                        <td>{{ sale.salesperson_name || "N/A" }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="mt-8 p-4 bg-base-200 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">User Info</h3>
            <p><strong>Username:</strong> {{ currentUser?.username }}</p>
            <p v-if="currentSalesperson">
                <strong>Salesperson:</strong> {{ currentSalesperson.name }}
            </p>
        </div>
    </div>
</template>
