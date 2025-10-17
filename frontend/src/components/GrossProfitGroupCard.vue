<script setup>
import GrossProfitSlider from "./GrossProfitSlider.vue";
import { ref, computed, watch, reactive } from "vue";

const props = defineProps({
    group: Object,
    onSave: Function,
    onReset: Function,
});

const saving = ref(false);

// Create a local reactive copy of the group data
const localGroup = reactive({
    ...props.group,
});

// Track original effective_gp_percent to detect changes
const originalGpPercent = ref(props.group.effective_gp_percent);
const lastSavedValue = ref(props.group.effective_gp_percent);

// Watch for group changes to update localGroup and lastSavedValue when we get fresh data from server
watch(
    () => props.group,
    (newGroup) => {
        // Update local group with fresh data from server
        Object.assign(localGroup, newGroup);

        // If we're not in the middle of a save/reset operation, update lastSavedValue
        if (!saving.value) {
            lastSavedValue.value = newGroup.effective_gp_percent;
        }
    },
    { deep: true }
);

// Computed property to detect if there are changes
const hasChanges = computed(() => {
    const current = localGroup.effective_gp_percent;
    const saved = lastSavedValue.value;
    const diff = Math.abs(current - saved);
    const hasChangesResult = diff > 0.001;

    return hasChangesResult;
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
        // Update last saved value after successful save
        lastSavedValue.value = localGroup.effective_gp_percent;
    } finally {
        saving.value = false;
    }
}

async function handleReset() {
    saving.value = true;
    try {
        await props.onReset(localGroup);
        // Update last saved value after successful reset
        lastSavedValue.value = localGroup.effective_gp_percent;
    } finally {
        saving.value = false;
    }
}

function fmtPct(v) {
    return v == null ? "-" : (v * 100).toFixed(1) + "%";
}
function fmtMoney(v) {
    return v ? "$" + v.toLocaleString() : "-";
}
</script>

<template>
    <div
        class="card bg-base-100 shadow-xl border border-base-300 transition-all duration-200 hover:shadow-2xl"
    >
        <div class="card-body">
            <!-- Group Header -->
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="card-title text-lg">
                        {{ localGroup.customer_class }} ›
                        {{ localGroup.salesperson_name }} ›
                        {{ localGroup.display_key }}
                    </h3>
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
                            <th>GP $ (Est.)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="q in localGroup.quarters" :key="q.label">
                            <td class="font-medium">{{ q.label }}</td>
                            <td>{{ fmtMoney(q.sales_2025) }}</td>
                            <td>{{ fmtMoney(q.sales) }}</td>
                            <td>{{ fmtPct(q.gp_percent) }}</td>
                            <td class="font-mono">
                                {{ fmtMoney(q.gp_value) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- GP% Override Section -->
            <div class="flex justify-between items-center mt-4">
                <div class="w-full max-w-sm">
                    <label class="text-sm font-medium mb-2 block">
                        Effective GP%
                    </label>
                    <div class="flex items-center space-x-2">
                        <GrossProfitSlider
                            v-model="localGroup.effective_gp_percent"
                        />
                        <div class="text-sm opacity-70">
                            <span
                                v-if="localGroup.is_custom"
                                class="badge badge-sm badge-primary ml-2"
                                >Custom</span
                            >
                        </div>
                    </div>
                </div>
                <div class="space-x-2">
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
        </div>
    </div>
</template>
