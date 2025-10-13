<template>
    <div class="admin-view">
        <div class="header">
            <div class="header-content">
                <div class="header-text">
                    <h1>Admin Dashboard</h1>
                    <p class="subtitle">Sales and Budget Summary for All Salespeople</p>
                </div>
                <div class="header-actions">
                    <button 
                        @click="downloadFullBudgetSheet" 
                        class="btn btn-primary"
                        :disabled="loading || summaryData.length === 0"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Download Full Budget Sheet
                    </button>
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Loading admin summary...</p>
        </div>

        <div v-else-if="error" class="error">
            <h3>Error Loading Data</h3>
            <p>{{ error }}</p>
            <button @click="fetchAdminSummary" class="retry-btn">Retry</button>
        </div>

        <div v-else class="summary-content">
            <div class="summary-stats">
                <div class="stat-card">
                    <h3>Total Salespeople</h3>
                    <p class="stat-number">{{ summaryData.length }}</p>
                </div>
                <div class="stat-card">
                    <h3>Total Sales</h3>
                    <p class="stat-number">${{ formatNumber(totalSales) }}</p>
                </div>
                <div class="stat-card">
                    <h3>Total Budget</h3>
                    <p class="stat-number">${{ formatNumber(totalBudget) }}</p>
                </div>
                <div class="stat-card">
                    <h3>Overall Variance</h3>
                    <p
                        class="stat-number"
                        :class="totalVariance >= 0 ? 'positive' : 'negative'"
                    >
                        ${{ formatNumber(totalVariance) }}
                    </p>
                </div>
            </div>

            <div class="table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>View</th>
                            <th>Role</th>
                            <th>Salesperson</th>
                            <th>Q1 Sales</th>
                            <th>Q2 Sales</th>
                            <th>Q3 Sales</th>
                            <th>Q4 Orders</th>
                            <th>Total Sales</th>
                            <th>Zero % Sales</th>
                            <th>Q1 Budget</th>
                            <th>Q2 Budget</th>
                            <th>Q3 Budget</th>
                            <th>Q4 Budget</th>
                            <th>Total Budget</th>
                            <th>Variance</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Hospitality Group -->
                        <template v-if="hospitalityData.length > 0">
                            <tr class="group-header hospitality-group">
                                <td colspan="15" class="group-title">
                                    <strong
                                        >Hospitality Salespeople ({{
                                            hospitalityData.length
                                        }})</strong
                                    >
                                </td>
                            </tr>
                            <tr
                                v-for="person in hospitalityData"
                                :key="person.salesperson_id"
                                class="data-row"
                            >
                                <td class="action-buttons">
                                    <div class="flex gap-2">
                                        <button
                                            @click="
                                                viewSalesperson(
                                                    person.salesperson_id
                                                )
                                            "
                                            class="btn btn-sm btn-primary"
                                            title="View Salesperson Details"
                                        >
                                            View
                                        </button>
                                        <button
                                            @click="
                                                downloadSalespersonData(
                                                    person.salesperson_id,
                                                    person.salesperson_name
                                                )
                                            "
                                            class="btn btn-sm btn-secondary"
                                            title="Download Salesperson Data"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                        </button>
                                    </div>
                                </td>
                                <td class="role">{{ person.role }}</td>
                                <td class="salesperson-name">
                                    <span class="name">{{
                                        person.salesperson_name
                                    }}</span>
                                    <span class="id"
                                        >ID: {{ person.salesperson_id }}</span
                                    >
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q1_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q2_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q3_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q4_sales) }}
                                </td>
                                <td class="number total-sales">
                                    ${{ formatNumber(person.total_sales) }}
                                </td>
                                <td class="number">
                                    <span class="zero-perc">
                                        ${{
                                            formatNumber(person.zero_perc_sales)
                                        }}
                                        <small
                                            >({{
                                                person.zero_perc_sales_percent
                                            }}%)</small
                                        >
                                    </span>
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q1_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q2_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q3_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q4_budget) }}
                                </td>
                                <td class="number total-budget">
                                    ${{ formatNumber(person.total_budget) }}
                                </td>
                                <td class="number">
                                    <span
                                        class="variance"
                                        :class="
                                            person.variance >= 0
                                                ? 'positive'
                                                : 'negative'
                                        "
                                    >
                                        ${{ formatNumber(person.variance) }}
                                    </span>
                                </td>
                            </tr>
                            <tr class="group-subtotal hospitality-subtotal">
                                <td class="subtotal-label">
                                    <strong>Hospitality Subtotal</strong>
                                </td>
                                <td class="subtotal-count">
                                    {{ hospitalityData.length }} salespeople
                                </td>
                                <td></td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q1_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q2_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q3_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q4_sales
                                        )
                                    }}
                                </td>
                                <td class="number total-sales">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.total_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    <span class="zero-perc">
                                        ${{
                                            formatNumber(
                                                hospitalitySubtotals.zero_perc_sales
                                            )
                                        }}
                                        <small
                                            >({{
                                                hospitalitySubtotals.zero_perc_sales_percent
                                            }}%)</small
                                        >
                                    </span>
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q1_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q2_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q3_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.q4_budget
                                        )
                                    }}
                                </td>
                                <td class="number total-budget">
                                    ${{
                                        formatNumber(
                                            hospitalitySubtotals.total_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    <span
                                        class="variance"
                                        :class="
                                            hospitalitySubtotals.variance >= 0
                                                ? 'positive'
                                                : 'negative'
                                        "
                                    >
                                        ${{
                                            formatNumber(
                                                hospitalitySubtotals.variance
                                            )
                                        }}
                                    </span>
                                </td>
                            </tr>
                        </template>

                        <!-- Non-Hospitality Group -->
                        <template v-if="nonHospitalityData.length > 0">
                            <tr class="group-header non-hospitality-group">
                                <td colspan="15" class="group-title">
                                    <strong
                                        >Non-Hospitality Salespeople ({{
                                            nonHospitalityData.length
                                        }})</strong
                                    >
                                </td>
                            </tr>
                            <tr
                                v-for="person in nonHospitalityData"
                                :key="person.salesperson_id"
                                class="data-row"
                            >
                                <td class="action-buttons">
                                    <div class="flex gap-2">
                                        <button
                                            @click="
                                                viewSalesperson(
                                                    person.salesperson_id
                                                )
                                            "
                                            class="btn btn-sm btn-primary"
                                            title="View Salesperson Details"
                                        >
                                            View
                                        </button>
                                        <button
                                            @click="
                                                downloadSalespersonData(
                                                    person.salesperson_id,
                                                    person.salesperson_name
                                                )
                                            "
                                            class="btn btn-sm btn-secondary"
                                            title="Download Salesperson Data"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                        </button>
                                    </div>
                                </td>
                                <td class="role">{{ person.role }}</td>
                                <td class="salesperson-name">
                                    <span class="name">{{
                                        person.salesperson_name
                                    }}</span>
                                    <span class="id"
                                        >ID: {{ person.salesperson_id }}</span
                                    >
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q1_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q2_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q3_sales) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q4_sales) }}
                                </td>
                                <td class="number total-sales">
                                    ${{ formatNumber(person.total_sales) }}
                                </td>
                                <td class="number">
                                    <span class="zero-perc">
                                        ${{
                                            formatNumber(person.zero_perc_sales)
                                        }}
                                        <small
                                            >({{
                                                person.zero_perc_sales_percent
                                            }}%)</small
                                        >
                                    </span>
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q1_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q2_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q3_budget) }}
                                </td>
                                <td class="number">
                                    ${{ formatNumber(person.q4_budget) }}
                                </td>
                                <td class="number total-budget">
                                    ${{ formatNumber(person.total_budget) }}
                                </td>
                                <td class="number">
                                    <span
                                        class="variance"
                                        :class="
                                            person.variance >= 0
                                                ? 'positive'
                                                : 'negative'
                                        "
                                    >
                                        ${{ formatNumber(person.variance) }}
                                    </span>
                                </td>
                            </tr>
                            <tr class="group-subtotal non-hospitality-subtotal">
                                <td class="subtotal-label">
                                    <strong>Non-Hospitality Subtotal</strong>
                                </td>
                                <td class="subtotal-count">
                                    {{ nonHospitalityData.length }} salespeople
                                </td>
                                <td></td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q1_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q2_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q3_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q4_sales
                                        )
                                    }}
                                </td>
                                <td class="number total-sales">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.total_sales
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    <span class="zero-perc">
                                        ${{
                                            formatNumber(
                                                nonHospitalitySubtotals.zero_perc_sales
                                            )
                                        }}
                                        <small
                                            >({{
                                                nonHospitalitySubtotals.zero_perc_sales_percent
                                            }}%)</small
                                        >
                                    </span>
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q1_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q2_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q3_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.q4_budget
                                        )
                                    }}
                                </td>
                                <td class="number total-budget">
                                    ${{
                                        formatNumber(
                                            nonHospitalitySubtotals.total_budget
                                        )
                                    }}
                                </td>
                                <td class="number">
                                    <span
                                        class="variance"
                                        :class="
                                            nonHospitalitySubtotals.variance >=
                                            0
                                                ? 'positive'
                                                : 'negative'
                                        "
                                    >
                                        ${{
                                            formatNumber(
                                                nonHospitalitySubtotals.variance
                                            )
                                        }}
                                    </span>
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { downloadCSV, getSalesBudgetHeaders, formatCurrencyForCSV } from "@/utils/downloadUtils";

