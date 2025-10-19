<script setup>
import { onMounted, onUnmounted, inject, computed, reactive, watch } from "vue";
import { storeToRefs } from "pinia";
import { useGrossProfitData } from "@/composables/useGrossProfitData";
import GrossProfitGroupCard from "@/components/GrossProfitGroupCard.vue";
import LoadingError from "@/components/LoadingError.vue";
import { useAuthStore } from "@/stores/auth";

const navActions = inject("navActions");
const { grouped, fetch, save, reset, resetAll, loading } = useGrossProfitData();
const authStore = useAuthStore();
const { adminStatus, superadminStatus } = storeToRefs(authStore);

const handleResetAll = async () => {
    try {
        await resetAll();
    } catch (error) {
        console.error("Error resetting all overrides:", error);
    }
};

const resetAllAction = {
    id: "reset-all-overrides",
    text: "Reset All Overrides",
    class: "btn btn-warning mr-2",
    handler: handleResetAll,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>',
};

const backAction = {
    id: "back-to-admin",
    text: "Back to Admin",
    class: "btn btn-ghost",
    handler: () => {
        // Navigate back to admin view
        window.history.back();
    },
    icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>',
};

const updateNavActions = () => {
    const actions = [];
    if (superadminStatus.value) {
        actions.push(resetAllAction);
    }
    if (adminStatus.value || superadminStatus.value) {
        actions.push(backAction);
    }
    navActions.set(actions);
};

watch([adminStatus, superadminStatus], () => updateNavActions(), {
    immediate: true,
});

const expandedGroups = reactive({});
const makeGroupKey = (group) =>
    `${group.salesperson_id}-${group.customer_class}-${group.group_key}`;

const computeSummary = (group) => {
    const totals = group.quarters.reduce(
        (acc, quarter) => {
            acc.sales2025 += quarter.sales_2025 || 0;
            acc.budget2026 += quarter.sales || 0;
            acc.gpValue += quarter.gp_value || 0;
            return acc;
        },
        { sales2025: 0, budget2026: 0, gpValue: 0 }
    );

    return {
        ...totals,
        effectiveGp: group.effective_gp_percent || 0,
    };
};

const groupRows = computed(() => {
    if (!grouped.value?.length) {
        return [];
    }

    return grouped.value.map((group) => {
        const key = makeGroupKey(group);
        return {
            key,
            group,
            summary: computeSummary(group),
        };
    });
});

const averageGpPercent = computed(() => {
    if (!grouped.value?.length) {
        return 0;
    }
    const total = grouped.value.reduce(
        (sum, grp) => sum + (grp.effective_gp_percent || 0),
        0
    );
    return total / grouped.value.length;
});

const toggleGroup = (key) => {
    expandedGroups[key] = !expandedGroups[key];
};

const formatCurrency = (value) =>
    new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value || 0);

const formatPercent = (value) => `${((value || 0) * 100).toFixed(1)}%`;

onMounted(() => {
    updateNavActions();
    // Fetch gross profit data when component mounts
    fetch();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <!-- Header -->
        <!-- <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-4xl">
                    <h1 class="text-5xl font-bold">Gross Profit Management</h1>
                    <p class="py-6">
                        Adjust effective GP% overrides for budget allocation.
                        Use sliders to modify gross profit percentages and save
                        changes.
                    </p>
                </div>
            </div>
        </div> -->

        <!-- Loading and Error States -->
        <LoadingError :loading="loading" :error="null" @retry="fetch" />

        <!-- Stats Summary -->
        <div v-if="!loading && grouped.length > 0" class="stats shadow mb-6">
            <div class="stat">
                <div class="stat-title">Module</div>
                <div class="stat-value text-primary">
                    Gross Profit Management
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Total Groups</div>
                <div class="stat-value text-primary">{{ grouped.length }}</div>
            </div>
            <div class="stat">
                <div class="stat-title">Groups with Custom GP%</div>
                <div class="stat-value text-secondary">
                    {{ grouped.filter((g) => g.is_custom).length }}
                </div>
            </div>
            <div class="stat">
                <div class="stat-title">Average GP%</div>
                <div class="stat-value text-accent">
                    {{ formatPercent(averageGpPercent) }}
                </div>
            </div>
        </div>

        <!-- Gross Profit Groups -->
        <div v-if="!loading && groupRows.length > 0">
            <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th class="w-20">Action</th>
                            <th>Group</th>
                            <th class="text-right">2025 Sales</th>
                            <th class="text-right">2026 Budget</th>
                            <th class="text-right">Historical GP%</th>
                            <th class="text-right">GP $ Est.</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="row in groupRows" :key="row.key">
                            <tr>
                                <td>
                                    <button
                                        class="btn btn-outline btn-xs"
                                        type="button"
                                        @click="toggleGroup(row.key)"
                                    >
                                        {{
                                            expandedGroups[row.key]
                                                ? "Collapse"
                                                : "Expand"
                                        }}
                                    </button>
                                </td>
                                <td>
                                    <div class="font-semibold">
                                        {{ row.group.display_key }}
                                    </div>
                                    <div class="text-xs opacity-70">
                                        {{ row.group.customer_class }} -
                                        {{ row.group.salesperson_name }}
                                    </div>
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.sales2025) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatCurrency(row.summary.budget2026) }}
                                </td>
                                <td class="text-right font-mono">
                                    {{ formatPercent(row.summary.effectiveGp) }}
                                </td>
                                <td class="text-right font-mono font-semibold">
                                    {{ formatCurrency(row.summary.gpValue) }}
                                </td>
                            </tr>
                            <tr v-if="expandedGroups[row.key]">
                                <!-- <td></td> -->
                                <td colspan="100%">
                                    <GrossProfitGroupCard
                                        :group="row.group"
                                        :onSave="save"
                                        :onReset="reset"
                                        @collapse="toggleGroup(row.key)"
                                    />
                                </td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- No Data State -->
        <div
            v-else-if="!loading && grouped.length === 0"
            class="alert alert-info"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                class="stroke-current shrink-0 w-6 h-6"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
            </svg>
            <span
                >No gross profit data available. Please check your data
                sources.</span
            >
        </div>
    </div>
</template>
