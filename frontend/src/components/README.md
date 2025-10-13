# Sales View Components

This directory contains the modularized components for the Sales View functionality.

## Components

### SalesTable.vue
- Displays the main sales data table with budget input fields
- Handles all table rendering and budget cell interactions
- Props: sales data, budget functions
- Uses BudgetInput component for individual cells

### SalesSummary.vue
- Shows summary statistics and totals
- Displays quarterly totals, customer count, and zero percent rates
- Props: sales data, calculation functions

### BudgetInput.vue
- Reusable input component for budget cells
- Handles number input with proper formatting
- Emits change, blur, and input events
- Props: value, cellClass


### UserInfo.vue
- Shows current user and salesperson information
- Simple display component
- Props: currentUser, currentSalesperson

## Composables

### useSalesData.js
- Manages sales data fetching and state
- Provides calculation functions for totals and summaries

### useBudgetData.js
- Manages budget data and interactions
- Handles auto-save functionality
- Manages localStorage for pending changes
- Provides budget cell management functions

## Utils

### formatters.js
- Utility functions for formatting currency, percentages, and dates
- Provides CSS class helpers for styling based on values

## Benefits of This Structure

1. **Separation of Concerns**: Each component has a single responsibility
2. **Reusability**: Components can be reused in other parts of the application
3. **Maintainability**: Easier to modify individual pieces
4. **Testability**: Each component can be tested in isolation
5. **Performance**: Smaller components can be optimized individually
6. **Code Organization**: Clear structure makes the codebase easier to navigate

## Usage

The main SalesView.vue now acts as a coordinator, importing and using these modular components. The heavy lifting is done by the composables, while the UI is broken down into focused, reusable components.
