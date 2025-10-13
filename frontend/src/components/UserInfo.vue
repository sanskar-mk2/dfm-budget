<template>
    <div class="mt-8 p-4 bg-base-200 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">User Info</h3>
        <p><strong>Username:</strong> {{ currentUser?.username }}</p>
        <p v-if="currentSalesperson">
            <strong>Salesperson:</strong>
            {{ currentSalesperson?.salesman_name }}
        </p>
    </div>
</template>

<script setup>
defineProps({
    currentUser: {
        type: Object,
        default: null
    },
    currentSalesperson: {
        type: Object,
        default: null
    }
});
</script>
