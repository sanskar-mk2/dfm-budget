<script setup>
import { computed } from 'vue'

const props = defineProps({
    ratio: {
        type: Number,
        required: true
    },
    locked: {
        type: Boolean,
        default: false
    },
    divisionName: {
        type: String,
        required: true
    },
    disabled: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['ratio-change', 'lock-toggle'])

const percentage = computed(() => (props.ratio * 100).toFixed(1))

const handleSliderChange = (event) => {
    if (!props.locked && !props.disabled) {
        const newRatio = parseFloat(event.target.value)
        emit('ratio-change', newRatio)
    }
}

const toggleLock = () => {
    if (!props.disabled) {
        emit('lock-toggle')
    }
}
</script>

<template>
    <div class="flex items-center gap-2">
        <!-- Lock Toggle Button -->
        <button
            @click="toggleLock"
            :disabled="disabled"
            :class="[
                'btn btn-sm btn-ghost',
                locked ? 'btn-primary' : 'btn-outline',
                disabled ? 'btn-disabled' : ''
            ]"
            :title="locked ? 'Unlock to edit' : 'Lock to prevent changes'"
        >
            <svg
                v-if="locked"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
            </svg>
            <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"
                />
            </svg>
        </button>

        <!-- Slider -->
        <div class="flex-1">
            <input
                type="range"
                :min="0"
                :max="1"
                :step="0.001"
                :value="ratio"
                :disabled="locked || disabled"
                @input="handleSliderChange"
                class="range range-primary range-sm w-full"
                :class="{ 'opacity-50': locked || disabled }"
            />
        </div>

        <!-- Percentage Display -->
        <div class="text-sm font-mono min-w-[4rem] text-right">
            <span :class="[
                'badge badge-sm',
                locked ? 'badge-primary' : 'badge-outline'
            ]">
                {{ percentage }}%
            </span>
        </div>
    </div>
</template>
