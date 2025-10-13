<template>
    <div class="overflow-x-auto">
        <table class="table-md table table-zebra w-full">
            <thead>
                <tr>
                    <th v-if="isHospitality">Brand</th>
                    <th v-if="isHospitality">Flag</th>
                    <th v-if="!isHospitality">Customer Class</th>
                    <th v-if="!isHospitality">Customer Name</th>
                    <th>Q1 Sales</th>
                    <th>Q2 Sales</th>
                    <th>Q3 Sales</th>
                    <th>Q4 Sales</th>
                    <th>Zero % Sales</th>
                    <th>Total Sales</th>
                    <th>Zero % %</th>
                    <th>Budget Q1</th>
                    <th>Budget Q2</th>
                    <th>Budget Q3</th>
                    <th>Budget Q4</th>
                </tr>
            </thead>
            <tbody>
                <!-- Grouped Sales Rows with Subtotals -->
                <template v-for="item in groupedSalesData" :key="item.isSubtotal ? `subtotal-${item.groupKey}` : `${item.customer_name}-${item.brand || 'null'}-${item.flag || 'null'}`">
                    <!-- Regular Sales Row -->
                    <tr v-if="!item.isSubtotal">
                        <td v-if="isHospitality">{{ item.brand || "N/A" }}</td>
                        <td v-if="isHospitality">{{ item.flag || "N/A" }}</td>
                        <td v-if="!isHospitality">{{ item.derived_customer_class || "N/A" }}</td>
                        <td v-if="!isHospitality" class="font-medium">
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
                        <td class="text-right">
                            ${{ formatCurrency(item.zero_perc_sales_total) }}
                        </td>
                        <td class="text-right font-semibold">
                            ${{ formatCurrency(item.total_sales) }}
                        </td>
                        <td class="text-right">
                            <span
                                :class="
                                    getZeroPercentClass(
                                        item.zero_perc_sales_percent
                                    )
                                "
                            >
                                {{
                                    formatPercentage(item.zero_perc_sales_percent)
                                }}%
                            </span>
                        </td>
                        <td :class="getCellClass(item, 1)">
                            <BudgetInput
                                :value="getBudgetValue(item, 1)"
                                :cell-class="getCellClass(item, 1)"
                                @change="
                                    (event) => handleBudgetChange(event, item, 1)
                                "
                                @blur="(event) => handleBudgetBlur(event, item, 1)"
                                @input="
                                    (event) => handleBudgetInput(event, item, 1)
                                "
                            />
                        </td>
                        <td :class="getCellClass(item, 2)">
                            <BudgetInput
                                :value="getBudgetValue(item, 2)"
                                :cell-class="getCellClass(item, 2)"
                                @change="
                                    (event) => handleBudgetChange(event, item, 2)
                                "
                                @blur="(event) => handleBudgetBlur(event, item, 2)"
                                @input="
                                    (event) => handleBudgetInput(event, item, 2)
                                "
                            />
                        </td>
                        <td :class="getCellClass(item, 3)">
                            <BudgetInput
                                :value="getBudgetValue(item, 3)"
                                :cell-class="getCellClass(item, 3)"
                                @change="
                                    (event) => handleBudgetChange(event, item, 3)
                                "
                                @blur="(event) => handleBudgetBlur(event, item, 3)"
                                @input="
                                    (event) => handleBudgetInput(event, item, 3)
                                "
                            />
                        </td>
                        <td :class="getCellClass(item, 4)">
                            <BudgetInput
                                :value="getBudgetValue(item, 4)"
                                :cell-class="getCellClass(item, 4)"
                                @change="
                                    (event) => handleBudgetChange(event, item, 4)
                                "
                                @blur="(event) => handleBudgetBlur(event, item, 4)"
                                @input="
                                    (event) => handleBudgetInput(event, item, 4)
                                "
                            />
                        </td>
                    </tr>
                    
                    <!-- Subtotal Row -->
                    <tr v-else class="bg-blue-50 border-t-2 border-blue-200">
                        <td v-if="isHospitality" class="font-bold text-blue-800">
                            {{ item.groupKey }} Total
                        </td>
                        <td v-if="isHospitality"></td>
                        <td v-if="!isHospitality" class="font-bold text-blue-800">
                            {{ item.groupKey }} Total
                        </td>
                        <td v-if="!isHospitality"></td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q1_sales) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q2_sales) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q3_sales) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q4_sales) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.zero_perc_sales_total) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.total_sales) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            <span
                                :class="
                                    getZeroPercentClass(
                                        item.zero_perc_sales_percent
                                    )
                                "
                            >
                                {{
                                    formatPercentage(item.zero_perc_sales_percent)
                                }}%
                            </span>
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q1_budget) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q2_budget) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q3_budget) }}
                        </td>
                        <td class="text-right font-bold text-blue-800">
                            ${{ formatCurrency(item.q4_budget) }}
                        </td>
                    </tr>
                </template>

                <!-- Custom Budget Rows -->
                <tr
                    v-for="budget in customBudgets"
                    :key="`custom-${budget.id}`"
                    class="bg-amber-50/30"
                >
                    <td v-if="isHospitality">{{ budget.brand || "N/A" }}</td>
                    <td v-if="isHospitality">{{ budget.flag || "N/A" }}</td>
                    <td v-if="!isHospitality">{{ budget.customer_class || "N/A" }}</td>
                    <td v-if="!isHospitality" class="font-medium">
                        <div class="flex items-center gap-2">
                            {{ budget.customer_name || "N/A" }}
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
                        </div>
                    </td>
                    <td class="text-right">$0.00</td>
                    <td class="text-right">$0.00</td>
                    <td class="text-right">$0.00</td>
                    <td class="text-right">$0.00</td>
                    <td class="text-right">$0.00</td>
                    <td class="text-right font-semibold">$0.00</td>
                    <td class="text-right">0%</td>
                    <td :class="getCellClass(budget, 1)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 1)"
                            :cell-class="getCellClass(budget, 1)"
                            @change="
                                (event) => handleBudgetChange(event, budget, 1)
                            "
                            @blur="
                                (event) => handleBudgetBlur(event, budget, 1)
                            "
                            @input="
                                (event) => handleBudgetInput(event, budget, 1)
                            "
                        />
                    </td>
                    <td :class="getCellClass(budget, 2)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 2)"
                            :cell-class="getCellClass(budget, 2)"
                            @change="
                                (event) => handleBudgetChange(event, budget, 2)
                            "
                            @blur="
                                (event) => handleBudgetBlur(event, budget, 2)
                            "
                            @input="
                                (event) => handleBudgetInput(event, budget, 2)
                            "
                        />
                    </td>
                    <td :class="getCellClass(budget, 3)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 3)"
                            :cell-class="getCellClass(budget, 3)"
                            @change="
                                (event) => handleBudgetChange(event, budget, 3)
                            "
                            @blur="
                                (event) => handleBudgetBlur(event, budget, 3)
                            "
                            @input="
                                (event) => handleBudgetInput(event, budget, 3)
                            "
                        />
                    </td>
                    <td :class="getCellClass(budget, 4)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 4)"
                            :cell-class="getCellClass(budget, 4)"
                            @change="
                                (event) => handleBudgetChange(event, budget, 4)
                            "
                            @blur="
                                (event) => handleBudgetBlur(event, budget, 4)
                            "
                            @input="
                                (event) => handleBudgetInput(event, budget, 4)
                            "
                        />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { computed } from "vue";