const authStore = useAuthStore();
const router = useRouter();

const loading = ref(false);
const error = ref(null);
const summaryData = ref([]);

const totalSales = computed(() => {
    return summaryData.value.reduce(
        (sum, person) => sum + person.total_sales,
        0
    );
});

const totalBudget = computed(() => {
    return summaryData.value.reduce(
        (sum, person) => sum + person.total_budget,
        0
    );
});

const totalVariance = computed(() => {
    return totalSales.value - totalBudget.value;
});

// Group data by role type
const hospitalityData = computed(() => {
    return summaryData.value.filter(
        (person) =>
            person.role && person.role.toLowerCase().startsWith("hospitality")
    );
});

const nonHospitalityData = computed(() => {
    return summaryData.value.filter(
        (person) =>
            !person.role || !person.role.toLowerCase().startsWith("hospitality")
    );
});

// Calculate subtotals for each group
const hospitalitySubtotals = computed(() => {
    const data = hospitalityData.value;
    if (data.length === 0) {
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
            variance: 0,
        };
    }

    const totals = data.reduce(
        (acc, person) => ({
            q1_sales: acc.q1_sales + person.q1_sales,
            q2_sales: acc.q2_sales + person.q2_sales,
            q3_sales: acc.q3_sales + person.q3_sales,
            q4_sales: acc.q4_sales + person.q4_sales,
            zero_perc_sales: acc.zero_perc_sales + person.zero_perc_sales,
            q1_budget: acc.q1_budget + person.q1_budget,
            q2_budget: acc.q2_budget + person.q2_budget,
            q3_budget: acc.q3_budget + person.q3_budget,
            q4_budget: acc.q4_budget + person.q4_budget,
        }),
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

    totals.total_sales =
        totals.q1_sales + totals.q2_sales + totals.q3_sales + totals.q4_sales;
    totals.total_budget =
        totals.q1_budget +
        totals.q2_budget +
        totals.q3_budget +
        totals.q4_budget;
    totals.variance = totals.total_sales - totals.total_budget;
    totals.zero_perc_sales_percent =
        totals.total_sales > 0
            ? (totals.zero_perc_sales / totals.total_sales) * 100
            : 0;

    return totals;
});

