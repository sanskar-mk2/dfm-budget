<script setup>
import { onMounted, onUnmounted, inject } from "vue";
import { useGrossProfitData } from "@/composables/useGrossProfitData";
import GrossProfitTable from "@/components/GrossProfitTable.vue";
import LoadingError from "@/components/LoadingError.vue";

const navActions = inject("navActions");
const { grouped, fetch, save, reset, resetAll, loading } = useGrossProfitData();

const handleResetAll = async () => {
    try {
        await resetAll();
    } catch (error) {
        console.error("Error resetting all overrides:", error);
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
    
    // Fetch gross profit data when component mounts
    fetch();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Gross Profit Management</h1>
                    <p class="py-6">
                        Adjust effective GP% overrides for budget allocation. Use sliders to modify gross profit percentages and save changes.
                    </p>
                </div>
            </div>
        </div>

        <!-- Loading and Error States -->
        <LoadingError 
            :loading="loading" 
            :error="null" 
            @retry="fetch" 
        />

        <!-- Stats Summary -->
        <div v-if="!loading && grouped.length > 0" class="stats shadow mb-6">
            <div class="stat">
                <div class="stat-title">Total Groups</div>
                <div class="stat-value text-primary">{{ grouped.length }}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Groups with Custom GP%</div>
                <div class="stat-value text-secondary">
                    {{ grouped.filter(g => g.is_custom).length }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Average GP%</div>
                <div class="stat-value text-accent">
                    {{ (grouped.reduce((sum, g) => sum + g.effective_gp_percent, 0) / grouped.length * 100).toFixed(1) }}%
                </div>
            </div>
        </div>

        <!-- Gross Profit Groups -->
        <div v-if="!loading && grouped.length > 0">
            <GrossProfitTable
                :groups="grouped"
                :onSave="save"
                :onReset="reset"
            />
        </div>

        <!-- No Data State -->
        <div v-else-if="!loading && grouped.length === 0" class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>No gross profit data available. Please check your data sources.</span>
        </div>
    </div>
</template>
