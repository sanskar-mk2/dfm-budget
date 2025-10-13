/**
 * Utility functions for downloading data as CSV files
 */

/**
 * Convert data to CSV format
 * @param {Array} data - Array of objects to convert to CSV
 * @param {Array} headers - Array of header objects with 'key' and 'label' properties
 * @returns {string} CSV string
 */
export function convertToCSV(data, headers) {
    if (!data || data.length === 0) return '';
    
    // Create header row
    const headerRow = headers.map(header => `"${header.label}"`).join(',');
    
    // Create data rows
    const dataRows = data.map(row => {
        return headers.map(header => {
            const value = row[header.key];
            // Handle null/undefined values
            if (value === null || value === undefined) return '""';
            // Escape quotes and wrap in quotes
            return `"${String(value).replace(/"/g, '""')}"`;
        }).join(',');
    });
    
    return [headerRow, ...dataRows].join('\n');
}

/**
 * Download data as CSV file
 * @param {Array} data - Array of objects to download
 * @param {Array} headers - Array of header objects with 'key' and 'label' properties
 * @param {string} filename - Name of the file to download
 */
export function downloadCSV(data, headers, filename) {
    const csv = convertToCSV(data, headers);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

/**
 * Format currency for CSV export
 * @param {number} value - Numeric value to format
 * @returns {string} Formatted currency string
 */
export function formatCurrencyForCSV(value) {
    if (value === null || value === undefined || isNaN(value)) return '0.00';
    return parseFloat(value).toFixed(2);
}

/**
 * Generate headers for sales and budget data export
 * @param {boolean} isHospitality - Whether the data is for hospitality users
 * @param {boolean} isMixed - Whether the data contains both hospitality and non-hospitality records
 * @returns {Array} Array of header objects
 */
export function getSalesBudgetHeaders(isHospitality, isMixed = false) {
    const baseHeaders = [
        { key: 'salesperson_name', label: 'Salesperson Name' },
        { key: 'salesperson_id', label: 'Salesperson ID' },
        { key: 'role', label: 'Role' }
    ];
    
    if (isMixed) {
        // For mixed data, include all possible fields
        baseHeaders.push(
            { key: 'brand', label: 'Brand' },
            { key: 'flag', label: 'Flag' },
            { key: 'derived_customer_class', label: 'Customer Class' },
            { key: 'customer_name', label: 'Customer Name' }
        );
    } else if (isHospitality) {
        baseHeaders.push(
            { key: 'brand', label: 'Brand' },
            { key: 'flag', label: 'Flag' }
        );
    } else {
        baseHeaders.push(
            { key: 'derived_customer_class', label: 'Customer Class' },
            { key: 'customer_name', label: 'Customer Name' }
        );
    }
    
    baseHeaders.push(
        { key: 'q1_sales', label: 'Q1 Sales' },
        { key: 'q2_sales', label: 'Q2 Sales' },
        { key: 'q3_sales', label: 'Q3 Sales' },
        { key: 'q4_sales', label: 'Q4 Sales' },
        { key: 'total_sales', label: 'Total Sales' },
        { key: 'zero_perc_sales_total', label: 'Zero % Sales' },
        { key: 'zero_perc_sales_percent', label: 'Zero % %' },
        { key: 'q1_budget', label: 'Q1 Budget' },
        { key: 'q2_budget', label: 'Q2 Budget' },
        { key: 'q3_budget', label: 'Q3 Budget' },
        { key: 'q4_budget', label: 'Q4 Budget' },
        { key: 'growth_percent', label: 'Growth' }
    );
    
    return baseHeaders;
}
