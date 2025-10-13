<template>
    <div v-if="sales.length > 0" class="mt-8 p-4 bg-base-200 rounded-lg">
        <h3 class="text-lg font-semibold mb-4">Sales Summary</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="stat">
                <div class="stat-title">Total Customers</div>
                <div class="stat-value text-primary">
                    {{ sales.length }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Q1 Total</div>
                <div class="stat-value text-info">
                    ${{ formatCurrency(getTotalQ1()) }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Q2 Total</div>
                <div class="stat-value text-info">
                    ${{ formatCurrency(getTotalQ2()) }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Q3 Total</div>
                <div class="stat-value text-info">
                    ${{ formatCurrency(getTotalQ3()) }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Q4 Total</div>
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
    }
});
</script>
