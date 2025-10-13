<template>
    <div class="overflow-x-auto">
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
                    <th>Budget Q1</th>
                    <th>Budget Q2</th>
                    <th>Budget Q3</th>
                    <th>Budget Q4</th>
                </tr>
            </thead>
            <tbody>
                <!-- Regular Sales Rows -->
                <tr
                    v-for="sale in sales"
                    :key="`${sale.customer_name}-${sale.brand || 'null'}-${sale.flag || 'null'}`"
                >
                    <td>{{ sale.brand || 'N/A' }}</td>
                    <td>{{ sale.flag || 'N/A' }}</td>
                    <td class="font-medium">
                        {{ sale.customer_name || 'N/A' }}
                    </td>
                    <td>{{ sale.derived_customer_class || 'N/A' }}</td>
                    <td class="text-right">
                        ${{ formatCurrency(sale.q1_sales) }}
                    </td>
                    <td class="text-right">
                        ${{ formatCurrency(sale.q2_sales) }}
                    </td>
                    <td class="text-right">
                        ${{ formatCurrency(sale.q3_sales) }}
                    </td>
                    <td class="text-right">
                        ${{ formatCurrency(sale.q4_sales) }}
                    </td>
                    <td class="text-right">
                        ${{ formatCurrency(sale.zero_perc_sales_total) }}
                    </td>
                    <td class="text-right font-semibold">
                        ${{ formatCurrency(sale.total_sales) }}
                    </td>
                    <td class="text-right">
                        <span :class="getZeroPercentClass(sale.zero_perc_sales_percent)">
                            {{ formatPercentage(sale.zero_perc_sales_percent) }}%
                        </span>
                    </td>
                    <td :class="getCellClass(sale, 1)">
                        <BudgetInput
                            :value="getBudgetValue(sale, 1)"
                            :cell-class="getCellClass(sale, 1)"
                            @change="(event) => handleBudgetChange(event, sale, 1)"
                            @blur="(event) => handleBudgetBlur(event, sale, 1)"
                            @input="(event) => handleBudgetInput(event, sale, 1)"
                        />
                    </td>
                    <td :class="getCellClass(sale, 2)">
                        <BudgetInput
                            :value="getBudgetValue(sale, 2)"
                            :cell-class="getCellClass(sale, 2)"
                            @change="(event) => handleBudgetChange(event, sale, 2)"
                            @blur="(event) => handleBudgetBlur(event, sale, 2)"
                            @input="(event) => handleBudgetInput(event, sale, 2)"
                        />
                    </td>
                    <td :class="getCellClass(sale, 3)">
                        <BudgetInput
                            :value="getBudgetValue(sale, 3)"
                            :cell-class="getCellClass(sale, 3)"
                            @change="(event) => handleBudgetChange(event, sale, 3)"
                            @blur="(event) => handleBudgetBlur(event, sale, 3)"
                            @input="(event) => handleBudgetInput(event, sale, 3)"
                        />
                    </td>
                    <td :class="getCellClass(sale, 4)">
                        <BudgetInput
                            :value="getBudgetValue(sale, 4)"
                            :cell-class="getCellClass(sale, 4)"
                            @change="(event) => handleBudgetChange(event, sale, 4)"
                            @blur="(event) => handleBudgetBlur(event, sale, 4)"
                            @input="(event) => handleBudgetInput(event, sale, 4)"
                        />
                    </td>
                </tr>

                <!-- Custom Budget Rows -->
                <tr
                    v-for="budget in customBudgets"
                    :key="`custom-${budget.id}`"
                    class="bg-amber-50/30"
                >
                    <td>{{ budget.brand || 'N/A' }}</td>
                    <td>{{ budget.flag || 'N/A' }}</td>
                    <td class="font-medium">
                        <div class="flex items-center gap-2">
                            {{ budget.customer_name || 'N/A' }}
                            <button
                                @click="handleDeleteCustomBudget(budget.id)"
                                class="btn btn-ghost btn-xs text-error hover:bg-error hover:text-error-content"
                                title="Delete custom budget"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    </td>
                    <td>{{ budget.customer_class || 'N/A' }}</td>
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
                            @change="(event) => handleBudgetChange(event, budget, 1)"
                            @blur="(event) => handleBudgetBlur(event, budget, 1)"
                            @input="(event) => handleBudgetInput(event, budget, 1)"
                        />
                    </td>
                    <td :class="getCellClass(budget, 2)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 2)"
                            :cell-class="getCellClass(budget, 2)"
                            @change="(event) => handleBudgetChange(event, budget, 2)"
                            @blur="(event) => handleBudgetBlur(event, budget, 2)"
                            @input="(event) => handleBudgetInput(event, budget, 2)"
                        />
                    </td>
                    <td :class="getCellClass(budget, 3)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 3)"
                            :cell-class="getCellClass(budget, 3)"
                            @change="(event) => handleBudgetChange(event, budget, 3)"
                            @blur="(event) => handleBudgetBlur(event, budget, 3)"
                            @input="(event) => handleBudgetInput(event, budget, 3)"
                        />
                    </td>
                    <td :class="getCellClass(budget, 4)">
                        <BudgetInput
                            :value="getBudgetValue(budget, 4)"
                            :cell-class="getCellClass(budget, 4)"
                            @change="(event) => handleBudgetChange(event, budget, 4)"
                            @blur="(event) => handleBudgetBlur(event, budget, 4)"
                            @input="(event) => handleBudgetInput(event, budget, 4)"
                        />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import BudgetInput from './BudgetInput.vue';
import { formatCurrency, formatPercentage, getZeroPercentClass } from '@/utils/formatters';

const props = defineProps({
    sales: {
        type: Array,
        required: true
    },
    customBudgets: {
        type: Array,
        default: () => []
    },
    getBudgetValue: {
        type: Function,
        required: true
    },
    getCellClass: {
        type: Function,
        required: true
    },
    handleBudgetChange: {
        type: Function,
        required: true
    },
    handleBudgetBlur: {
        type: Function,
        required: true
    },
    handleBudgetInput: {
        type: Function,
        required: true
    },
    handleDeleteCustomBudget: {
        type: Function,
        required: true
    }
});
</script>
