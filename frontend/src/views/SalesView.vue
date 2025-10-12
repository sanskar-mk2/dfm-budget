<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const sales = ref([]);
const loading = ref(false);
const error = ref("");
const debugData = ref(null);
const showDebug = ref(false);

const {
    currentUser,
    currentSalesperson,
    logout: authLogout,
    apiCall,
} = authStore;

const isHospitality = computed(() => {
    const role = currentSalesperson.value?.role || '';
    return role.startsWith('Hospitality');
});

const fetchSales = async () => {
    loading.value = true;
    error.value = "";

    try {
        const response = await apiCall("http://localhost:8000/sales");

        if (!response.ok) {
            throw new Error("Failed to fetch sales data");
        }

        const data = await response.json();
        sales.value = data.data || [];
    } catch (err) {
        error.value = err.message;
        console.error("Error fetching sales:", err);
    } finally {
        loading.value = false;
    }
};

const fetchDebugData = async () => {
    try {
        const response = await apiCall("http://localhost:8000/sales/debug");

        if (!response.ok) {
            throw new Error("Failed to fetch debug data");
        }

        const data = await response.json();
        debugData.value = data;
        showDebug.value = true;
        console.log("Debug data:", data);
    } catch (err) {
        error.value = err.message;
        console.error("Error fetching debug data:", err);
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

const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return "0.00";
    return parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
};

const formatPercentage = (percentage) => {
    if (!percentage && percentage !== 0) return "0.00";
    return parseFloat(percentage).toFixed(2);
};

const getZeroPercentClass = (percentage) => {
    if (!percentage && percentage !== 0) return "";
    const percent = parseFloat(percentage);
    if (percent === 0) return "text-success";
    if (percent < 5) return "text-warning";
    if (percent < 10) return "text-warning";
    return "text-error";
};

// Summary calculation functions
const getTotalQ1 = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.q1_sales) || 0), 0);
};

const getTotalQ2 = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.q2_sales) || 0), 0);
};

const getTotalQ3 = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.q3_sales) || 0), 0);
};

const getTotalQ4 = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.q4_sales) || 0), 0);
};

const getTotalSales = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.total_sales) || 0), 0);
};

const getTotalZeroPercent = () => {
    return sales.value.reduce((sum, sale) => sum + (parseFloat(sale.zero_perc_sales_total) || 0), 0);
};

const getZeroPercentRate = () => {
    const totalSales = getTotalSales();
    const totalZeroPercent = getTotalZeroPercent();
    return totalSales > 0 ? (totalZeroPercent / totalSales) * 100 : 0;
};

onMounted(() => {
    fetchSales();
});
</script>

