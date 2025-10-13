<script setup>
import { computed } from 'vue';

const props = defineProps({
    summaryData: {
        type: Array,
        required: true,
        default: () => []
    }
});

const totalSales = computed(() =>
    props.summaryData.reduce((sum, p) => sum + p.total_sales, 0)
);

const totalBudget = computed(() =>
    props.summaryData.reduce((sum, p) => sum + p.total_budget, 0)
);

const totalVariance = computed(() => totalSales.value - totalBudget.value);

const formatNumber = (num) =>
    new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(num || 0);
</script>

<template>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stat bg-base-100 shadow rounded-xl">
            <div class="stat-title">Total Salespeople</div>
            <div class="stat-value text-primary">{{ summaryData.length }}</div>
        </div>
        <div class="stat bg-base-100 shadow rounded-xl">
            <div class="stat-title">Total Sales</div>
            <div class="stat-value text-primary">
                ${{ formatNumber(totalSales) }}
            </div>
        </div>
        <div class="stat bg-base-100 shadow rounded-xl">
            <div class="stat-title">Total Budget</div>
            <div class="stat-value text-primary">
                ${{ formatNumber(totalBudget) }}
            </div>
        </div>
        <div class="stat bg-base-100 shadow rounded-xl">
            <div class="stat-title">Variance</div>
            <div class="stat-value text-primary">
                ${{ formatNumber(totalVariance) }}
            </div>
        </div>
    </div>
</template>
