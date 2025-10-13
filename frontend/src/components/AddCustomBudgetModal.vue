<template>
    <div v-if="isOpen" class="modal modal-open">
        <div class="modal-box w-11/12 max-w-2xl">
            <h3 class="font-bold text-lg mb-4">Add Custom Row</h3>

            <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Customer Name (non-hospitality only) -->
                <div v-if="!isHospitality" class="form-control">
                    <label class="label">
                        <span class="label-text">Customer Name</span>
                    </label>
                    <input
                        ref="customerNameInput"
                        v-model="form.customer_name"
                        type="text"
                        placeholder="Enter customer name"
                        class="input input-bordered w-full"
                        :class="{ 'input-error': errors.customer_name }"
                        required
                    />
                    <label v-if="errors.customer_name" class="label">
                        <span class="label-text-alt text-error">{{
                            errors.customer_name
                        }}</span>
                    </label>
                </div>

                <!-- Non-Hospitality Form -->
                <div v-if="!isHospitality" class="space-y-4">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Customer Class</span>
                        </label>
                        <input
                            v-model="form.customer_class"
                            type="text"
                            list="customer-classes"
                            placeholder="Enter or select customer class"
                            class="input input-bordered w-full"
                            :class="{ 'input-error': errors.customer_class }"
                            required
                        />
                        <datalist id="customer-classes">
                            <option
                                v-for="customerClass in props.autosuggestData
                                    .customer_classes"
                                :key="customerClass"
                                :value="customerClass"
                            />
                        </datalist>
                        <label v-if="errors.customer_class" class="label">
                            <span class="label-text-alt text-error">{{
                                errors.customer_class
                            }}</span>
                        </label>
                    </div>
                </div>

                <!-- Hospitality Form -->
                <div v-else class="space-y-4">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Brand</span>
                        </label>
                        <input
                            ref="brandInput"
                            v-model="form.brand"
                            type="text"
                            list="brands"
                            placeholder="Enter or select brand"
                            class="input input-bordered w-full"
                            :class="{ 'input-error': errors.brand }"
                            required
                        />
                        <datalist id="brands">
                            <option
                                v-for="brand in props.autosuggestData.brands"
                                :key="brand"
                                :value="brand"
                            />
                        </datalist>
                        <label v-if="errors.brand" class="label">
                            <span class="label-text-alt text-error">{{
                                errors.brand
                            }}</span>
                        </label>
                    </div>

                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Flag</span>
                        </label>
                        <input
                            v-model="form.flag"
                            type="text"
                            placeholder="Enter flag"
                            class="input input-bordered w-full"
                            :class="{ 'input-error': errors.flag }"
                            required
                        />
                        <label v-if="errors.flag" class="label">
                            <span class="label-text-alt text-error">{{
                                errors.flag
                            }}</span>
                        </label>
                    </div>

                    <div class="form-control hidden">
                        <label class="label">
                            <span class="label-text">Customer Class</span>
                        </label>
                        <input
                            type="text"
                            value="Hospitality"
                            class="input input-bordered w-full input-disabled"
                            disabled
                        />
                    </div>
                </div>

                <!-- Form Actions -->
                <div class="modal-action">
                    <button
                        type="button"
                        @click="handleCancel"
                        class="btn btn-ghost"
                        :disabled="loading"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        class="btn btn-primary"
                        :disabled="loading"
                    >
                        <span
                            v-if="loading"
                            class="loading loading-spinner loading-sm"
                        ></span>
                        {{ loading ? "Creating..." : "Add Budget" }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, nextTick } from "vue";

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    isHospitality: {
        type: Boolean,
        default: false,
    },
    autosuggestData: {
        type: Object,
        default: () => ({
            customer_classes: [],
            brands: [],
        }),
    },
});

const emit = defineEmits(["close", "created", "fetch-autosuggest"]);

const loading = ref(false);
const customerNameInput = ref(null);
const brandInput = ref(null);

const form = reactive({
    customer_name: "",
    customer_class: "",
    brand: "",
    flag: "",
});

const errors = reactive({
    customer_name: "",
    customer_class: "",
    brand: "",
    flag: "",
});

const validateForm = () => {
    // Clear previous errors
    Object.keys(errors).forEach((key) => (errors[key] = ""));

    let isValid = true;

    if (!props.isHospitality) {
        // Non-hospitality validation
        if (!form.customer_name.trim()) {
            errors.customer_name = "Customer name is required";
            isValid = false;
        }
        if (!form.customer_class.trim()) {
            errors.customer_class = "Customer class is required";
            isValid = false;
        }
    } else {
        // Hospitality validation
        if (!form.brand.trim()) {
            errors.brand = "Brand is required";
            isValid = false;
        }
        if (!form.flag.trim()) {
            errors.flag = "Flag is required";
            isValid = false;
        }
    }

    return isValid;
};

const handleSubmit = async () => {
    console.log("handleSubmit called", {
        isHospitality: props.isHospitality,
        form: { ...form },
    });

    if (!validateForm()) {
        console.log("Form validation failed", errors);
        return;
    }

    console.log("Form validation passed, proceeding with submission");
    loading.value = true;

    try {
        const budgetData = {
            customer_name: props.isHospitality ? null : form.customer_name,
            customer_class: props.isHospitality
                ? "Hospitality"
                : form.customer_class,
            brand: props.isHospitality ? form.brand.toUpperCase() : null,
            flag: props.isHospitality ? form.flag.toUpperCase() : null,
            is_custom: true,
        };

        console.log("Emitting budget data:", budgetData);
        // Emit the budget data to parent component
        emit("created", budgetData);

        // Reset form
        resetForm();

        // Close modal
        emit("close");
    } catch (error) {
        console.error("Error creating custom budget:", error);
    } finally {
        loading.value = false;
    }
};

const handleCancel = () => {
    resetForm();
    emit("close");
};

const resetForm = () => {
    form.customer_name = "";
    form.customer_class = "";
    form.brand = "";
    form.flag = "";
    Object.keys(errors).forEach((key) => (errors[key] = ""));
};

// Watch for modal open to fetch autosuggest data and focus input
watch(
    () => props.isOpen,
    async (isOpen) => {
        if (isOpen) {
            emit("fetch-autosuggest");
            // Focus the appropriate input after the modal is rendered
            await nextTick();
            if (props.isHospitality && brandInput.value) {
                brandInput.value.focus();
            } else if (!props.isHospitality && customerNameInput.value) {
                customerNameInput.value.focus();
            }
        }
    }
);
</script>
