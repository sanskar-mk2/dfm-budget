export const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
};

export const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '0';
    return parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
};

export const formatPercentage = (percentage) => {
    if (!percentage && percentage !== 0) return '0.00';
    return parseFloat(percentage).toFixed(2);
};

export const getZeroPercentClass = (percentage) => {
    if (!percentage && percentage !== 0) return '';
    const percent = parseFloat(percentage);
    if (percent === 0) return 'text-success';
    if (percent < 5) return 'text-warning';
    if (percent < 10) return 'text-warning';
    return 'text-error';
};
