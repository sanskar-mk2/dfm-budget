<script setup>
import GrossProfitGroupCard from "./GrossProfitGroupCard.vue";

const props = defineProps({
    groups: Array,
    onSave: Function,
    onReset: Function,
});
</script>

<template>
    <div class="space-y-6">
        <GrossProfitGroupCard
            v-for="g in groups"
            :key="g.display_key"
            :group="g"
            :onSave="onSave"
            :onReset="onReset"
        />
    </div>
</template>
