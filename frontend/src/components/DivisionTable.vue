<script setup>
import { ref, computed } from "vue";
import DivisionSlider from "./DivisionSlider.vue";

const props = defineProps({
    divisions: {
        type: Array,
        required: true,
    },
    readonly: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["ratio-change", "lock-toggle"]);

// Removed showActuals state - actuals column is now always visible

const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
};

const handleRatioChange = (divisionIndex, newRatio) => {
    emit("ratio-change", divisionIndex, newRatio);
};

const handleLockToggle = (divisionIndex) => {
    emit("lock-toggle", divisionIndex);
};

// Calculate totals for the table
const totals = computed(() => {
    if (!props.divisions || props.divisions.length === 0) {
        return {
            totalRatio: 0,
            totalActualSales: 0,
            totalQ1: 0,
            totalQ2: 0,
            totalQ3: 0,
            totalQ4: 0,
            totalAllocated: 0
        };
    }

    return props.divisions.reduce((acc, division) => {
        acc.totalRatio += division.effective_ratio || 0;
        acc.totalActualSales += division.total_2025_sales || 0;
        acc.totalQ1 += division.q1_allocated || 0;
        acc.totalQ2 += division.q2_allocated || 0;
        acc.totalQ3 += division.q3_allocated || 0;
        acc.totalQ4 += division.q4_allocated || 0;
        acc.totalAllocated += division.total_allocated || 0;
        return acc;
    }, {
        totalRatio: 0,
        totalActualSales: 0,
        totalQ1: 0,
        totalQ2: 0,
        totalQ3: 0,
        totalQ4: 0,
        totalAllocated: 0
    });
});
</script>

<template>
    <div class="overflow-x-auto">
        
        <table class="table table-zebra w-full">
            <thead>
                <tr>
                    <th class="w-8">#</th>
                    <th>Division</th>
                    <th class="w-80">Effective Ratio</th>
                    <th class="text-right">2025 Sales</th>
                    <th class="text-right">Q1</th>
                    <th class="text-right">Q2</th>
                    <th class="text-right">Q3</th>
                    <th class="text-right">Q4</th>
                    <th class="text-right">Total</th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="(division, index) in divisions"
                    :key="division.item_division"
                >
                    <td class="text-sm opacity-60">
                        {{ division.item_division }}
                    </td>
                    <td>
                        <div class="flex flex-col">
                            <span class="font-medium">{{
                                division.division_name
                            }}</span>
                            <span
                                v-if="division.is_custom"
                                class="text-xs badge badge-primary badge-sm"
                            >
                                Custom
                            </span>
                        </div>
                    </td>
                    <td>
                        <DivisionSlider
                            :ratio="division.effective_ratio"
                            :locked="division.locked"
                            :division-name="division.division_name"
                            :disabled="readonly"
                            @ratio-change="
                                (newRatio) => handleRatioChange(index, newRatio)
                            "
                            @lock-toggle="() => handleLockToggle(index)"
                        />
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.total_2025_sales) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q1_allocated) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q2_allocated) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q3_allocated) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q4_allocated) }}
                    </td>
                    <td class="text-right font-mono font-semibold">
                        {{ formatCurrency(division.total_allocated) }}
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="bg-base-200 font-bold">
                    <td colspan="2" class="text-right">
                        <span class="text-lg">Total</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ (totals.totalRatio * 100).toFixed(2) }}%</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalActualSales) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ1) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ2) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ3) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ4) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalAllocated) }}</span>
                    </td>
                </tr>
            </tfoot>
        </table>
    </div>
</template>
