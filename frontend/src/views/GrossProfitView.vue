<script setup>
import { onMounted } from "vue";
import { useGrossProfitData } from "@/composables/useGrossProfitData";

const { grouped, fetch, save, reset, loading } = useGrossProfitData();

onMounted(fetch);

function formatPct(v) {
    return v == null ? "-" : (v * 100).toFixed(1) + "%";
}
function formatMoney(v) {
    return v ? "$" + v.toLocaleString() : "-";
}
</script>

<template>
    <div class="p-6 space-y-6">
        <h1 class="text-3xl font-bold mb-4">Gross Profit Overview</h1>

        <div v-if="loading" class="text-center py-10">Loading...</div>

        <div v-else>
            <div
                v-for="group in grouped"
                :key="group.display_key"
                class="card bg-base-100 shadow p-4 mb-4"
            >
                <h2 class="font-semibold text-lg mb-2">
                    {{ group.customer_class }} › {{ group.salesperson_name }} ›
                    {{ group.display_key }}
                </h2>

                <table class="table w-full text-sm">
                    <thead>
                        <tr>
                            <th>Quarter</th>
                            <th>Sales</th>
                            <th>Historical GP%</th>
                            <th>GP $ (Est.)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="q in group.quarters" :key="q.label">
                            <td>{{ q.label }}</td>
                            <td>{{ formatMoney(q.sales) }}</td>
                            <td>{{ formatPct(q.gp_percent) }}</td>
                            <td>{{ formatMoney(q.gp_value) }}</td>
                        </tr>
                    </tbody>
                </table>

                <div class="mt-3 flex justify-between items-center">
                    <div>
                        Effective GP%:
                        <input
                            type="number"
                            step="0.001"
                            v-model.number="group.effective_gp_percent"
                            class="input input-sm input-bordered w-28 ml-2"
                        />
                        <span class="ml-1 text-gray-500"
                            >(applies to all quarters)</span
                        >
                    </div>
                    <div class="space-x-2">
                        <button
                            class="btn btn-sm btn-outline"
                            @click="save(group)"
                        >
                            Save
                        </button>
                        <button
                            class="btn btn-sm btn-outline"
                            @click="reset(group)"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
