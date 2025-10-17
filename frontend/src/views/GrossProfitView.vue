<script setup>
import { onMounted, onUnmounted, inject } from "vue";
import { useGrossProfitData } from "@/composables/useGrossProfitData";

const navActions = inject("navActions");
const { gpData, loading, fetchGrossProfitData } = useGrossProfitData();

onMounted(() => {
    // Set navigation actions for this view
    navActions.set([
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
    fetchGrossProfitData();
});

onUnmounted(() => navActions.clear());

function formatPct(v) {
  return v === null ? "-" : `${(v * 100).toFixed(1)}%`;
}

function formatMoney(v) {
  return `$${v.toLocaleString(undefined, { minimumFractionDigits: 0 })}`;
}
</script>

<template>
    <div class="p-6">
        <h1 class="text-3xl font-bold mb-4">Gross Profit Overview (2026)</h1>

        <div v-if="loading" class="text-center py-10">Loading...</div>

        <div v-else class="overflow-x-auto">
            <table class="table table-zebra w-full text-sm">
                <thead>
                    <tr>
                        <th>Salesperson</th>
                        <th>Customer Class</th>
                        <th>Group</th>
                        <th>Q1 GP%</th>
                        <th>Q2 GP%</th>
                        <th>Q3 GP%</th>
                        <th>Q4 GP%</th>
                        <th>FY GP%</th>
                        <th>Q1 GP$</th>
                        <th>Q2 GP$</th>
                        <th>Q3 GP$</th>
                        <th>Q4 GP$</th>
                        <th>Total GP$</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="row in gpData" :key="row.salesperson_id + row.group_key">
                        <td>{{ row.salesperson_name }}</td>
                        <td>{{ row.customer_class }}</td>
                        <td>{{ row.group_key }}</td>
                        <td>{{ formatPct(row.q1_gp_percent) }}</td>
                        <td>{{ formatPct(row.q2_gp_percent) }}</td>
                        <td>{{ formatPct(row.q3_gp_percent) }}</td>
                        <td>{{ formatPct(row.q4_gp_percent) }}</td>
                        <td>{{ formatPct(row.full_year_gp_percent) }}</td>
                        <td>{{ formatMoney(row.q1_gp_value) }}</td>
                        <td>{{ formatMoney(row.q2_gp_value) }}</td>
                        <td>{{ formatMoney(row.q3_gp_value) }}</td>
                        <td>{{ formatMoney(row.q4_gp_value) }}</td>
                        <td class="font-semibold">{{ formatMoney(row.total_gp_value) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
