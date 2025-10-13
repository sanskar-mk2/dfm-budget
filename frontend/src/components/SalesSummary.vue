<template>
    <div v-if="sales.length > 0" class="mt-8 p-4 bg-base-200 rounded-lg">
        <h3 class="text-lg font-semibold mb-4">Sales & Budget Summary</h3>
        
        <!-- Sales Summary -->
        <div class="mb-6">
            <h4 class="text-md font-medium mb-3 text-primary">Sales</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat">
                    <div class="stat-title">Total Customers</div>
                    <div class="stat-value text-primary">
                        {{ sales.length }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q1 Sales</div>
                    <div class="stat-value text-info">
                        ${{ formatCurrency(getTotalQ1()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q2 Sales</div>
                    <div class="stat-value text-info">
                        ${{ formatCurrency(getTotalQ2()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q3 Sales</div>
                    <div class="stat-value text-info">
                        ${{ formatCurrency(getTotalQ3()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q4 Sales</div>
                    <div class="stat-value text-info">
                        ${{ formatCurrency(getTotalQ4()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Sales</div>
                    <div class="stat-value text-success">
                        ${{ formatCurrency(getTotalSales()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Zero % Sales</div>
                    <div class="stat-value text-warning">
                        ${{ formatCurrency(getTotalZeroPercent()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Zero % Rate</div>
                    <div class="stat-value" :class="getZeroPercentClass(getZeroPercentRate())">
                        {{ getZeroPercentRate().toFixed(2) }}%
                    </div>
                </div>
            </div>
        </div>

        <!-- Budget Summary -->
        <div v-if="getTotalQ1Budget" class="mb-6">
            <h4 class="text-md font-medium mb-3 text-secondary">Budget</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat">
                    <div class="stat-title">Q1 Budget</div>
                    <div class="stat-value text-secondary">
                        ${{ formatCurrency(getTotalQ1Budget()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q2 Budget</div>
                    <div class="stat-value text-secondary">
                        ${{ formatCurrency(getTotalQ2Budget()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q3 Budget</div>
                    <div class="stat-value text-secondary">
                        ${{ formatCurrency(getTotalQ3Budget()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Q4 Budget</div>
                    <div class="stat-value text-secondary">
                        ${{ formatCurrency(getTotalQ4Budget()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Budget</div>
                    <div class="stat-value text-accent">
                        ${{ formatCurrency(getTotalBudget()) }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Variance</div>
                    <div class="stat-value" :class="getVarianceClass(getTotalSales() - getTotalBudget())">
                        ${{ formatCurrency(getTotalSales() - getTotalBudget()) }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { formatCurrency, getZeroPercentClass } from '@/utils/formatters';

defineProps({
    sales: {
        type: Array,
        required: true
    },
    getTotalQ1: {
        type: Function,
        required: true
    },
    getTotalQ2: {
        type: Function,
        required: true
    },
    getTotalQ3: {
        type: Function,
        required: true
    },
    getTotalQ4: {
        type: Function,
        required: true
    },
    getTotalSales: {
        type: Function,
        required: true
    },
    getTotalZeroPercent: {
        type: Function,
        required: true
    },
    getZeroPercentRate: {
        type: Function,
        required: true
    },
    getTotalQ1Budget: {
        type: Function,
        required: false
    },
    getTotalQ2Budget: {
        type: Function,
        required: false
    },
    getTotalQ3Budget: {
        type: Function,
        required: false
    },
    getTotalQ4Budget: {
        type: Function,
        required: false
    },
    getTotalBudget: {
        type: Function,
        required: false
    }
});

const getVarianceClass = (variance) => {
    if (variance > 0) return 'text-success';
    if (variance < 0) return 'text-error';
    return 'text-base-content';
};
</script>
