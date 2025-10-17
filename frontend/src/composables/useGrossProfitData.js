import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useGrossProfitData() {
    const authStore = useAuthStore();
    const loading = ref(false);
    const error = ref(null);
    const gpData = ref([]);

    const fetchGrossProfitData = async () => {
        loading.value = true;
        error.value = null;
        try {
            const res = await authStore.apiCall("/api/gross-profit");
            if (!res.ok) throw new Error("Failed to fetch");
            const result = await res.json();
            gpData.value = result.data || [];
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    };

    return { gpData, loading, error, fetchGrossProfitData };
}
