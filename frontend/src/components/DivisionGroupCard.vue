<script setup>
import { ref, computed, watch } from "vue";
import DivisionTable from "./DivisionTable.vue";

const props = defineProps({
    group: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["save-ratios", "reset-group"]);

// Local copy of divisions for editing
const localDivisions = ref([]);

// Initialize local divisions when group changes
watch(
    () => props.group,
    (newGroup) => {
        if (newGroup && newGroup.divisions) {
            localDivisions.value = newGroup.divisions.map((div) => ({
                ...div,
            }));
        }
    },
    { immediate: true }
);

// Computed properties
const totalRatio = computed(() => {
    return localDivisions.value.reduce(
        (sum, div) => sum + div.effective_ratio,
        0
    );
});

const ratioStatus = computed(() => {
    const total = totalRatio.value;
    if (Math.abs(total - 1) < 0.001) {
        return { status: "perfect", icon: "✅", class: "text-success" };
    } else if (total > 1) {
        return { status: "over", icon: "⚠️", class: "text-warning" };
    } else {
        return { status: "under", icon: "⚠️", class: "text-warning" };
    }
});

const hasChanges = computed(() => {
    return localDivisions.value.some(
        (div) =>
            div.effective_ratio !== div.division_ratio_2025 || div.is_custom
    );
});

// Auto-normalization logic
const normalizeRatios = (changedIndex, newRatio) => {
    const unlockedDivisions = localDivisions.value
        .map((div, index) => ({ ...div, index }))
        .filter((div) => !div.locked);

    if (unlockedDivisions.length <= 1) {
        // If only one division is unlocked, just set it to 1
        localDivisions.value[changedIndex].effective_ratio = 1;
        return;
    }

    // Calculate the sum of all locked divisions
    const lockedSum = localDivisions.value
        .filter((div) => div.locked)
        .reduce((sum, div) => sum + div.effective_ratio, 0);

    // Calculate remaining ratio for unlocked divisions
    const remainingRatio = 1 - lockedSum;

    // If the new ratio would exceed the remaining ratio, cap it
    const cappedRatio = Math.min(newRatio, remainingRatio);
    localDivisions.value[changedIndex].effective_ratio = cappedRatio;

    // Distribute the remaining ratio proportionally among other unlocked divisions
    const otherUnlocked = unlockedDivisions.filter(
        (div) => div.index !== changedIndex
    );
    const otherUnlockedSum = otherUnlocked.reduce(
        (sum, div) => sum + div.effective_ratio,
        0
    );

    if (otherUnlockedSum > 0) {
        const remainingForOthers = remainingRatio - cappedRatio;
        const scaleFactor = remainingForOthers / otherUnlockedSum;

        otherUnlocked.forEach((div) => {
            localDivisions.value[div.index].effective_ratio =
                div.effective_ratio * scaleFactor;
        });
    }
};

// Event handlers
const handleRatioChange = (divisionIndex, newRatio) => {
    normalizeRatios(divisionIndex, newRatio);
};

const handleLockToggle = (divisionIndex) => {
    localDivisions.value[divisionIndex].locked =
        !localDivisions.value[divisionIndex].locked;
};

const handleSave = async () => {
    try {
        await emit("save-ratios", props.group.group_key, localDivisions.value);
    } catch (error) {
        console.error("Error saving ratios:", error);
        // You might want to show a toast notification here
    }
};

const handleReset = async () => {
    try {
        await emit(
            "reset-group",
            props.group.salesperson_id,
            props.group.customer_class,
            props.group.group_key
        );
    } catch (error) {
        console.error("Error resetting group:", error);
        // You might want to show a toast notification here
    }
};
</script>

<template>
    <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
            <!-- Group Header -->
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="card-title text-lg">
                        {{ group.customer_class }} ›
                        {{ group.salesperson_name }} › {{ group.display_key }}
                    </h3>
                    <div class="text-sm opacity-70">
                        {{ group.divisions.length }} divisions
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <span :class="['text-sm font-mono', ratioStatus.class]">
                        Total: {{ (totalRatio * 100).toFixed(1) }}%
                        {{ ratioStatus.icon }}
                    </span>
                </div>
            </div>

            <!-- Division Table -->
            <DivisionTable
                :divisions="localDivisions"
                :readonly="false"
                @ratio-change="handleRatioChange"
                @lock-toggle="handleLockToggle"
            />

            <!-- Action Buttons -->
            <div class="card-actions justify-end mt-4">
                <button
                    @click="handleReset"
                    class="btn btn-ghost btn-sm"
                    :disabled="!hasChanges"
                >
                    Reset
                </button>
                <button
                    @click="handleSave"
                    class="btn btn-primary btn-sm"
                    :disabled="!hasChanges"
                >
                    Save Changes
                </button>
            </div>

            <!-- Status Messages -->
            <div
                v-if="ratioStatus.status !== 'perfect'"
                class="alert alert-warning mt-2"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="stroke-current shrink-0 h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                </svg>
                <span>
                    <span v-if="ratioStatus.status === 'over'">
                        Total ratio exceeds 100%. Adjust sliders to balance the
                        ratios.
                    </span>
                    <span v-else>
                        Total ratio is under 100%. Adjust sliders to reach 100%.
                    </span>
                </span>
            </div>
        </div>
    </div>
</template>
