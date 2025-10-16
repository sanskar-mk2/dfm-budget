<script setup>
import { ref } from "vue";
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

// State for showing/hiding actuals columns
const showActuals = ref(false);

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
</script>

<template>
    <div class="overflow-x-auto">
        <!-- Toggle button for showing/hiding actuals -->
        <div class="mb-4 flex justify-end">
            <button 
                @click="showActuals = !showActuals"
                class="btn btn-xs btn-outline"
            >
                {{ showActuals ? 'Hide Actuals' : 'Show Actuals' }}
            </button>
        </div>
        
        <table class="table table-zebra w-full">
            <thead>
                <tr>
                    <th class="w-8">#</th>
                    <th>Division</th>
                    <th class="w-80">Effective Ratio</th>
                    <th v-if="showActuals" class="text-right">2025 Ratio</th>
                    <th v-if="showActuals" class="text-right">Actual Sales</th>
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
                    <td v-if="showActuals" class="text-right font-mono text-sm">
                        {{ (division.division_ratio_2025 * 100).toFixed(2) }}%
                    </td>
                    <td v-if="showActuals" class="text-right font-mono text-sm">
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
        </table>
    </div>
</template>