import BudgetInput from "./BudgetInput.vue";
import {
    formatCurrency,
    formatPercentage,
    getZeroPercentClass,
} from "@/utils/formatters";

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
});

// Group sales data by Brand (hospitality) or Customer Class (non-hospitality)
// Maintains the backend sort order: Brand DESC, Flag DESC, Customer Name DESC for hospitality
const groupedSalesData = computed(() => {
    const groups = {};
    const groupOrder = []; // Track order of groups as they appear in the data
    
    props.sales.forEach(sale => {
        const groupKey = props.isHospitality 
            ? (sale.brand || 'Unknown Brand')
            : (sale.derived_customer_class || 'Unknown Class');
        
        if (!groups[groupKey]) {
            groups[groupKey] = [];
            groupOrder.push(groupKey); // Track first occurrence order
        }
        groups[groupKey].push(sale);
    });
    
    // Convert to array with subtotals, maintaining the order from backend
    const result = [];
    groupOrder.forEach(groupKey => {
        const groupSales = groups[groupKey];
        
        // Add all sales in this group (already sorted by backend)
        groupSales.forEach(sale => {
            result.push({ ...sale, isSubtotal: false });
        });
        
        // Calculate subtotal for this group
        const subtotal = {
            isSubtotal: true,
            groupKey,
            q1_sales: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.q1_sales) || 0), 0),
            q2_sales: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.q2_sales) || 0), 0),
            q3_sales: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.q3_sales) || 0), 0),
            q4_sales: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.q4_sales) || 0), 0),
            zero_perc_sales_total: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.zero_perc_sales_total) || 0), 0),
            total_sales: groupSales.reduce((sum, sale) => sum + (parseFloat(sale.total_sales) || 0), 0),
            zero_perc_sales_percent: 0, // Will be calculated
            // Calculate budget totals for this group
            q1_budget: groupSales.reduce((sum, sale) => sum + (parseFloat(props.getBudgetValue(sale, 1)) || 0), 0),
            q2_budget: groupSales.reduce((sum, sale) => sum + (parseFloat(props.getBudgetValue(sale, 2)) || 0), 0),
            q3_budget: groupSales.reduce((sum, sale) => sum + (parseFloat(props.getBudgetValue(sale, 3)) || 0), 0),
            q4_budget: groupSales.reduce((sum, sale) => sum + (parseFloat(props.getBudgetValue(sale, 4)) || 0), 0)
        };
        
        // Calculate zero percent percentage for subtotal
        subtotal.zero_perc_sales_percent = subtotal.total_sales > 0 
            ? (subtotal.zero_perc_sales_total / subtotal.total_sales) * 100 
            : 0;
            
        result.push(subtotal);
    });
    
    return result;
});
</script>
