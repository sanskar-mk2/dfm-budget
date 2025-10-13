<template>
    <input
        type="number"
        :value="value"
        @input="$emit('change', $event)"
        @blur="$emit('blur', $event)"
        @keypress="$emit('input', $event)"
        :class="[
            'input input-sm w-24 text-right border-2 transition-all duration-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200',
            cellClass
        ]"
        step="0.01"
        placeholder="0.00"
    />
</template>

<script setup>
defineProps({
    value: {
        type: [String, Number],
        default: 0
    },
    cellClass: {
        type: String,
        default: ''
    }
});

defineEmits(['change', 'blur', 'input']);
</script>
