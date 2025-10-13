# Composables

This directory contains Vue 3 composables that provide reusable stateful logic for the application.

## useSalesData.js

Manages all sales-related data and operations:

### Features
- Sales data fetching and state management
- Summary calculation functions (totals, percentages)
- Loading and error state management

### Returns
- `sales`: Reactive array of sales data
- `loading`: Loading state
- `error`: Error message
- `fetchSales()`: Function to fetch sales data
- Various calculation functions for totals and summaries

## useBudgetData.js

Manages budget-related data and operations:

### Features
- Budget data fetching and state management
- Auto-save functionality with debouncing
- LocalStorage integration for pending changes
- Visual feedback for saving states
- Budget cell management

### Returns
- `budgets`: Reactive array of budget data
- `budgetMap`: Map for quick budget lookups
- `savingCells`: Set of cells currently being saved
- `savedCells`: Set of recently saved cells
- `inputValues`: Current input values
- `fetchBudgets()`: Function to fetch budget data
- `saveBudgetCell()`: Function to save individual budget cells
- `getBudgetValue()`: Function to get budget value for a cell
- `getCellClass()`: Function to get CSS class for a cell
- Various event handlers for budget inputs
- LocalStorage management functions

## Benefits

1. **Reusable Logic**: Can be used across multiple components
2. **Separation of Concerns**: Business logic separated from UI
3. **State Management**: Centralized state management for related data
4. **Performance**: Optimized with Vue 3 reactivity
5. **Testing**: Easier to unit test business logic
6. **Maintainability**: Changes to business logic don't affect UI components
