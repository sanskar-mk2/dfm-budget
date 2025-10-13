<template>
    <div class="relative">
        <!-- Sticky horizontal scroll bar at top -->
        <div class="sticky top-0 z-20 bg-base-100 border-b border-gray-200">
            <div class="overflow-x-auto h-4">
                <div class="h-4" :style="{ width: tableWidth + 'px' }"></div>
            </div>
        </div>

        <!-- Main table with scroll -->
        <div class="overflow-x-auto">
            <table ref="tableRef" class="table-sm table w-full">
                <thead>
                    <tr>
                        <th></th>
                        <th
                            v-if="isHospitality"
                            class="sticky left-0 bg-base-100 z-10"
                        >
                            Brand
                        </th>
                        <th
                            v-if="isHospitality"
                            class="sticky left-16 bg-base-100 z-10"
                        >
                            Flag
                        </th>
                        <th
                            v-if="!isHospitality"
                            class="sticky left-0 bg-base-100 z-10"
                        >
                            Customer Class
                        </th>
                        <th
                            v-if="!isHospitality"
                            class="sticky left-32 bg-base-100 z-10"
                        >
                            Customer Name
                        </th>
                        <th>Q1 Sales</th>
                        <th>Q2 Sales</th>
                        <th>Q3 Sales</th>
                        <th>Q4 Orders</th>
                        <th>Total Sales</th>
                        <th v-if="isHospitality">0% Sales (Rate)</th>
                        <th>Budget Q1</th>
                        <th>Budget Q2</th>
                        <th>Budget Q3</th>
                        <th>Budget Q4</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Grouped Sales Rows with Subtotals -->
                    <template
                        v-for="item in groupedSalesData"
                        :key="
                            item.isSubtotal
                                ? `subtotal-${item.groupKey}`
                                : `${item.customer_name}-${
                                      item.brand || 'null'
                                  }-${item.flag || 'null'}`
                        "
                    >
                        <!-- Regular Sales Row -->
                        <tr v-if="!item.isSubtotal">
                            <td></td>
                            <td
                                v-if="isHospitality"
                                class="sticky left-0 bg-base-100 z-10"
                            >
                                {{ item.brand || "N/A" }}
                            </td>
                            <td
                                v-if="isHospitality"
                                class="sticky left-16 bg-base-100 z-10"
                            >
                                {{ item.flag || "N/A" }}
                            </td>
                            <td
                                v-if="!isHospitality"
                                class="sticky left-0 bg-base-100 z-10"
                            >
                                {{ item.derived_customer_class || "N/A" }}
                            </td>
                            <td
                                v-if="!isHospitality"
                                class="sticky left-32 bg-base-100 z-10"
                            >
                                {{ item.customer_name || "N/A" }}
                            </td>
                            <td class="text-right">
                                ${{ formatCurrency(item.q1_sales) }}
                            </td>
                            <td class="text-right">
                                ${{ formatCurrency(item.q2_sales) }}
                            </td>
                            <td class="text-right">
                                ${{ formatCurrency(item.q3_sales) }}
                            </td>
                            <td class="text-right">
                                ${{ formatCurrency(item.q4_sales) }}
                            </td>
                            <td class="text-right font-semibold">
                                ${{ formatCurrency(item.total_sales) }}
                            </td>
                            <td v-if="isHospitality" class="text-right">
                                ${{
                                    formatCurrency(item.zero_perc_sales_total)
                                }}
                                ({{
                                    formatPercentage(
                                        item.zero_perc_sales_percent
                                    )
                                }}%)
                            </td>
                            <td
                                :class="getCellClass(item, 1)"
                                class="text-right"
                            >
                                <BudgetInput
                                    :value="getBudgetValue(item, 1)"
                                    :cell-class="getCellClass(item, 1)"
                                    @change="
                                        (event) =>
                                            handleBudgetChange(event, item, 1)
                                    "
                                    @blur="
                                        (event) =>
                                            handleBudgetBlur(event, item, 1)
                                    "
                                    @input="
                                        (event) =>
                                            handleBudgetInput(event, item, 1)
                                    "
                                />
                            </td>
                            <td
                                :class="getCellClass(item, 2)"
                                class="text-right"
                            >
                                <BudgetInput
                                    :value="getBudgetValue(item, 2)"
                                    :cell-class="getCellClass(item, 2)"
                                    @change="
                                        (event) =>
                                            handleBudgetChange(event, item, 2)
                                    "
                                    @blur="
                                        (event) =>
                                            handleBudgetBlur(event, item, 2)
                                    "
                                    @input="
                                        (event) =>
                                            handleBudgetInput(event, item, 2)
                                    "
                                />
                            </td>
                            <td
                                :class="getCellClass(item, 3)"
                                class="text-right"
                            >
                                <BudgetInput
                                    :value="getBudgetValue(item, 3)"
                                    :cell-class="getCellClass(item, 3)"
                                    @change="
                                        (event) =>
                                            handleBudgetChange(event, item, 3)
                                    "
                                    @blur="
                                        (event) =>
                                            handleBudgetBlur(event, item, 3)
                                    "
                                    @input="
                                        (event) =>
                                            handleBudgetInput(event, item, 3)
                                    "
                                />
                            </td>
                            <td
                                :class="getCellClass(item, 4)"
                                class="text-right"
                            >
                                <BudgetInput
                                    :value="getBudgetValue(item, 4)"
                                    :cell-class="getCellClass(item, 4)"
                                    @change="
                                        (event) =>
                                            handleBudgetChange(event, item, 4)
                                    "
                                    @blur="
                                        (event) =>
                                            handleBudgetBlur(event, item, 4)
                                    "
                                    @input="
                                        (event) =>
                                            handleBudgetInput(event, item, 4)
                                    "
                                />
                            </td>
                        </tr>

                        <!-- Subtotal Row -->
                        <tr
                            v-else
                            class="bg-blue-50 border-t-2 border-b-4 border-primary"
                        >
                            <td
                                colspan="3"
                                class="font-bold text-secondary-content text-center sticky left-0 bg-secondary z-10"
                            >
                                {{ item.groupKey }} Total
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q1_sales) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q2_sales) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q3_sales) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q4_sales) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.total_sales) }}
                            </td>
                            <td
                                v-if="isHospitality"
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{
                                    formatCurrency(item.zero_perc_sales_total)
                                }}
                                ({{
                                    formatPercentage(
                                        item.zero_perc_sales_percent
                                    )
                                }}%)
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q1_budget) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q2_budget) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q3_budget) }}
                            </td>
                            <td
                                class="text-right font-bold text-base-content bg-secondary/50"
                            >
                                ${{ formatCurrency(item.q4_budget) }}
                            </td>
                        </tr>
                    </template>

                    <!-- Custom Budget Rows -->
                    <tr
                        v-for="budget in customBudgets"
                        :key="`custom-${budget.id}`"
                    >
                        <td>
                            <button
                                @click="handleDeleteCustomBudget(budget.id)"
                                class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content"
                                title="Delete custom budget"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    class="h-4 w-4"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                    />
                                </svg>
                            </button>
                        </td>
                        <td
                            v-if="isHospitality"
                            class="sticky left-0 bg-base-100 z-10"
                        >
                            {{ budget.brand || "N/A" }}
                        </td>
                        <td
                            v-if="isHospitality"
                            class="sticky left-16 bg-base-100 z-10"
                        >
                            {{ budget.flag || "N/A" }}
                        </td>
                        <td
                            v-if="!isHospitality"
                            class="sticky left-0 bg-base-100 z-10"
                        >
                            {{ budget.customer_class || "N/A" }}
                        </td>
                        <td
                            v-if="!isHospitality"
                            class="sticky left-32 bg-base-100 z-10"
                        >
                            {{ budget.customer_name || "N/A" }}
                        </td>
                        <td class="text-right">$0.00</td>
                        <td class="text-right">$0.00</td>
                        <td class="text-right">$0.00</td>
                        <td class="text-right">$0.00</td>
                        <td class="text-right font-semibold">$0.00</td>
                        <td v-if="isHospitality" class="text-right">
                            $0.00 (0.00%)
                        </td>
                        <td :class="getCellClass(budget, 1)" class="text-right">
                            <BudgetInput
                                :value="getBudgetValue(budget, 1)"
                                :cell-class="getCellClass(budget, 1)"
                                @change="
                                    (event) =>
                                        handleBudgetChange(event, budget, 1)
                                "
                                @blur="
                                    (event) =>
                                        handleBudgetBlur(event, budget, 1)
                                "
                                @input="
                                    (event) =>
                                        handleBudgetInput(event, budget, 1)
                                "
                            />
                        </td>
                        <td :class="getCellClass(budget, 2)" class="text-right">
                            <BudgetInput
                                :value="getBudgetValue(budget, 2)"
                                :cell-class="getCellClass(budget, 2)"
                                @change="
                                    (event) =>
                                        handleBudgetChange(event, budget, 2)
                                "
                                @blur="
                                    (event) =>
                                        handleBudgetBlur(event, budget, 2)
                                "
                                @input="
                                    (event) =>
                                        handleBudgetInput(event, budget, 2)
                                "
                            />
                        </td>
                        <td :class="getCellClass(budget, 3)" class="text-right">
                            <BudgetInput
                                :value="getBudgetValue(budget, 3)"
                                :cell-class="getCellClass(budget, 3)"
                                @change="
                                    (event) =>
                                        handleBudgetChange(event, budget, 3)
                                "
                                @blur="
                                    (event) =>
                                        handleBudgetBlur(event, budget, 3)
                                "
                                @input="
                                    (event) =>
                                        handleBudgetInput(event, budget, 3)
                                "
                            />
                        </td>
                        <td :class="getCellClass(budget, 4)" class="text-right">
                            <BudgetInput
                                :value="getBudgetValue(budget, 4)"
                                :cell-class="getCellClass(budget, 4)"
                                @change="
                                    (event) =>
                                        handleBudgetChange(event, budget, 4)
                                "
                                @blur="
                                    (event) =>
                                        handleBudgetBlur(event, budget, 4)
                                "
                                @input="
                                    (event) =>
                                        handleBudgetInput(event, budget, 4)
                                "
                            />
                        </td>
                    </tr>

                    <!-- Total Row -->
                    <tr class="border-t-4 border-gray-400">
                        <td
                            colspan="3"
                            v-if="isHospitality"
                            class="font-bold bg-primary text-center text-primary-content text-md sticky left-0 z-10"
                        >
                            TOTAL
                        </td>
                        <td
                            v-if="!isHospitality"
                            class="sticky left-32 text-base-content bg-primary/50 font-bold text-md z-10"
                        ></td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ1()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ2()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ3()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ4()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalSales()) }}
                        </td>
                        <td
                            v-if="isHospitality"
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalZeroPercent()) }} ({{
                                getZeroPercentRate().toFixed(2)
                            }}%)
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ1Budget()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ2Budget()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ3Budget()) }}
                        </td>
                        <td
                            class="text-right font-bold text-md text-base-content bg-primary/50"
                        >
                            ${{ formatCurrency(getTotalQ4Budget()) }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue";
import BudgetInput from "./BudgetInput.vue";
import { formatCurrency, formatPercentage } from "@/utils/formatters";

const props = defineProps({
    sales: {
        type: Array,
        required: true,
    },
    customBudgets: {
        type: Array,
        default: () => [],
    },
    getBudgetValue: {
        type: Function,
        required: true,
    },
    getCellClass: {
        type: Function,
        required: true,
    },
    handleBudgetChange: {
        type: Function,
        required: true,
    },
    handleBudgetBlur: {
        type: Function,
        required: true,
    },
    handleBudgetInput: {
        type: Function,
        required: true,
    },
    handleDeleteCustomBudget: {
        type: Function,
        required: true,
    },
    isHospitality: {
        type: Boolean,
        required: true,
    },
    getTotalQ1: {
        type: Function,
        required: true,
    },
    getTotalQ2: {
        type: Function,
        required: true,
    },
    getTotalQ3: {
        type: Function,
        required: true,
    },
    getTotalQ4: {
        type: Function,
        required: true,
    },
    getTotalSales: {
        type: Function,
        required: true,
    },
    getTotalZeroPercent: {
        type: Function,
        required: true,
    },
    getZeroPercentRate: {
        type: Function,
        required: true,
    },
    getTotalQ1Budget: {
        type: Function,
        required: false,
    },
    getTotalQ2Budget: {
        type: Function,
        required: false,
    },
    getTotalQ3Budget: {
        type: Function,
        required: false,
    },
    getTotalQ4Budget: {
        type: Function,
        required: false,
    },
});

// Group sales data by Brand (hospitality) or Customer Class (non-hospitality)
// Maintains the backend sort order: Brand DESC, Flag DESC, Customer Name DESC for hospitality
const groupedSalesData = computed(() => {
    const groups = {};
    const groupOrder = []; // Track order of groups as they appear in the data

    props.sales.forEach((sale) => {
        const groupKey = props.isHospitality
            ? sale.brand || "Unknown Brand"
            : sale.derived_customer_class || "Unknown Class";

        if (!groups[groupKey]) {
            groups[groupKey] = [];
            groupOrder.push(groupKey); // Track first occurrence order
        }
        groups[groupKey].push(sale);
    });

    // Convert to array with subtotals, maintaining the order from backend
    const result = [];
    groupOrder.forEach((groupKey) => {
        const groupSales = groups[groupKey];

        // Add all sales in this group (already sorted by backend)
        groupSales.forEach((sale) => {
            result.push({ ...sale, isSubtotal: false });
        });

        // Calculate subtotal for this group
        const subtotal = {
            isSubtotal: true,
            groupKey,
            q1_sales: groupSales.reduce(
                (sum, sale) => sum + (parseFloat(sale.q1_sales) || 0),
                0
            ),
            q2_sales: groupSales.reduce(
                (sum, sale) => sum + (parseFloat(sale.q2_sales) || 0),
                0
            ),
            q3_sales: groupSales.reduce(
                (sum, sale) => sum + (parseFloat(sale.q3_sales) || 0),
                0
            ),
            q4_sales: groupSales.reduce(
                (sum, sale) => sum + (parseFloat(sale.q4_sales) || 0),
                0
            ),
            zero_perc_sales_total: groupSales.reduce(
                (sum, sale) =>
                    sum + (parseFloat(sale.zero_perc_sales_total) || 0),
                0
            ),
            total_sales: groupSales.reduce(
                (sum, sale) => sum + (parseFloat(sale.total_sales) || 0),
                0
            ),
            zero_perc_sales_percent: 0, // Will be calculated
            // Calculate budget totals for this group
            q1_budget: groupSales.reduce(
                (sum, sale) =>
                    sum + (parseFloat(props.getBudgetValue(sale, 1)) || 0),
                0
            ),
            q2_budget: groupSales.reduce(
                (sum, sale) =>
                    sum + (parseFloat(props.getBudgetValue(sale, 2)) || 0),
                0
            ),
            q3_budget: groupSales.reduce(
                (sum, sale) =>
                    sum + (parseFloat(props.getBudgetValue(sale, 3)) || 0),
                0
            ),
            q4_budget: groupSales.reduce(
                (sum, sale) =>
                    sum + (parseFloat(props.getBudgetValue(sale, 4)) || 0),
                0
            ),
        };

        // Calculate zero percent percentage for subtotal
        subtotal.zero_perc_sales_percent =
            subtotal.total_sales > 0
                ? (subtotal.zero_perc_sales_total / subtotal.total_sales) * 100
                : 0;

        result.push(subtotal);
    });

    return result;
});

// Scroll synchronization
const tableRef = ref(null);
const tableWidth = ref(1200); // Default width

const syncScroll = (source, target) => {
    if (source && target) {
        target.scrollLeft = source.scrollLeft;
    }
};

onMounted(() => {
    // Set initial table width
    if (tableRef.value) {
        tableWidth.value = tableRef.value.scrollWidth;
    }

    // Add scroll event listeners
    const topScrollBar = document.querySelector(".sticky .overflow-x-auto");
    const mainScrollContainer = document.querySelector(
        ".overflow-x-auto:not(.sticky .overflow-x-auto)"
    );

    if (topScrollBar && mainScrollContainer) {
        topScrollBar.addEventListener("scroll", () =>
            syncScroll(topScrollBar, mainScrollContainer)
        );
        mainScrollContainer.addEventListener("scroll", () =>
            syncScroll(mainScrollContainer, topScrollBar)
        );
    }
});

onUnmounted(() => {
    // Clean up event listeners
    const topScrollBar = document.querySelector(".sticky .overflow-x-auto");
    const mainScrollContainer = document.querySelector(
        ".overflow-x-auto:not(.sticky .overflow-x-auto)"
    );

    if (topScrollBar && mainScrollContainer) {
        topScrollBar.removeEventListener("scroll", () =>
            syncScroll(topScrollBar, mainScrollContainer)
        );
        mainScrollContainer.removeEventListener("scroll", () =>
            syncScroll(mainScrollContainer, topScrollBar)
        );
    }
});
</script>
