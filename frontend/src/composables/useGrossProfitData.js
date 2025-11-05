import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useGrossProfitData() {
  const auth = useAuthStore();
  const loading = ref(false);
  const raw = ref([]);

  const grouped = computed(() => {
    const map = {};
    for (const r of raw.value) {
      const key = `${r.salesperson_id}-${r.customer_class}-${r.group_key}`;
      if (!map[key]) {
        map[key] = {
          salesperson_id: r.salesperson_id,
          salesperson_name: r.salesperson_name,
          customer_class: r.customer_class,
          group_key: r.group_key,
          brand: r.brand,
          display_key:
            r.customer_class === "Hospitality" && r.brand
              ? `${r.group_key} (${r.brand})`
              : r.group_key,
          effective_gp_percent: r.effective_gp_percent, // Full-year reference value
          is_custom: r.is_custom,
          quarters: [
            { 
              label: "Q1", 
              sales_2025: r.q1_sales_2025, 
              sales: r.quarter_1_sales, 
              gp_percent: r.q1_gp_percent, // Historical GP% for reference
              effective_gp_percent: r.q1_effective_gp_percent || r.q1_gp_percent || r.effective_gp_percent, // Effective GP% (override or fallback)
              gp_value: r.q1_gp_value 
            },
            { 
              label: "Q2", 
              sales_2025: r.q2_sales_2025, 
              sales: r.quarter_2_sales, 
              gp_percent: r.q2_gp_percent, 
              effective_gp_percent: r.q2_effective_gp_percent || r.q2_gp_percent || r.effective_gp_percent, 
              gp_value: r.q2_gp_value 
            },
            { 
              label: "Q3", 
              sales_2025: r.q3_sales_2025, 
              sales: r.quarter_3_sales, 
              gp_percent: r.q3_gp_percent, 
              effective_gp_percent: r.q3_effective_gp_percent || r.q3_gp_percent || r.effective_gp_percent, 
              gp_value: r.q3_gp_value 
            },
            { 
              label: "Q4", 
              sales_2025: r.q4_sales_2025, 
              sales: r.quarter_4_sales, 
              gp_percent: r.q4_gp_percent, 
              effective_gp_percent: r.q4_effective_gp_percent || r.q4_gp_percent || r.effective_gp_percent, 
              gp_value: r.q4_gp_value 
            },
          ],
        };
      }
    }
    return Object.values(map);
  });

  async function fetch() {
    loading.value = true;
    const res = await auth.apiCall("/api/gross-profit");
    const data = await res.json();
    raw.value = data.data || [];
    loading.value = false;
  }

  async function fetchSingleGroup(salespersonId, customerClass, groupKey) {
    const response = await auth.apiCall(
      `/api/gross-profit/${salespersonId}/${encodeURIComponent(customerClass)}/${encodeURIComponent(groupKey)}`
    );
    if (!response.ok) throw new Error("Failed to fetch group");
    const result = await response.json();
    return result.data || [];
  }

  async function save(group) {
    // Collect quarter-specific override values
    // If value differs from default, set it; if it matches default but group had custom overrides, clear it (set to null)
    const override = {
      salesperson_id: group.salesperson_id,
      salesperson_name: group.salesperson_name,
      customer_class: group.customer_class,
      group_key: group.group_key,
    };

    // Helper function to determine if a quarter should have an override
    const processQuarter = (quarter, quarterNum) => {
      if (!quarter || quarter.effective_gp_percent === null || quarter.effective_gp_percent === undefined) {
        return;
      }
      const historical = quarter.gp_percent;
      const fullYear = group.effective_gp_percent;
      const defaultVal = historical !== null && historical !== undefined ? historical : fullYear;
      const currentVal = quarter.effective_gp_percent || 0;
      const diff = Math.abs(currentVal - (defaultVal || 0));
      
      if (diff > 0.001) {
        // Value differs from default - set override
        override[`custom_q${quarterNum}_gp_percent`] = Math.min(Math.max(currentVal, 0), 1);
      } else if (group.is_custom) {
        // Value matches default but group had custom overrides - clear this quarter's override
        override[`custom_q${quarterNum}_gp_percent`] = null;
      }
    };

    // Process each quarter
    const q1 = group.quarters.find(q => q.label === "Q1");
    processQuarter(q1, 1);
    
    const q2 = group.quarters.find(q => q.label === "Q2");
    processQuarter(q2, 2);
    
    const q3 = group.quarters.find(q => q.label === "Q3");
    processQuarter(q3, 3);
    
    const q4 = group.quarters.find(q => q.label === "Q4");
    processQuarter(q4, 4);

    const overrides = [override];

    await auth.apiCall("/api/gross-profit/save-overrides", {
      method: "POST",
      body: JSON.stringify({ overrides }),
    });

    // Fetch only updated group
    const updatedRows = await fetchSingleGroup(group.salesperson_id, group.customer_class, group.group_key);

    // Replace that group locally while maintaining position
    const newData = [...raw.value];
    const groupRows = newData.filter(
      r => r.group_key === group.group_key && r.salesperson_id === group.salesperson_id
    );
    
    if (groupRows.length > 0) {
      // Find the first occurrence of this group
      const firstIndex = newData.findIndex(
        r => r.group_key === group.group_key && r.salesperson_id === group.salesperson_id
      );
      
      // Remove all rows for this group
      const filteredData = newData.filter(
        r => !(r.group_key === group.group_key && r.salesperson_id === group.salesperson_id)
      );
      
      // Insert new data at the original position
      filteredData.splice(firstIndex, 0, ...updatedRows);
      raw.value = filteredData;
    } else {
      // Fallback: just append if group not found
      raw.value = [...raw.value.filter(
        r => !(r.group_key === group.group_key && r.salesperson_id === group.salesperson_id)
      ), ...updatedRows];
    }
  }

  async function reset(group) {
    await auth.apiCall(
      `/api/gross-profit/reset/${group.salesperson_id}/${encodeURIComponent(group.customer_class)}/${encodeURIComponent(group.group_key)}`,
      { method: "DELETE" }
    );
    
    // Fetch only updated group
    const updatedRows = await fetchSingleGroup(group.salesperson_id, group.customer_class, group.group_key);

    // Replace that group locally while maintaining position
    const newData = [...raw.value];
    const groupRows = newData.filter(
      r => r.group_key === group.group_key && r.salesperson_id === group.salesperson_id
    );
    
    if (groupRows.length > 0) {
      // Find the first occurrence of this group
      const firstIndex = newData.findIndex(
        r => r.group_key === group.group_key && r.salesperson_id === group.salesperson_id
      );
      
      // Remove all rows for this group
      const filteredData = newData.filter(
        r => !(r.group_key === group.group_key && r.salesperson_id === group.salesperson_id)
      );
      
      // Insert new data at the original position
      filteredData.splice(firstIndex, 0, ...updatedRows);
      raw.value = filteredData;
    } else {
      // Fallback: just append if group not found
      raw.value = [...raw.value.filter(
        r => !(r.group_key === group.group_key && r.salesperson_id === group.salesperson_id)
      ), ...updatedRows];
    }
  }

  async function resetAll() {
    await auth.apiCall("/api/gross-profit/reset-all", {
      method: "DELETE"
    });
    
    // Get list of groups that had custom overrides
    const groupsWithCustom = grouped.value.filter(g => g.is_custom);
    
    // Fetch updated data for each group that had custom overrides
    const updatePromises = groupsWithCustom.map(group => 
      fetchSingleGroup(group.salesperson_id, group.customer_class, group.group_key)
    );
    
    const updatedGroupsData = await Promise.all(updatePromises);
    
    // Replace all the updated groups in the data
    let newData = [...raw.value];
    
    groupsWithCustom.forEach((group, index) => {
      const updatedRows = updatedGroupsData[index];
      
      // Remove old rows for this group
      newData = newData.filter(
        r => !(r.group_key === group.group_key && r.salesperson_id === group.salesperson_id)
      );
      
      // Add updated rows
      newData.push(...updatedRows);
    });
    
    raw.value = newData;
  }

  return { grouped, fetch, save, reset, resetAll, loading };
}