<template>
    <div class="container mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold">Sales Data</h1>
            <div class="flex gap-2">
                <button
                    @click="fetchDebugData"
                    class="btn btn-outline btn-info"
                >
                    Debug Data
                </button>
                <button @click="logout" class="btn btn-outline btn-error">
                    Logout
                </button>
            </div>
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
                        <th>Brand</th>
                        <th>Flag</th>
                        <th>Customer Name</th>
                        <th>Customer Class</th>
                        <th>Q1 Sales</th>
                        <th>Q2 Sales</th>
                        <th>Q3 Sales</th>
                        <th>Q4 Sales</th>
                        <th>Zero % Sales</th>
                        <th>Total Sales</th>
                        <th>Zero % %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="sale in sales" :key="`${sale.customer_name}-${sale.brand || 'null'}-${sale.flag || 'null'}`">
                        <td>{{ sale.brand || 'N/A' }}</td>
                        <td>{{ sale.flag || 'N/A' }}</td>
                        <td class="font-medium">{{ sale.customer_name || 'N/A' }}</td>
                        <td>{{ sale.derived_customer_class || 'N/A' }}</td>
                        <td class="text-right">${{ formatCurrency(sale.q1_sales) }}</td>
                        <td class="text-right">${{ formatCurrency(sale.q2_sales) }}</td>
                        <td class="text-right">${{ formatCurrency(sale.q3_sales) }}</td>
                        <td class="text-right">${{ formatCurrency(sale.q4_sales) }}</td>
                        <td class="text-right">${{ formatCurrency(sale.zero_perc_sales_total) }}</td>
                        <td class="text-right font-semibold">${{ formatCurrency(sale.total_sales) }}</td>
                        <td class="text-right">
                            <span :class="getZeroPercentClass(sale.zero_perc_sales_percent)">
                                {{ formatPercentage(sale.zero_perc_sales_percent) }}%
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Summary Section -->
        <div v-if="sales.length > 0" class="mt-8 p-4 bg-base-200 rounded-lg">
            <h3 class="text-lg font-semibold mb-4">Sales Summary</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat">
                    <div class="stat-title">Total Customers</div>
                    <div class="stat-value text-primary">{{ sales.length }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q1 Total</div>
                    <div class="stat-value text-info">${{ formatCurrency(getTotalQ1()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q2 Total</div>
                    <div class="stat-value text-info">${{ formatCurrency(getTotalQ2()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q3 Total</div>
                    <div class="stat-value text-info">${{ formatCurrency(getTotalQ3()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q4 Total</div>
                    <div class="stat-value text-info">${{ formatCurrency(getTotalQ4()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Sales</div>
                    <div class="stat-value text-success">${{ formatCurrency(getTotalSales()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Zero % Sales</div>
                    <div class="stat-value text-warning">${{ formatCurrency(getTotalZeroPercent()) }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Zero % Rate</div>
                    <div class="stat-value" :class="getZeroPercentClass(getZeroPercentRate())">
                        {{ getZeroPercentRate().toFixed(2) }}%
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-8 p-4 bg-base-200 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">User Info</h3>
            <p><strong>Username:</strong> {{ currentUser?.username }}</p>
            <p v-if="currentSalesperson">
                <strong>Salesperson:</strong> {{ currentSalesperson.name }}
            </p>
        </div>

        <!-- Debug Data Section -->
        <div
            v-if="showDebug && debugData"
            class="mt-8 p-4 bg-base-300 rounded-lg"
        >
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">Debug Information</h3>
                <button @click="showDebug = false" class="btn btn-sm btn-ghost">
                    Close
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-base-100 p-3 rounded">
                    <h4 class="font-semibold mb-2">Period Information</h4>
                    <p>
                        <strong>Salesman No:</strong>
                        {{ debugData.salesman_no }}
                    </p>
                    <p>
                        <strong>Min Period:</strong>
                        {{ debugData.period_info?.min_period }}
                    </p>
                    <p>
                        <strong>Max Period:</strong>
                        {{ debugData.period_info?.max_period }}
                    </p>
                    <p>
                        <strong>Total Records:</strong>
                        {{ debugData.period_info?.total_records }}
                    </p>
                    <p>
                        <strong>Unique Periods:</strong>
                        {{ debugData.period_info?.unique_periods }}
                    </p>
                </div>

                <div class="bg-base-100 p-3 rounded">
                    <h4 class="font-semibold mb-2">Period List</h4>
                    <div class="max-h-32 overflow-y-auto">
                        <span
                            v-for="period in debugData.period_list"
                            :key="period"
                            class="badge badge-outline mr-1 mb-1"
                        >
                            {{ period }}
                        </span>
                    </div>
                </div>
            </div>

            <div class="mt-4">
                <h4 class="font-semibold mb-2">Sample Sales Data</h4>
                <div class="overflow-x-auto">
                    <table class="table table-xs">
                        <thead>
                            <tr>
                                <th>Flag</th>
                                <th>Brand</th>
                                <th>Customer</th>
                                <th>Period</th>
                                <th>Sales</th>
                                <th>Zero %</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                                v-for="item in debugData.sales_sample"
                                :key="item.id"
                            >
                                <td>{{ item.flag }}</td>
                                <td>{{ item.brand }}</td>
                                <td>{{ item.customer_name }}</td>
                                <td>{{ item.period }}</td>
                                <td>
                                    ${{ item.ext_sales?.toFixed(2) || "0.00" }}
                                </td>
                                <td>{{ item.zero_perc_sales }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>
