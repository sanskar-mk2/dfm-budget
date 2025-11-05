<script setup>
import { ref, computed, watch, reactive } from "vue";

const props = defineProps({
    group: Object,
    onSave: Function,
    onReset: Function,
});

const emit = defineEmits(["collapse"]);

const saving = ref(false);

// Create a local reactive copy of the group data
const localGroup = reactive({
    ...props.group,
    quarters: props.group.quarters.map(q => ({ ...q }))
});

// Track original quarter effective_gp_percent values to detect changes
const lastSavedQuarters = ref(
    props.group.quarters.map(q => ({
        label: q.label,
        effective_gp_percent: q.effective_gp_percent
    }))
);

// Watch for group changes to update localGroup and lastSavedQuarters when we get fresh data from server
watch(
    () => props.group,
    (newGroup) => {
        // Update local group with fresh data from server
        Object.assign(localGroup, {
            ...newGroup,
            quarters: newGroup.quarters.map(q => ({ ...q }))
        });

        // If we're not in the middle of a save/reset operation, update lastSavedQuarters
        if (!saving.value) {
            lastSavedQuarters.value = newGroup.quarters.map(q => ({
                label: q.label,
                effective_gp_percent: q.effective_gp_percent
            }));
        }
    },
    { deep: true }
);

// Computed property to detect if there are changes in any quarter
const hasChanges = computed(() => {
    for (let i = 0; i < localGroup.quarters.length; i++) {
        const current = localGroup.quarters[i].effective_gp_percent;
        const saved = lastSavedQuarters.value.find(q => q.label === localGroup.quarters[i].label);
        if (saved) {
            const diff = Math.abs((current || 0) - (saved.effective_gp_percent || 0));
            if (diff > 0.001) {
                return true;
            }
        }
    }
    return false;
});

// Computed property to detect if reset should be enabled
const canReset = computed(() => {
    // Reset is enabled if there are custom overrides OR if there are local changes
    return localGroup.is_custom || hasChanges.value;
});

async function handleSave() {
    saving.value = true;
    try {
        await props.onSave(localGroup);
        // Update last saved quarter values after successful save
        lastSavedQuarters.value = localGroup.quarters.map(q => ({
            label: q.label,
            effective_gp_percent: q.effective_gp_percent
        }));
    } finally {
        saving.value = false;
    }
}

async function handleReset() {
    saving.value = true;
    try {
        await props.onReset(localGroup);
        // Update last saved quarter values after successful reset
        lastSavedQuarters.value = localGroup.quarters.map(q => ({
            label: q.label,
            effective_gp_percent: q.effective_gp_percent
        }));
    } finally {
        saving.value = false;
    }
}

function fmtPct(v) {
    return v == null ? "-" : (v * 100).toFixed(1) + "%";
}
function fmtMoney(v) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(v || 0);
}

// Convert decimal to percentage for input display
function toPercentInput(v) {
    if (v == null || v === undefined) return "";
    return (v * 100).toFixed(1);
}

// Convert percentage input to decimal
function fromPercentInput(v) {
    if (!v || v === "") return null;
    const num = parseFloat(v);
    if (isNaN(num)) return null;
    return Math.min(Math.max(num / 100, 0), 1);
}

// Handle input for effective GP%
function updateEffectiveGp(quarter, value) {
    const decimal = fromPercentInput(value);
    quarter.effective_gp_percent = decimal;
    // Recalculate GP value based on the new effective GP%
    if (decimal !== null && quarter.sales !== null && quarter.sales !== undefined) {
        quarter.gp_value = Math.round(quarter.sales * decimal * 100) / 100;
    }
}

const handleCollapse = () => {
    emit("collapse");
};
</script>

<template>
    <div
        class="card bg-base-100 shadow-xl border border-base-300 transition-all duration-200 hover:shadow-2xl"
    >
        <div class="card-body">
            <!-- Group Header -->
            <div class="flex items-center justify-between mb-4">
                <h3 class="card-title text-lg">
                    {{ localGroup.customer_class }} ›
                    {{ localGroup.salesperson_name }} ›
                    {{ localGroup.display_key }}
                </h3>
                <div class="flex items-center gap-2">
                    <button
                        class="btn btn-sm btn-ghost"
                        :disabled="saving || !canReset"
                        @click="handleReset"
                    >
                        Reset
                    </button>
                    <button
                        class="btn btn-sm btn-primary"
                        :disabled="saving || !hasChanges"
                        @click="handleSave"
                    >
                        <span
                            v-if="saving"
                            class="loading loading-spinner loading-xs"
                        ></span>
                        Save Changes
                    </button>
                </div>
            </div>

            <!-- Data Table -->
            <div class="overflow-x-auto">
                <table class="table w-full text-sm">
                    <thead>
                        <tr>
                            <th>Quarter</th>
                            <th>2025 Sales</th>
                            <th>2026 Budget</th>
                            <th>Historical GP%</th>
                            <th>Effective GP%</th>
                            <th>GP $ (Est.)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="q in localGroup.quarters" :key="q.label">
                            <td class="font-medium">{{ q.label }}</td>
                            <td>{{ fmtMoney(q.sales_2025) }}</td>
                            <td>{{ fmtMoney(q.sales) }}</td>
                            <td>{{ fmtPct(q.gp_percent) }}</td>
                            <td>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    max="100"
                                    :value="toPercentInput(q.effective_gp_percent)"
                                    @input="(e) => updateEffectiveGp(q, e.target.value)"
                                    @blur="(e) => updateEffectiveGp(q, e.target.value)"
                                    class="input input-bordered input-sm w-20 text-right font-mono"
                                    placeholder="0.0"
                                />
                                <span class="text-xs opacity-60 ml-1">%</span>
                            </td>
                            <td class="font-mono">
                                {{ fmtMoney(q.gp_value) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Reference Info -->
            <div class="mt-4 pt-4 border-t border-base-300">
                <div class="flex items-center justify-between text-sm">
                    <span class="opacity-70">
                        <span v-if="localGroup.is_custom" class="badge badge-sm badge-primary mr-2">Has Custom Overrides</span>
                        Full-Year Effective GP% (Reference): 
                    </span>
                    <span class="font-mono opacity-70">
                        {{ fmtPct(localGroup.effective_gp_percent) }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>
