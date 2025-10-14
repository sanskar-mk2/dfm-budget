import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import {
    downloadCSV,
    getSalesBudgetHeaders,
    formatCurrencyForCSV,
} from "@/utils/downloadUtils";

export function useAdminData() {
    const authStore = useAuthStore();
    const loading = ref(false);
    const error = ref(null);
    const summaryData = ref([]);

    const totalSales = computed(() =>
        summaryData.value.reduce((sum, p) => sum + p.total_sales, 0)
    );
    const totalBudget = computed(() =>
        summaryData.value.reduce((sum, p) => sum + p.total_budget, 0)
    );
    const totalGrowthPercent = computed(() => {
        if (totalSales.value === 0) return 0;
        return (
            ((totalBudget.value - totalSales.value) / totalSales.value) * 100
        );
    });

    const hospitalityData = computed(() =>
        summaryData.value.filter(
            (p) => p.role && p.role.toLowerCase().startsWith("hospitality")
        )
    );
    const nonHospitalityData = computed(() =>
        summaryData.value.filter(
            (p) => !p.role || !p.role.toLowerCase().startsWith("hospitality")
        )
    );

    function computeSubtotals(data) {
        if (!data.length)
            return {
                q1_sales: 0,
                q2_sales: 0,
                q3_sales: 0,
                q4_sales: 0,
                total_sales: 0,
                zero_perc_sales: 0,
                zero_perc_sales_percent: 0,
                q1_budget: 0,
                q2_budget: 0,
                q3_budget: 0,
                q4_budget: 0,
                total_budget: 0,
                growth_percent: 0,
            };

        const t = data.reduce(
            (acc, p) => {
                acc.q1_sales += p.q1_sales;
                acc.q2_sales += p.q2_sales;
                acc.q3_sales += p.q3_sales;
                acc.q4_sales += p.q4_sales;
                acc.zero_perc_sales += p.zero_perc_sales;
                acc.q1_budget += p.q1_budget;
                acc.q2_budget += p.q2_budget;
                acc.q3_budget += p.q3_budget;
                acc.q4_budget += p.q4_budget;
                return acc;
            },
            {
                q1_sales: 0,
                q2_sales: 0,
                q3_sales: 0,
                q4_sales: 0,
                zero_perc_sales: 0,
                q1_budget: 0,
                q2_budget: 0,
                q3_budget: 0,
                q4_budget: 0,
            }
        );

        t.total_sales = t.q1_sales + t.q2_sales + t.q3_sales + t.q4_sales;
        t.total_budget = t.q1_budget + t.q2_budget + t.q3_budget + t.q4_budget;
        t.growth_percent =
            t.total_sales !== 0
                ? ((t.total_budget - t.total_sales) / t.total_sales) * 100
                : 0;
        t.zero_perc_sales_percent = t.total_sales
            ? (t.zero_perc_sales / t.total_sales) * 100
            : 0;
        return t;
    }

    const hospitalitySubtotals = computed(() =>
        computeSubtotals(hospitalityData.value)
    );
    const nonHospitalitySubtotals = computed(() =>
        computeSubtotals(nonHospitalityData.value)
    );

    async function fetchAdminSummary() {
        loading.value = true;
        error.value = null;
        try {
            const res = await authStore.apiCall("/api/admin/summary");
            if (!res.ok) throw new Error("Failed to fetch admin summary");
            const data = await res.json();
            summaryData.value = data.data || [];
        } catch (err) {
            error.value = err.message;
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function fetchSalespersonData(id) {
        try {
            const salesRes = await authStore.apiCall(`/api/sales/${id}`);
            if (!salesRes.ok) throw new Error("Failed to fetch sales data");
            const sales = await salesRes.json();

            const budgetRes = await authStore.apiCall(`/api/budget/${id}`);
            if (!budgetRes.ok) throw new Error("Failed to fetch budget data");
            const budget = await budgetRes.json();

            // Get salesperson info from summary data
            const salespersonInfo = summaryData.value.find(
                (p) => p.salesperson_id === id
            );

            return sales.data.map((s) => {
                const b = budget.data.find(
                    (x) =>
                        x.brand === s.brand &&
                        x.flag === s.flag &&
                        x.customer_name === s.customer_name
                );
                const totalSales =
                    (parseFloat(s.q1_sales) || 0) +
                    (parseFloat(s.q2_sales) || 0) +
                    (parseFloat(s.q3_sales) || 0) +
                    (parseFloat(s.q4_sales) || 0);
                const totalBudget = b
                    ? (parseFloat(b.quarter_1_sales) || 0) +
                      (parseFloat(b.quarter_2_sales) || 0) +
                      (parseFloat(b.quarter_3_sales) || 0) +
                      (parseFloat(b.quarter_4_sales) || 0)
                    : 0;
                const growthPercent =
                    totalSales !== 0 &&
                    !isNaN(totalSales) &&
                    !isNaN(totalBudget)
                        ? ((totalBudget - totalSales) / totalSales) * 100
                        : 0;

                return {
                    ...s,
                    salesperson_id: id,
                    salesperson_name:
                        salespersonInfo?.salesperson_name || "Unknown",
                    role: salespersonInfo?.role || "Unknown",
                    q1_budget: b
                        ? formatCurrencyForCSV(b.quarter_1_sales)
                        : "0.00",
                    q2_budget: b
                        ? formatCurrencyForCSV(b.quarter_2_sales)
                        : "0.00",
                    q3_budget: b
                        ? formatCurrencyForCSV(b.quarter_3_sales)
                        : "0.00",
                    q4_budget: b
                        ? formatCurrencyForCSV(b.quarter_4_sales)
                        : "0.00",
                    open_2026: formatCurrencyForCSV(s.open_2026),
                    growth_percent: isNaN(growthPercent)
                        ? "0.00"
                        : growthPercent.toFixed(2),
                };
            });
        } catch (err) {
            console.error(err);
            return [];
        }
    }

    async function downloadSalespersonData(id, name) {
        const data = await fetchSalespersonData(id);
        if (!data.length) return alert("No data available");
        const person = summaryData.value.find((p) => p.salesperson_id === id);
        const isHosp = person?.role?.toLowerCase().startsWith("hospitality");
        const headers = getSalesBudgetHeaders(isHosp);
        const filename = `${name.replace(/[^a-zA-Z0-9]/g, "_")}_budget_${
            new Date().toISOString().split("T")[0]
        }.csv`;
        downloadCSV(data, headers, filename);
    }

    async function downloadFullBudgetSheet() {
        if (!summaryData.value.length) return alert("No data available");

        try {
            // Show loading state
            const originalLoading = loading.value;
            loading.value = true;

            const allData = [];

            // Fetch data for all salespeople
            for (const person of summaryData.value) {
                const data = await fetchSalespersonData(person.salesperson_id);
                allData.push(...data);
            }

            if (!allData.length) {
                alert("No data available");
                return;
            }

            // Determine if we have mixed data types (both hospitality and non-hospitality)
            const hasHospitality = allData.some((d) =>
                d.role?.toLowerCase().startsWith("hospitality")
            );
            const hasNonHospitality = allData.some(
                (d) => !d.role?.toLowerCase().startsWith("hospitality")
            );
            const isMixed = hasHospitality && hasNonHospitality;

            // Use appropriate headers based on data type
            const headers = getSalesBudgetHeaders(hasHospitality, isMixed);

            const filename = `full_budget_sheet_${
                new Date().toISOString().split("T")[0]
            }.csv`;
            downloadCSV(allData, headers, filename);
        } catch (err) {
            console.error("Error downloading full budget sheet:", err);
            alert("Error downloading budget sheet. Please try again.");
        } finally {
            // Restore original loading state
            loading.value = false;
        }
    }

    return {
        loading,
        error,
        summaryData,
        totalSales,
        totalBudget,
        totalGrowthPercent,
        hospitalityData,
        nonHospitalityData,
        hospitalitySubtotals,
        nonHospitalitySubtotals,
        fetchAdminSummary,
        downloadSalespersonData,
        downloadFullBudgetSheet,
    };
}
