<script setup>
import { computed } from "vue";

const props = defineProps({
    data: {
        type: Array,
        required: true,
        default: () => [],
    },
    subtotals: {
        type: Object,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        required: true,
        validator: (value) =>
            ["hospitality", "non-hospitality"].includes(value),
    },
});

const emit = defineEmits(["view-salesperson", "download-salesperson"]);

const formatNumber = (num) =>
    new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(num || 0);
</script>

<template>
    <div v-if="data.length" class="mt-10 bg-base-100 shadow-md rounded-xl">
        <h2
            class="text-lg px-6 py-3 bg-primary text-primary-content rounded-t-xl"
        >
            {{ title }} ({{ data.length }})
        </h2>
        <div class="overflow-x-auto rounded-xl">
            <table class="table table-zebra text-sm">
                <thead>
                    <tr>
                        <th></th>
                        <th>Salesperson</th>
                        <th>Q1 Sales</th>
                        <th>Q2 Sales</th>
                        <th>Q3 Sales</th>
                        <th>Q4 Orders</th>
                        <th>Total Sales</th>
                        <th>0% Sales (Rate)</th>
                        <th>Q1 Budget</th>
                        <th>Q2 Budget</th>
                        <th>Q3 Budget</th>
                        <th>Q4 Budget</th>
                        <th>Total Budget</th>
                        <th>Growth</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="p in data" :key="p.salesperson_id" class="hover">
                        <td>
                            <div class="join">
                                <button
                                    @click="
                                        emit(
                                            'view-salesperson',
                                            p.salesperson_id
                                        )
                                    "
                                    class="btn btn-xs btn-ghost join-item"
                                    title="View"
                                >
                                    👁️
                                </button>
                                <button
                                    @click="
                                        emit(
                                            'download-salesperson',
                                            p.salesperson_id,
                                            p.salesperson_name
                                        )
                                    "
                                    class="btn btn-xs btn-ghost join-item"
                                    title="Download"
                                >
                                    ⬇️
                                </button>
                            </div>
                        </td>
                        <td>
                            {{ p.salesperson_name }}
                            <div class="text-xs opacity-70">
                                ID: {{ p.salesperson_id }}
                            </div>
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q1_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q2_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q3_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q4_sales) }}
                        </td>
                        <td class="text-right font-bold">
                            ${{ formatNumber(p.total_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.zero_perc_sales) }}
                            <div class="text-xs opacity-60">
                                ({{ p.zero_perc_sales_percent.toFixed(2) }}%)
                            </div>
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q1_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q2_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q3_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(p.q4_budget) }}
                        </td>
                        <td class="text-right font-bold">
                            ${{ formatNumber(p.total_budget) }}
                        </td>
                        <td class="text-right">
                            {{ p.total_sales !== 0 ? (((p.total_budget - p.total_sales) / p.total_sales) * 100).toFixed(2) : '0.00' }}%
                        </td>
                    </tr>

                    <!-- Subtotal -->
                    <tr class="font-bold bg-secondary text-secondary-content [&:nth-child(even)]:bg-secondary [&:nth-child(odd)]:bg-secondary">
                        <td colspan="2" class="text-center">Subtotal</td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q1_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q2_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q3_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q4_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.total_sales) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.zero_perc_sales) }}
                            <div class="text-xs opacity-70">
                                ({{
                                    subtotals.zero_perc_sales_percent.toFixed(
                                        2
                                    )
                                }}%)
                            </div>
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q1_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q2_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q3_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.q4_budget) }}
                        </td>
                        <td class="text-right">
                            ${{ formatNumber(subtotals.total_budget) }}
                        </td>
                        <td class="text-right">
                            {{ subtotals.total_sales !== 0 ? (((subtotals.total_budget - subtotals.total_sales) / subtotals.total_sales) * 100).toFixed(2) : '0.00' }}%
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