const nonHospitalitySubtotals = computed(() => {
    const data = nonHospitalityData.value;
    if (data.length === 0) {
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
            variance: 0,
        };
    }

    const totals = data.reduce(
        (acc, person) => ({
            q1_sales: acc.q1_sales + person.q1_sales,
            q2_sales: acc.q2_sales + person.q2_sales,
            q3_sales: acc.q3_sales + person.q3_sales,
            q4_sales: acc.q4_sales + person.q4_sales,
            zero_perc_sales: acc.zero_perc_sales + person.zero_perc_sales,
            q1_budget: acc.q1_budget + person.q1_budget,
            q2_budget: acc.q2_budget + person.q2_budget,
            q3_budget: acc.q3_budget + person.q3_budget,
            q4_budget: acc.q4_budget + person.q4_budget,
        }),
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

    totals.total_sales =
        totals.q1_sales + totals.q2_sales + totals.q3_sales + totals.q4_sales;
    totals.total_budget =
        totals.q1_budget +
        totals.q2_budget +
        totals.q3_budget +
        totals.q4_budget;
    totals.variance = totals.total_sales - totals.total_budget;
    totals.zero_perc_sales_percent =
        totals.total_sales > 0
            ? (totals.zero_perc_sales / totals.total_sales) * 100
            : 0;

    return totals;
});

