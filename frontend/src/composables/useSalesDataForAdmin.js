import { ref, computed, unref } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useSalesDataForAdmin(salespersonId) {
    const authStore = useAuthStore();
    const { apiCall } = authStore;

    const sales = ref([]);
    const loading = ref(false);
    const error = ref("");
    const salespersonInfo = ref(null);

    const isHospitality = computed(() => {
        return salespersonInfo.value?.is_hospitality || false;
    });

    const fetchSales = async () => {
        loading.value = true;
        error.value = "";

        try {
            // Use unref to get the actual value from reactive references
            const id = unref(salespersonId);
            const response = await apiCall(`/api/sales/${id}`);

            if (!response.ok) {
                throw new Error("Failed to fetch sales data");
            }

            const data = await response.json();
            sales.value = data.data || [];
            salespersonInfo.value = data.salesperson_info || null;
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
        salespersonInfo,
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
