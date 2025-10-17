import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useGrossProfitData() {
    const auth = useAuthStore();
    const loading = ref(false);
    const error = ref(null);
    const raw = ref([]);

    const grouped = computed(() => {
        if (!raw.value.length) return [];
        const groups = {};
        for (const r of raw.value) {
            const key = `${r.salesperson_id}-${r.customer_class}-${r.group_key}`;
            if (!groups[key]) {
                groups[key] = {
                    salesperson_id: r.salesperson_id,
                    salesperson_name: r.salesperson_name,
                    customer_class: r.customer_class,
                    group_key: r.group_key,
                    display_key:
                        r.customer_class === "Hospitality" && r.brand
                            ? `${r.group_key} (${r.brand})`
                            : r.group_key,
                    quarters: [
                        {
                            label: "Q1",
                            sales: r.quarter_1_sales,
                            gp_percent: r.q1_gp_percent,
                            gp_value: r.q1_gp_value,
                        },
                        {
                            label: "Q2",
                            sales: r.quarter_2_sales,
                            gp_percent: r.q2_gp_percent,
                            gp_value: r.q2_gp_value,
                        },
                        {
                            label: "Q3",
                            sales: r.quarter_3_sales,
                            gp_percent: r.q3_gp_percent,
                            gp_value: r.q3_gp_value,
                        },
                        {
                            label: "Q4",
                            sales: r.quarter_4_sales,
                            gp_percent: r.q4_gp_percent,
                            gp_value: r.q4_gp_value,
                        },
                    ],
                    effective_gp_percent: r.effective_gp_percent,
                    is_custom: r.is_custom,
                    total_gp_value: r.total_gp_value,
                };
            }
        }
        return Object.values(groups);
    });

    async function fetch() {
        loading.value = true;
        try {
            const res = await auth.apiCall("/api/gross-profit");
            const data = await res.json();
            raw.value = data.data || [];
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    }

    async function save(group) {
        const overrides = [
            {
                salesperson_id: group.salesperson_id,
                salesperson_name: group.salesperson_name,
                customer_class: group.customer_class,
                group_key: group.group_key,
                custom_gp_percent: group.effective_gp_percent,
            },
        ];
        await auth.apiCall("/api/gross-profit/save-overrides", {
            method: "POST",
            body: JSON.stringify({ overrides }),
        });
    }

    async function reset(group) {
        await auth.apiCall(
            `/api/gross-profit/reset/${
                group.salesperson_id
            }/${encodeURIComponent(group.customer_class)}/${encodeURIComponent(
                group.group_key
            )}`,
            { method: "DELETE" }
        );
    }

    return { grouped, fetch, save, reset, loading, error };
}