const formatNumber = (num) => {
    if (num === null || num === undefined) return "0";
    return new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(num);
};

const fetchAdminSummary = async () => {
    loading.value = true;
    error.value = null;

    try {
        const response = await authStore.apiCall(
            "http://localhost:8000/admin/summary"
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Failed to fetch admin summary"
            );
        }

        const data = await response.json();
        summaryData.value = data.data || [];
    } catch (err) {
        error.value = err.message;
        console.error("Error fetching admin summary:", err);
    } finally {
        loading.value = false;
    }
};

const viewSalesperson = (salespersonId) => {
    router.push(`/salesperson/${salespersonId}`);
};

// Download functions
const downloadFullBudgetSheet = async () => {
    try {
        const allData = [];
        
        // Fetch data for all salespeople
        for (const person of summaryData.value) {
            const salesData = await fetchSalespersonData(person.salesperson_id);
            if (salesData) {
                allData.push(...salesData);
            }
        }
        
        if (allData.length === 0) {
            alert('No data available to download');
            return;
        }
        
        // Determine if this is hospitality data (check first person's role)
        const isHospitality = summaryData.value.some(person => 
            person.role && person.role.toLowerCase().startsWith('hospitality')
        );
        
        const headers = getSalesBudgetHeaders(isHospitality);
        const filename = `full_budget_sheet_${new Date().toISOString().split('T')[0]}.csv`;
        
        downloadCSV(allData, headers, filename);
    } catch (error) {
        console.error('Error downloading full budget sheet:', error);
        alert('Error downloading data. Please try again.');
    }
};

const downloadSalespersonData = async (salespersonId, salespersonName) => {
    try {
        const salesData = await fetchSalespersonData(salespersonId);
        
        if (!salesData || salesData.length === 0) {
            alert('No data available for this salesperson');
            return;
        }
        
        // Determine if this is hospitality data
        const person = summaryData.value.find(p => p.salesperson_id === salespersonId);
        const isHospitality = person && person.role && person.role.toLowerCase().startsWith('hospitality');
        
        const headers = getSalesBudgetHeaders(isHospitality);
        const filename = `${salespersonName.replace(/[^a-zA-Z0-9]/g, '_')}_budget_${new Date().toISOString().split('T')[0]}.csv`;
        
        downloadCSV(salesData, headers, filename);
    } catch (error) {
        console.error('Error downloading salesperson data:', error);
        alert('Error downloading data. Please try again.');
    }
};

const fetchSalespersonData = async (salespersonId) => {
    try {
        // Fetch sales data
        const salesResponse = await authStore.apiCall(`http://localhost:8000/sales/${salespersonId}`);
        if (!salesResponse.ok) throw new Error('Failed to fetch sales data');
        const salesData = await salesResponse.json();
        
        // Fetch budget data
        const budgetResponse = await authStore.apiCall(`http://localhost:8000/budget/${salespersonId}`);
        if (!budgetResponse.ok) throw new Error('Failed to fetch budget data');
        const budgetData = await budgetResponse.json();
        
        // Combine sales and budget data
        const combinedData = salesData.data.map(sale => {
            // Find matching budget entry
            const budget = budgetData.data.find(b => 
                b.brand === sale.brand && 
                b.flag === sale.flag && 
                b.customer_name === sale.customer_name
            );
            
            return {
                ...sale,
                salesperson_name: salesData.salesperson_info?.salesperson_name || 'Unknown',
                salesperson_id: salespersonId,
                role: salesData.salesperson_info?.role || 'Unknown',
                q1_budget: budget ? formatCurrencyForCSV(budget.quarter_1_sales) : '0.00',
                q2_budget: budget ? formatCurrencyForCSV(budget.quarter_2_sales) : '0.00',
                q3_budget: budget ? formatCurrencyForCSV(budget.quarter_3_sales) : '0.00',
                q4_budget: budget ? formatCurrencyForCSV(budget.quarter_4_sales) : '0.00'
            };
        });
        
        return combinedData;
    } catch (error) {
        console.error('Error fetching salesperson data:', error);
        return null;
    }
};

