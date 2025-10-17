import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useDivisionData() {
    const authStore = useAuthStore();
    const loading = ref(false);
    const error = ref(null);
    const divisionData = ref([]);

    // Grouped data computed property
    const groupedData = computed(() => {
        if (!divisionData.value.length) return [];

        const groups = {};

        divisionData.value.forEach((item) => {
            const key = `${item.salesperson_id}-${item.customer_class}-${item.group_key}`;

            if (!groups[key]) {
                groups[key] = {
                    salesperson_id: item.salesperson_id,
                    salesperson_name: item.salesperson_name,
                    customer_class: item.customer_class,
                    group_key: item.group_key,
                    brand: item.brand,
                    display_key:
                        item.customer_class === "Hospitality" && item.brand
                            ? `${item.group_key} (${item.brand})`
                            : item.group_key,
                    divisions: [],
                    totalRatio: 0,
                    hasCustomRatios: false,
                };
            }

            const division = {
                item_division: item.item_division,
                division_name: item.division_name,
                effective_ratio: item.effective_ratio,
                is_custom: item.is_custom,
                q1_allocated: item.q1_allocated,
                q2_allocated: item.q2_allocated,
                q3_allocated: item.q3_allocated,
                q4_allocated: item.q4_allocated,
                total_allocated: item.total_allocated,
                division_ratio_2025: item.division_ratio_2025,
                total_2025_sales: item.total_2025_sales,
                locked: false, // UI state for lock toggle
            };

            groups[key].divisions.push(division);
            groups[key].totalRatio += division.effective_ratio;
            if (division.is_custom) {
                groups[key].hasCustomRatios = true;
            }
        });

        // Sort divisions within each group by item_division
        Object.values(groups).forEach((group) => {
            group.divisions.sort((a, b) => a.item_division - b.item_division);
        });

        return Object.values(groups);
    });

    const fetchDivisionData = async () => {
        loading.value = true;
        error.value = null;

        try {
            const response = await authStore.apiCall(
                "/api/division/allocations"
            );

            if (response.ok) {
                const result = await response.json();
                divisionData.value = result.data || [];
            } else {
                const errorData = await response.json();
                console.error("Error fetching division data:", errorData);
                error.value =
                    errorData.detail || "Failed to fetch division data";
            }
        } catch (err) {
            console.error("Exception fetching division data:", err);
            error.value = "Network error occurred";
        } finally {
            loading.value = false;
        }
    };

    const fetchSingleGroup = async (salespersonId, customerClass, groupKey) => {
        const response = await authStore.apiCall(
            `/api/division/allocations/${salespersonId}/${encodeURIComponent(customerClass)}/${encodeURIComponent(groupKey)}`
        );
        if (!response.ok) throw new Error("Failed to fetch group");
        const result = await response.json();
        return result.data || [];
    };

    const saveRatios = async (groupKey, divisions) => {
        try {
            // Find the group data to get salesperson info
            const group = groupedData.value.find(
                (g) => g.group_key === groupKey
            );
            if (!group) {
                throw new Error("Group not found");
            }

            // Prepare overrides data
            const overrides = divisions
                .filter(
                    (div) =>
                        div.is_custom ||
                        div.effective_ratio !== div.division_ratio_2025
                )
                .map((div) => ({
                    salesperson_id: group.salesperson_id,
                    salesperson_name: group.salesperson_name,
                    customer_class: group.customer_class,
                    group_key: group.group_key,
                    item_division: div.item_division,
                    custom_ratio: div.effective_ratio,
                }));

            if (overrides.length === 0) {
                console.log("No changes to save");
                return { success: true, message: "No changes to save" };
            }

            const response = await authStore.apiCall(
                "/api/division/save-ratios",
                {
                    method: "POST",
                    body: JSON.stringify({ overrides }),
                }
            );

            if (response.ok) {
                const result = await response.json();

                // Fetch only updated group
                const updatedRows = await fetchSingleGroup(group.salesperson_id, group.customer_class, group.group_key);

                // Replace that group locally while maintaining position
                const newData = [...divisionData.value];
                const groupRows = newData.filter(
                    i => i.group_key === group.group_key && i.salesperson_id === group.salesperson_id
                );
                
                if (groupRows.length > 0) {
                    // Find the first occurrence of this group
                    const firstIndex = newData.findIndex(
                        i => i.group_key === group.group_key && i.salesperson_id === group.salesperson_id
                    );
                    
                    // Remove all rows for this group
                    const filteredData = newData.filter(
                        i => !(i.group_key === group.group_key && i.salesperson_id === group.salesperson_id)
                    );
                    
                    // Insert new data at the original position
                    filteredData.splice(firstIndex, 0, ...updatedRows);
                    divisionData.value = filteredData;
                } else {
                    // Fallback: just append if group not found
                    divisionData.value = [...divisionData.value.filter(
                        i => !(i.group_key === group.group_key && i.salesperson_id === group.salesperson_id)
                    ), ...updatedRows];
                }

                return result;
            } else {
                const errorData = await response.json();
                console.error("Error saving ratios:", errorData);
                throw new Error(errorData.detail || "Failed to save ratios");
            }
        } catch (err) {
            console.error("Exception saving ratios:", err);
            throw err;
        }
    };

    const resetGroupOverrides = async (
        salespersonId,
        customerClass,
        groupKey
    ) => {
        try {
            const response = await authStore.apiCall(
                `/api/division/reset-group/${salespersonId}/${encodeURIComponent(
                    customerClass
                )}/${encodeURIComponent(groupKey)}`,
                { method: "DELETE" }
            );

            if (response.ok) {
                const result = await response.json();

                // Fetch only updated group
                const updatedRows = await fetchSingleGroup(salespersonId, customerClass, groupKey);

                // Replace that group locally while maintaining position
                const newData = [...divisionData.value];
                const groupRows = newData.filter(
                    i => i.group_key === groupKey && i.salesperson_id === salespersonId
                );
                
                if (groupRows.length > 0) {
                    // Find the first occurrence of this group
                    const firstIndex = newData.findIndex(
                        i => i.group_key === groupKey && i.salesperson_id === salespersonId
                    );
                    
                    // Remove all rows for this group
                    const filteredData = newData.filter(
                        i => !(i.group_key === groupKey && i.salesperson_id === salespersonId)
                    );
                    
                    // Insert new data at the original position
                    filteredData.splice(firstIndex, 0, ...updatedRows);
                    divisionData.value = filteredData;
                } else {
                    // Fallback: just append if group not found
                    divisionData.value = [...divisionData.value.filter(
                        i => !(i.group_key === groupKey && i.salesperson_id === salespersonId)
                    ), ...updatedRows];
                }

                return result;
            } else {
                const errorData = await response.json();
                throw new Error(
                    errorData.detail || "Failed to reset group overrides"
                );
            }
        } catch (err) {
            console.error("Exception resetting group overrides:", err);
            throw err;
        }
    };

    const resetAllOverrides = async () => {
        try {
            // Delete all overrides for all groups
            const deletePromises = groupedData.value
                .filter((group) => group.hasCustomRatios)
                .map((group) =>
                    resetGroupOverrides(
                        group.salesperson_id,
                        group.customer_class,
                        group.group_key
                    )
                );

            if (deletePromises.length === 0) {
                return { success: true, message: "No overrides to reset" };
            }

            await Promise.all(deletePromises);

            return {
                success: true,
                message: `Reset overrides for ${deletePromises.length} groups`,
            };
        } catch (err) {
            console.error("Exception resetting all overrides:", err);
            throw err;
        }
    };

    return {
        loading,
        error,
        divisionData,
        groupedData,
        fetchDivisionData,
        saveRatios,
        resetGroupOverrides,
        resetAllOverrides,
    };
}
