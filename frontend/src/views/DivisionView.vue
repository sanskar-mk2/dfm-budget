<script setup>
import { onMounted, onUnmounted, inject } from "vue";
import { useDivisionData } from "@/composables/useDivisionData";
import DivisionGroupCard from "@/components/DivisionGroupCard.vue";
import LoadingError from "@/components/LoadingError.vue";

const navActions = inject("navActions");
const { loading, error, groupedData, fetchDivisionData, saveRatios, resetGroupOverrides, resetAllOverrides } = useDivisionData();

const handleSaveRatios = async (groupKey, divisions) => {
    try {
        await saveRatios(groupKey, divisions);
    } catch (error) {
        console.error("Error saving ratios:", error);
        // You might want to show a toast notification here
    }
};

const handleResetGroup = async (salespersonId, customerClass, groupKey) => {
    try {
        await resetGroupOverrides(salespersonId, customerClass, groupKey);
    } catch (error) {
        console.error("Error resetting group overrides:", error);
    }
};

const handleResetAll = async () => {
    try {
        await resetAllOverrides();
    } catch (error) {
        console.error("Error resetting overrides:", error);
    }
};

onMounted(() => {
    // Set navigation actions for this view
    navActions.set([
        {
            id: "reset-all-overrides",
            text: "Reset All Overrides",
            class: "btn btn-warning mr-2",
            handler: handleResetAll,
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>',
        },
        {
            id: "back-to-admin",
            text: "Back to Admin",
            class: "btn btn-ghost",
            handler: () => {
                // Navigate back to admin view
                window.history.back();
            },
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>',
        },
    ]);
    
    // Fetch division data when component mounts
    fetchDivisionData();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Division Ratio Management</h1>
                    <p class="py-6">
                        Adjust division ratios for budget allocation. Use sliders to modify ratios and lock divisions to prevent changes.
                    </p>
                </div>
            </div>
        </div>

        <!-- Loading and Error States -->
        <LoadingError 
            :loading="loading" 
            :error="error" 
            @retry="fetchDivisionData" 
        />

        <!-- Division Groups -->
        <div v-if="!loading && !error && groupedData.length > 0" class="space-y-6">
            <div class="stats shadow mb-6">
                <div class="stat">
                    <div class="stat-title">Total Groups</div>
                    <div class="stat-value text-primary">{{ groupedData.length }}</div>
                </div>
                <div class="stat">
                    <div class="stat-title">Groups with Custom Ratios</div>
                    <div class="stat-value text-secondary">
                        {{ groupedData.filter(g => g.hasCustomRatios).length }}
                    </div>
                </div>
                <div class="stat">
                    <div class="stat-title">Total Divisions</div>
                    <div class="stat-value text-accent">
                        {{ groupedData.reduce((sum, g) => sum + g.divisions.length, 0) }}
                    </div>
                </div>
            </div>

            <!-- Group Cards -->
            <DivisionGroupCard
                v-for="group in groupedData"
                :key="`${group.salesperson_id}-${group.customer_class}-${group.group_key}`"
                :group="group"
                @save-ratios="handleSaveRatios"
                @reset-group="handleResetGroup"
            />
        </div>

        <!-- No Data State -->
        <div v-else-if="!loading && !error && groupedData.length === 0" class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>No division data available. Please check your data sources.</span>
        </div>
    </div>
</template>