onMounted(() => {
    fetchAdminSummary();
});
</script>

<style scoped>
.admin-view {
    padding: 2rem;
    max-width: 100%;
    overflow-x: auto;
}

.header {
    margin-bottom: 2rem;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
}

.header-text h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.subtitle {
    color: #7f8c8d;
    font-size: 1.1rem;
}

.header-actions {
    flex-shrink: 0;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

.error {
    text-align: center;
    padding: 2rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    color: #721c24;
}

.retry-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
}

.retry-btn:hover {
    background-color: #c82333;
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.stat-card h3 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 0.9rem;
    font-weight: 600;
}

.stat-number {
    font-size: 1.8rem;
    font-weight: bold;
    margin: 0;
    color: #2c3e50;
}

.stat-number.positive {
    color: #27ae60;
}

.stat-number.negative {
    color: #e74c3c;
}

.table-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-x: auto;
}

.admin-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1200px;
}

.admin-table th {
    background-color: #f8f9fa;
    padding: 1rem 0.75rem;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    border-bottom: 2px solid #dee2e6;
    position: sticky;
    top: 0;
    z-index: 10;
}

.admin-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #dee2e6;
    vertical-align: top;
}

.data-row:hover {
    background-color: #f8f9fa;
}

.salesperson-name {
    min-width: 150px;
}

.salesperson-name .name {
    display: block;
    font-weight: 600;
    color: #2c3e50;
}

.salesperson-name .id {
    display: block;
    font-size: 0.8rem;
    color: #7f8c8d;
}

.role {
    min-width: 120px;
    color: #7f8c8d;
}

.number {
    text-align: right;
    font-family: "Courier New", monospace;
    min-width: 100px;
}

.total-sales {
    font-weight: 600;
    background-color: #e8f5e8;
}

.total-budget {
    font-weight: 600;
    background-color: #e8f4fd;
}

.zero-perc {
    display: block;
}

.zero-perc small {
    display: block;
    color: #7f8c8d;
    font-size: 0.8rem;
}

.variance {
    font-weight: 600;
}

.variance.positive {
    color: #27ae60;
}

.variance.negative {
    color: #e74c3c;
}

.group-header {
    background-color: #f8f9fa;
    border-top: 2px solid #dee2e6;
}

.group-title {
    font-size: 1.1rem;
    color: #2c3e50;
    padding: 1rem 0.75rem;
    text-align: left;
}

.hospitality-group .group-title {
    background-color: #e8f5e8;
    color: #155724;
}

.non-hospitality-group .group-title {
    background-color: #e8f4fd;
    color: #004085;
}

.group-subtotal {
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
}

.hospitality-subtotal {
    background-color: #d4edda;
    border-color: #c3e6cb;
}

.non-hospitality-subtotal {
    background-color: #d1ecf1;
    border-color: #bee5eb;
}

.subtotal-label {
    font-weight: bold;
    color: #2c3e50;
}

.subtotal-count {
    color: #6c757d;
    font-size: 0.9rem;
}

.action-buttons {
    text-align: center;
    min-width: 120px;
}

.action-buttons .btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}

@media (max-width: 768px) {
    .admin-view {
        padding: 1rem;
    }

    .header-content {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }

    .header-actions {
        align-self: flex-start;
    }

    .summary-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .admin-table {
        font-size: 0.9rem;
    }

    .admin-table th,
    .admin-table td {
        padding: 0.5rem 0.25rem;
    }
}
</style>
