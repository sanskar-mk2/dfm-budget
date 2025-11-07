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

const formatPercent = (value) => {
    if (value == null || value === undefined) return "-";
    return (value * 100).toFixed(1) + "%";
};

// Calculate totals for the table
const totals = computed(() => {
    if (!props.divisions || props.divisions.length === 0) {
        return {
            totalRatio: 0,
            totalActualSales: 0,
            totalQ1Sales: 0,
            totalQ2Sales: 0,
            totalQ3Sales: 0,
            totalQ4Sales: 0,
            totalQ1: 0,
            totalQ2: 0,
            totalQ3: 0,
            totalQ4: 0,
            totalAllocated: 0,
            totalQ1Gp: 0,
            totalQ2Gp: 0,
            totalQ3Gp: 0,
            totalQ4Gp: 0,
            totalGp: 0
        };
    }

    return props.divisions.reduce((acc, division) => {
        acc.totalRatio += division.effective_ratio || 0;
        acc.totalActualSales += division.total_2025_sales || 0;
        acc.totalQ1Sales += division.q1_sales || 0;
        acc.totalQ2Sales += division.q2_sales || 0;
        acc.totalQ3Sales += division.q3_sales || 0;
        acc.totalQ4Sales += division.q4_sales || 0;
        acc.totalQ1 += division.q1_allocated || 0;
        acc.totalQ2 += division.q2_allocated || 0;
        acc.totalQ3 += division.q3_allocated || 0;
        acc.totalQ4 += division.q4_allocated || 0;
        acc.totalAllocated += division.total_allocated || 0;
        acc.totalQ1Gp += division.q1_gp_value || 0;
        acc.totalQ2Gp += division.q2_gp_value || 0;
        acc.totalQ3Gp += division.q3_gp_value || 0;
        acc.totalQ4Gp += division.q4_gp_value || 0;
        acc.totalGp += division.total_gp_value || 0;
        return acc;
    }, {
        totalRatio: 0,
        totalActualSales: 0,
        totalQ1Sales: 0,
        totalQ2Sales: 0,
        totalQ3Sales: 0,
        totalQ4Sales: 0,
        totalQ1: 0,
        totalQ2: 0,
        totalQ3: 0,
        totalQ4: 0,
        totalAllocated: 0,
        totalQ1Gp: 0,
        totalQ2Gp: 0,
        totalQ3Gp: 0,
        totalQ4Gp: 0,
        totalGp: 0
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
                    <th class="text-right">Q1 Sales</th>
                    <th class="text-right">Q2 Sales</th>
                    <th class="text-right">Q3 Sales</th>
                    <th class="text-right">Q4 Sales</th>
                    <th class="text-right">GP%</th>
                    <th class="text-right">Q1 GP%</th>
                    <th class="text-right">Q2 GP%</th>
                    <th class="text-right">Q3 GP%</th>
                    <th class="text-right">Q4 GP%</th>
                    <th class="text-right">GP $</th>
                    <th class="text-right">Q1 GP</th>
                    <th class="text-right">Q2 GP</th>
                    <th class="text-right">Q3 GP</th>
                    <th class="text-right">Q4 GP</th>
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
                        {{ formatCurrency(division.q1_sales) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q2_sales) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q3_sales) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q4_sales) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatPercent(division.gp_percent) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatPercent(division.q1_gp_percent) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatPercent(division.q2_gp_percent) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatPercent(division.q3_gp_percent) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatPercent(division.q4_gp_percent) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.total_gp_value) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q1_gp_value) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q2_gp_value) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q3_gp_value) }}
                    </td>
                    <td class="text-right font-mono text-sm">
                        {{ formatCurrency(division.q4_gp_value) }}
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
                        <span class="text-lg">{{ formatCurrency(totals.totalQ1Sales) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ2Sales) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ3Sales) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ4Sales) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">-</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">-</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">-</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">-</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">-</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalGp) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ1Gp) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ2Gp) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ3Gp) }}</span>
                    </td>
                    <td class="text-right">
                        <span class="text-lg">{{ formatCurrency(totals.totalQ4Gp) }}</span>
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
