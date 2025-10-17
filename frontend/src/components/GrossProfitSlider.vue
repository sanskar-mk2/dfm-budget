<script setup>
import { ref, watch, computed } from "vue";

const props = defineProps({
    modelValue: Number, // e.g. 0.52
});

const emit = defineEmits(["update:modelValue"]);

// Ensure we always have a valid number, default to 0 if modelValue is null/undefined
const internal = ref((props.modelValue || 0) * 100);

// Computed property for display value to ensure it's always a valid number
const displayValue = computed(() => {
    const val = internal.value;
    // Ensure we have a valid number
    if (typeof val !== 'number' || isNaN(val)) {
        return '0.0';
    }
    return val.toFixed(1);
});

watch(internal, (val) => {
    // Ensure we have a valid number before emitting
    if (typeof val === 'number' && !isNaN(val)) {
        const newValue = val / 100;
        emit("update:modelValue", newValue);
    }
});

watch(
    () => props.modelValue,
    (v) => {
        // Ensure we have a valid number before setting internal value
        if (typeof v === 'number' && !isNaN(v)) {
            internal.value = v * 100;
        } else {
            internal.value = 0;
        }
    }
);
</script>

<template>
    <div class="flex items-center space-x-3 w-full">
        <input
            type="range"
            min="0"
            max="100"
            step="0.1"
            :value="typeof internal === 'number' && !isNaN(internal) ? internal : 0"
            @input="(e) => internal = parseFloat(e.target.value) || 0"
            class="range range-sm range-primary flex-grow"
        />
        <span class="badge badge-sm badge-primary">
            {{ displayValue }}%
        </span>
    </div>
</template>
