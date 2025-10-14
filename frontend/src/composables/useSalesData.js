import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useSalesData() {
    const authStore = useAuthStore();
    const { apiCall } = authStore;

    const sales = ref([]);
    const loading = ref(false);
    const error = ref("");

    const isHospitality = computed(() => {
        const role = authStore.currentSalesperson?.role || "";
        return role.startsWith("Hospitality");
    });

    const fetchSales = async () => {
        loading.value = true;
        error.value = "";

        try {
            const response = await apiCall("/api/sales");

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

    // Summary calculation functions
    const getTotalQ1 = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.q1_sales) || 0),
            0
        );
    };

    const getTotalQ2 = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.q2_sales) || 0),
            0
        );
    };

    const getTotalQ3 = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.q3_sales) || 0),
            0
        );
    };

    const getTotalQ4 = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.q4_sales) || 0),
            0
        );
    };

    const getTotalSales = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.total_sales) || 0),
            0
        );
    };

    const getTotalZeroPercent = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.zero_perc_sales_total) || 0),
            0
        );
    };

    const getZeroPercentRate = () => {
        const totalSales = getTotalSales();
        const totalZeroPercent = getTotalZeroPercent();
        return totalSales > 0 ? (totalZeroPercent / totalSales) * 100 : 0;
    };

    const getTotalOpen2026 = () => {
        return sales.value.reduce(
            (sum, sale) => sum + (parseFloat(sale.open_2026) || 0),
            0
        );
    };

    return {
        sales,
        loading,
        error,
        isHospitality,
        fetchSales,
        getTotalQ1,
        getTotalQ2,
        getTotalQ3,
        getTotalQ4,
        getTotalSales,
        getTotalZeroPercent,
        getZeroPercentRate,
        getTotalOpen2026,
    };
}
