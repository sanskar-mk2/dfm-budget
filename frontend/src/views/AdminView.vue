<script setup>
import { computed, onMounted, onUnmounted, inject } from "vue";
import { useRouter } from "vue-router";
import AdminStats from "@/components/AdminStats.vue";
import LoadingError from "@/components/LoadingError.vue";
import SalespersonTable from "@/components/SalespersonTable.vue";
import { useAdminData } from "@/composables/useAdminData";

const router = useRouter();
const navActions = inject("navActions");

const {
    loading,
    error,
    summaryData,
    hospitalityData,
    nonHospitalityData,
    hospitalitySubtotals,
    nonHospitalitySubtotals,
    fetchAdminSummary,
    downloadSalespersonData,
    downloadFullBudgetSheet
} = useAdminData();

function viewSalesperson(id) {
    router.push(`/salesperson/${id}`);
}

onMounted(() => {
    fetchAdminSummary();
    navActions.set([
        {
            id: "division-view",
            text: "Division View",
            class: "btn btn-secondary mr-2",
            handler: () => router.push("/division"),
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>',
        },
        {
            id: "gross-profit-view",
            text: "Gross Profit View",
            class: "btn btn-accent mr-2",
            handler: () => router.push("/gross-profit"),
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>',
        },
        {
            id: "download-full-budget",
            text: "Download Full Budget Sheet",
            class: "btn btn-primary",
            disabled: computed(
                () => loading.value || !summaryData.value.length
            ),
            handler: downloadFullBudgetSheet,
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>',
        },
    ]);
});
onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <LoadingError 
            :loading="loading" 
            :error="error" 
            @retry="fetchAdminSummary" 
        />

        <!-- Data -->
        <div v-if="!loading && !error">
            <!-- Stats -->
            <AdminStats :summary-data="summaryData" />

            <!-- Hospitality Table -->
            <SalespersonTable
                v-if="hospitalityData.length"
                :data="hospitalityData"
                :subtotals="hospitalitySubtotals"
                title="Hospitality Salespeople"
                type="hospitality"
                @view-salesperson="viewSalesperson"
                @download-salesperson="downloadSalespersonData"
            />

            <!-- Non-Hospitality Table -->
            <SalespersonTable
                v-if="nonHospitalityData.length"
                :data="nonHospitalityData"
                :subtotals="nonHospitalitySubtotals"
                title="Non-Hospitality Salespeople"
                type="non-hospitality"
                @view-salesperson="viewSalesperson"
                @download-salesperson="downloadSalespersonData"
            />
        </div>
    </div>
</template>

