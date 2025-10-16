<script setup>
import { onMounted, onUnmounted, inject, ref } from "vue";
import { useAuthStore } from "@/stores/auth";

const navActions = inject("navActions");
const authStore = useAuthStore();
const loading = ref(false);
const error = ref(null);
const divisionData = ref([]);

const fetchDivisionData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
        console.log("Fetching division allocations...");
        const response = await authStore.apiCall("/api/division/allocations");
        
        if (response.ok) {
            const result = await response.json();
            console.log("Division allocations response:", result);
            divisionData.value = result.data || [];
            console.log("Division data:", divisionData.value);
        } else {
            const errorData = await response.json();
            console.error("Error fetching division data:", errorData);
            error.value = errorData.detail || "Failed to fetch division data";
        }
    } catch (err) {
        console.error("Exception fetching division data:", err);
        error.value = "Network error occurred";
    } finally {
        loading.value = false;
    }
};

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
    
    // Fetch division data when component mounts
    fetchDivisionData();
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-md">
                    <h1 class="text-5xl font-bold">Division View</h1>
                    <p class="py-6">
                        This is the Division view. Content will be added here in the future.
                    </p>
                    
                    <!-- Loading State -->
                    <div v-if="loading" class="flex justify-center">
                        <span class="loading loading-spinner loading-lg"></span>
                    </div>
                    
                    <!-- Error State -->
                    <div v-else-if="error" class="alert alert-error">
                        <span>{{ error }}</span>
                    </div>
                    
                    <!-- Success State -->
                    <div v-else-if="divisionData.length > 0" class="alert alert-success">
                        <span>Successfully loaded {{ divisionData.length }} division records</span>
                    </div>
                    
                    <!-- No Data State -->
                    <div v-else class="alert alert-info">
                        <span>No division data available</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
