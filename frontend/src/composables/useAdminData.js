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
                q4_orders: 0,
                total_sales: 0,
                zero_perc_sales: 0,
                zero_perc_sales_percent: 0,
                open_2026: 0,
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
                acc.q4_orders += p.q4_orders;
                acc.zero_perc_sales += p.zero_perc_sales;
                acc.open_2026 += p.open_2026;
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
                q4_orders: 0,
                zero_perc_sales: 0,
                open_2026: 0,
                q1_budget: 0,
                q2_budget: 0,
                q3_budget: 0,
                q4_budget: 0,
            }
        );

        t.total_sales =
            t.q1_sales + t.q2_sales + t.q3_sales + t.q4_sales + t.q4_orders;
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

    const parseNumericValue = (value) => {
        if (value === null || value === undefined) return 0;
        if (typeof value === "number") return value;
        if (typeof value === "string") {
            const cleaned = value.replace(/[%$,]/g, "").trim();
            const parsed = parseFloat(cleaned);
            return Number.isNaN(parsed) ? 0 : parsed;
        }
        return 0;
    };

    const sumField = (rows, keys) => {
        const lookupKeys = Array.isArray(keys) ? keys : [keys];
        return rows.reduce((total, row) => {
            for (const key of lookupKeys) {
                if (row[key] !== undefined && row[key] !== null) {
                    total += parseNumericValue(row[key]);
                    break;
                }
            }
            return total;
        }, 0);
    };

    const createTotalsRow = (rows, overrides = {}) => {
        if (!rows?.length) return null;

        const totals = {
            salesperson_name: "Total",
            salesperson_id: "",
            role: "",
            brand: "",
            flag: "",
            derived_customer_class: "",
            customer_name: "",
        };

        const q1Sales = sumField(rows, "q1_sales");
        const q2Sales = sumField(rows, "q2_sales");
        const q3Sales = sumField(rows, "q3_sales");
        const q4Sales = sumField(rows, "q4_sales");
        const q4Orders = sumField(rows, "q4_orders");
        const totalSalesFromField = sumField(rows, "total_sales");
        const computedTotalSales =
            q1Sales + q2Sales + q3Sales + q4Sales + q4Orders;
        const totalSales =
            totalSalesFromField !== 0
                ? totalSalesFromField
                : computedTotalSales;
        const zeroPercSales = sumField(rows, [
            "zero_perc_sales_total",
            "zero_perc_sales",
        ]);
        const open2026 = sumField(rows, "open_2026");
        const q1Budget = sumField(rows, "q1_budget");
        const q2Budget = sumField(rows, "q2_budget");
        const q3Budget = sumField(rows, "q3_budget");
        const q4Budget = sumField(rows, "q4_budget");
        const totalBudgetFromQuarters =
            q1Budget + q2Budget + q3Budget + q4Budget;
        const totalBudgetField = sumField(rows, "total_budget");
        const totalBudget =
            totalBudgetFromQuarters !== 0
                ? totalBudgetFromQuarters
                : totalBudgetField;

        const zeroPercPercentValue =
            totalSales !== 0 ? (zeroPercSales / totalSales) * 100 : 0;
        const growthPercentValue =
            totalSales !== 0
                ? (((totalBudget || 0) - totalSales) / totalSales) * 100
                : 0;

        return {
            ...totals,
            ...overrides,
            q1_sales: formatCurrencyForCSV(q1Sales),
            q2_sales: formatCurrencyForCSV(q2Sales),
            q3_sales: formatCurrencyForCSV(q3Sales),
            q4_sales: formatCurrencyForCSV(q4Sales),
            q4_orders: formatCurrencyForCSV(q4Orders),
            total_sales: formatCurrencyForCSV(totalSales),
            zero_perc_sales_total: formatCurrencyForCSV(zeroPercSales),
            zero_perc_sales_percent: Number.isFinite(zeroPercPercentValue)
                ? zeroPercPercentValue.toFixed(2)
                : "0.00",
            open_2026: formatCurrencyForCSV(open2026),
            q1_budget: formatCurrencyForCSV(q1Budget),
            q2_budget: formatCurrencyForCSV(q2Budget),
            q3_budget: formatCurrencyForCSV(q3Budget),
            q4_budget: formatCurrencyForCSV(q4Budget),
            growth_percent: Number.isFinite(growthPercentValue)
                ? growthPercentValue.toFixed(2)
                : "0.00",
        };
    };

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

            // Track which budgets have been matched with sales
            // Use the same matching logic: brand, flag, customer_name
            const matchedBudgetKeys = new Set();

            // Map sales data to include budget information
            const salesData = sales.data.map((s) => {
                const b = budget.data.find(
                    (x) =>
                        x.brand === s.brand &&
                        x.flag === s.flag &&
                        x.customer_name === s.customer_name
                );

                // Mark this budget as matched if found
                // Use the same key format as matching logic (brand, flag, customer_name)
                if (b) {
                    const budgetKey = `${b.brand || "null"}_${
                        b.flag || "null"
                    }_${b.customer_name || "null"}`;
                    matchedBudgetKeys.add(budgetKey);
                }

                const totalSales =
                    (parseFloat(s.q1_sales) || 0) +
                    (parseFloat(s.q2_sales) || 0) +
                    (parseFloat(s.q3_sales) || 0) +
                    (parseFloat(s.q4_sales) || 0) +
                    (parseFloat(s.q4_orders) || 0);
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

            // Find custom budgets that don't have matching sales
            const customBudgets = budget.data
                .filter((b) => {
                    if (!b.is_custom) return false;

                    // Check if this budget was already matched with a sale
                    // Use the same key format as matching logic (brand, flag, customer_name)
                    const budgetKey = `${b.brand || "null"}_${
                        b.flag || "null"
                    }_${b.customer_name || "null"}`;
                    return !matchedBudgetKeys.has(budgetKey);
                })
                .map((b) => {
                    // Convert custom budget to CSV format with zero sales values
                    const totalBudget =
                        (parseFloat(b.quarter_1_sales) || 0) +
                        (parseFloat(b.quarter_2_sales) || 0) +
                        (parseFloat(b.quarter_3_sales) || 0) +
                        (parseFloat(b.quarter_4_sales) || 0);

                    // Determine if this is hospitality based on customer_class
                    const isHosp =
                        b.customer_class &&
                        b.customer_class
                            .toLowerCase()
                            .startsWith("hospitality");

                    return {
                        salesperson_id: id,
                        salesperson_name:
                            salespersonInfo?.salesperson_name || "Unknown",
                        role: salespersonInfo?.role || "Unknown",
                        brand: b.brand || "",
                        flag: b.flag || "",
                        derived_customer_class: b.customer_class || "",
                        customer_name: b.customer_name || "",
                        q1_sales: "0.00",
                        q2_sales: "0.00",
                        q3_sales: "0.00",
                        q4_sales: "0.00",
                        q4_orders: "0.00",
                        total_sales: "0.00",
                        zero_perc_sales_total: "0.00",
                        zero_perc_sales_percent: "0.00",
                        open_2026: "0.00",
                        q1_budget: formatCurrencyForCSV(b.quarter_1_sales),
                        q2_budget: formatCurrencyForCSV(b.quarter_2_sales),
                        q3_budget: formatCurrencyForCSV(b.quarter_3_sales),
                        q4_budget: formatCurrencyForCSV(b.quarter_4_sales),
                        growth_percent: totalBudget > 0 ? "100.00" : "0.00",
                    };
                });

            // Combine sales data with custom budgets
            return [...salesData, ...customBudgets];
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
        const totalsRow = createTotalsRow(data, {
            salesperson_name: "Total",
            role: "",
        });
        const preparedData = totalsRow ? [...data, totalsRow] : data;
        downloadCSV(preparedData, headers, filename);
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
            const totalsRow = createTotalsRow(allData, {
                salesperson_name: "Grand Total",
            });
            const preparedData = totalsRow ? [...allData, totalsRow] : allData;
            downloadCSV(preparedData, headers, filename);
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
