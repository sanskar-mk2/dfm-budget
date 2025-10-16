<script setup>
import { onMounted, onUnmounted, inject } from "vue";

const navActions = inject("navActions");

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
});

onUnmounted(() => navActions.clear());
</script>

<template>
    <div class="p-6 space-y-6">
        <div class="hero bg-base-200 rounded-lg">
            <div class="hero-content text-center">
                <div class="max-w-md">
                    <h1 class="text-5xl font-bold">Gross Profit View</h1>
                    <p class="py-6">
                        This is the Gross Profit view. Content will be added here in the future.
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>
