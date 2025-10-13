<script setup>
defineProps({
    loading: {
        type: Boolean,
        required: true,
    },
    error: {
        type: String,
        default: null,
    },
});

defineEmits(["retry"]);
</script>

<template>
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <p class="mt-4 text-base text-gray-600 dark:text-gray-300">
            Loading admin summary...
        </p>
    </div>

    <!-- Error State -->
    <div
        v-else-if="error"
        class="alert alert-error flex flex-col items-center text-center"
    >
        <h3 class="font-bold text-lg">Error loading data</h3>
        <p class="text-sm mb-4">{{ error }}</p>
        <button class="btn btn-sm btn-error" @click="$emit('retry')">
            Retry
        </button>
    </div>
</template>
