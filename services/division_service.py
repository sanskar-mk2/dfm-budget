from sqlmodel import Session, text, select
from typing import List, Dict, Any
from db.budget_models import DivisionRatioOverride
from datetime import datetime, date


class DivisionService:
    def __init__(self, db: Session):
        self.db = db

    def _get_sales_normalized(self) -> List[Dict[str, Any]]:
        """
        Normalize sales data (group_key logic)
        Returns list of dicts with: group_key, customer_class, item_division, ext_sales, ext_cost, period
        """
        query = text(
            """
              SELECT
                CASE WHEN s.derived_customer_class LIKE 'Hospitality%'
                     THEN NULLIF(TRIM(s.flag),'')
                     ELSE NULLIF(TRIM(s.customer_name),'')
              END AS group_key,
                s.derived_customer_class AS customer_class,
                s.item_division,
                s.ext_sales,
                s.ext_cost,
                s.period
              FROM sales_budget_2026 s
              WHERE s.period >= '2025-01-01' AND s.period < '2026-01-01'
                AND s.salesperson IS NOT NULL
                AND (
                  (s.derived_customer_class LIKE 'Hospitality%' AND s.flag IS NOT NULL AND s.flag<>'')
                  OR (s.derived_customer_class NOT LIKE 'Hospitality%' AND s.customer_name IS NOT NULL AND s.customer_name<>'')
                )
        """
        )
        result = self.db.exec(query)
        return [
            {
                "group_key": row.group_key,
                "customer_class": row.customer_class,
                "item_division": row.item_division,
                "ext_sales": float(row.ext_sales) if row.ext_sales else 0.0,
                "ext_cost": float(row.ext_cost) if row.ext_cost else 0.0,
                "period": row.period,
            }
            for row in result
        ]

    def _get_grouped_sales(
        self, sales_norm: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Group sales by group_key + division
        Returns list of dicts with: group_key, customer_class, item_division, total_sales, total_cost
        """
        grouped = {}
        for sale in sales_norm:
            if sale["group_key"] is None:
                continue
            key = (sale["group_key"], sale["customer_class"], sale["item_division"])
            if key not in grouped:
                grouped[key] = {
                    "group_key": sale["group_key"],
                    "customer_class": sale["customer_class"],
                    "item_division": sale["item_division"],
                    "total_sales": 0.0,
                    "total_cost": 0.0,
                }
            grouped[key]["total_sales"] += sale["ext_sales"]
            grouped[key]["total_cost"] += sale["ext_cost"]
        return list(grouped.values())

    def _get_group_totals(
        self, grouped_sales: List[Dict[str, Any]]
    ) -> Dict[tuple, float]:
        """
        Calculate totals per group
        Returns dict keyed by (group_key, customer_class) -> total_group_sales
        """
        totals = {}
        for sale in grouped_sales:
            key = (sale["group_key"], sale["customer_class"])
            totals[key] = totals.get(key, 0.0) + sale["total_sales"]
        return totals

    def _get_ratios_raw(
        self, grouped_sales: List[Dict[str, Any]], group_totals: Dict[tuple, float]
    ) -> List[Dict[str, Any]]:
        """
        Calculate raw division ratios (may still have dupes from dirty data)
        Returns list of dicts with: group_key, customer_class, item_division, division_ratio_2025
        """
        ratios = []
        for sale in grouped_sales:
            key = (sale["group_key"], sale["customer_class"])
            total_group_sales = group_totals.get(key, 0.0)
            ratio = (
                0.0
                if total_group_sales == 0
                else sale["total_sales"] / total_group_sales
            )
            ratios.append(
                {
                    "group_key": sale["group_key"],
                    "customer_class": sale["customer_class"],
                    "item_division": sale["item_division"],
                    "division_ratio_2025": ratio,
                }
            )
        return ratios

    def _get_ratios_deduplicated(
        self, ratios_raw: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate ratios (HARD DEDUPE)
        Returns list of dicts with: group_key, customer_class, item_division, division_ratio_2025
        """
        deduped = {}
        for ratio in ratios_raw:
            key = (
                ratio["group_key"],
                ratio["customer_class"],
                ratio["item_division"],
            )
            if key not in deduped:
                deduped[key] = ratio.copy()
            else:
                # Take MAX ratio
                deduped[key]["division_ratio_2025"] = max(
                    deduped[key]["division_ratio_2025"], ratio["division_ratio_2025"]
                )
        return list(deduped.values())

    def _get_ratios_normalized(
        self, ratios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize ratios to sum to 1.0 per group
        Returns list of dicts with: group_key, customer_class, item_division, division_ratio_2025
        """
        # Calculate sum of ratios per group
        ratio_sums = {}
        for ratio in ratios:
            key = (ratio["group_key"], ratio["customer_class"])
            ratio_sums[key] = ratio_sums.get(key, 0.0) + ratio["division_ratio_2025"]

        # Normalize each ratio
        normalized = []
        for ratio in ratios:
            key = (ratio["group_key"], ratio["customer_class"])
            total_sum = ratio_sums.get(key, 0.0)
            normalized_ratio = (
                ratio["division_ratio_2025"] / total_sum if total_sum > 0 else 0.0
            )
            normalized.append(
                {
                    "group_key": ratio["group_key"],
                    "customer_class": ratio["customer_class"],
                    "item_division": ratio["item_division"],
                    "division_ratio_2025": normalized_ratio,
                }
            )
        return normalized

    def _get_budget_normalized(self) -> List[Dict[str, Any]]:
        """
        Normalize budget data
        Returns list of dicts with: salesperson_id, salesperson_name, customer_class, group_key, brand, quarter_1_sales, quarter_2_sales, quarter_3_sales, quarter_4_sales
        """
        query = text(
            """
              SELECT
                b.salesperson_id,
                b.salesperson_name,
                b.customer_class,
                CASE WHEN b.customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(b.flag),'')
                     ELSE NULLIF(TRIM(b.customer_name),'') END AS group_key,
                CASE WHEN b.customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(b.brand),'')
                     ELSE NULL END AS brand,
                b.quarter_1_sales, b.quarter_2_sales, b.quarter_3_sales, b.quarter_4_sales
              FROM dfm_dashboards.budget_2026 b
        """
        )
        result = self.db.exec(query)
        return [
            {
                "salesperson_id": row.salesperson_id,
                "salesperson_name": row.salesperson_name,
                "customer_class": row.customer_class,
                "group_key": row.group_key,
                "brand": row.brand,
                "quarter_1_sales": (
                    float(row.quarter_1_sales) if row.quarter_1_sales else 0.0
                ),
                "quarter_2_sales": (
                    float(row.quarter_2_sales) if row.quarter_2_sales else 0.0
                ),
                "quarter_3_sales": (
                    float(row.quarter_3_sales) if row.quarter_3_sales else 0.0
                ),
                "quarter_4_sales": (
                    float(row.quarter_4_sales) if row.quarter_4_sales else 0.0
                ),
            }
            for row in result
        ]

    def _get_collapsed_budget(
        self, budget_norm: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Collapse budget per salesperson + group_key
        Returns list of dicts with: salesperson_id, salesperson_name, customer_class, group_key, brand, q1_total, q2_total, q3_total, q4_total
        """
        collapsed = {}
        for budget in budget_norm:
            key = (
                budget["salesperson_id"],
                budget["salesperson_name"],
                budget["customer_class"],
                budget["group_key"],
            )
            if key not in collapsed:
                collapsed[key] = {
                    "salesperson_id": budget["salesperson_id"],
                    "salesperson_name": budget["salesperson_name"],
                    "customer_class": budget["customer_class"],
                    "group_key": budget["group_key"],
                    "brand": budget["brand"],
                    "q1_total": 0.0,
                    "q2_total": 0.0,
                    "q3_total": 0.0,
                    "q4_total": 0.0,
                }
            collapsed[key]["q1_total"] += budget["quarter_1_sales"]
            collapsed[key]["q2_total"] += budget["quarter_2_sales"]
            collapsed[key]["q3_total"] += budget["quarter_3_sales"]
            collapsed[key]["q4_total"] += budget["quarter_4_sales"]
            # Keep MAX brand
            if budget["brand"] and (
                not collapsed[key]["brand"] or budget["brand"] > collapsed[key]["brand"]
            ):
                collapsed[key]["brand"] = budget["brand"]
        return list(collapsed.values())

    def _get_divisions_deduplicated(self) -> List[Dict[str, Any]]:
        """
        Get unique divisions (guard against duplicate div_no rows)
        Returns list of dicts with: div_no, div_desc
        """
        query = text(
            """
              SELECT d.div_no, MIN(d.div_desc) AS div_desc
              FROM dfm_dashboards.division_masters d
              GROUP BY d.div_no
        """
        )
        result = self.db.exec(query)
        return [
            {
                "div_no": row.div_no,
                "div_desc": row.div_desc,
            }
            for row in result
        ]

    def _get_overall_division_totals(
        self, grouped_sales: List[Dict[str, Any]]
    ) -> Dict[int, float]:
        """
        Total sales per division across all groups
        Returns dict keyed by item_division -> total_division_sales
        """
        totals = {}
        for sale in grouped_sales:
            div = sale["item_division"]
            totals[div] = totals.get(div, 0.0) + sale["total_sales"]
        return totals

    def _get_default_division_ratios(
        self, divisions: List[Dict[str, Any]], overall_division_totals: Dict[int, float]
    ) -> Dict[int, float]:
        """
        Overall division ratios (default for missing historical data)
        Returns dict keyed by item_division -> default_ratio
        """
        grand_total = sum(overall_division_totals.values())
        default_ratios = {}
        for div in divisions:
            div_no = div["div_no"]
            division_sales = overall_division_totals.get(div_no, 0.0)
            default_ratio = division_sales / grand_total if grand_total > 0 else 0.0
            default_ratios[div_no] = default_ratio
        return default_ratios

    def _get_group_historical_totals(
        self, grouped_sales: List[Dict[str, Any]]
    ) -> Dict[tuple, float]:
        """
        Check if group has any historical sales
        Returns dict keyed by (group_key, customer_class) -> group_total_sales
        """
        totals = {}
        for sale in grouped_sales:
            key = (sale["group_key"], sale["customer_class"])
            totals[key] = totals.get(key, 0.0) + sale["total_sales"]
        return totals

    def _get_gp_by_division(
        self, sales_norm: List[Dict[str, Any]]
    ) -> Dict[tuple, Dict[str, Any]]:
        """
        Calculate GP% and GP$ by division (group_key, customer_class, item_division)
        Returns dict keyed by (group_key, customer_class, item_division) -> GP data
        """
        # Group sales by division and quarter
        division_quarter_data = {}
        for sale in sales_norm:
            if sale["group_key"] is None:
                continue

            # Determine quarter
            period = sale["period"]
            if isinstance(period, str):
                period = datetime.strptime(period, "%Y-%m-%d").date()
            q1_start = date(2025, 1, 1)
            q2_start = date(2025, 4, 1)
            q3_start = date(2025, 7, 1)
            q4_start = date(2025, 10, 1)
            q4_end = date(2026, 1, 1)

            if period >= q1_start and period < q2_start:
                quarter = "q1"
            elif period >= q2_start and period < q3_start:
                quarter = "q2"
            elif period >= q3_start and period < q4_start:
                quarter = "q3"
            elif period >= q4_start and period < q4_end:
                quarter = "q4"
            else:
                continue

            key = (
                sale["group_key"],
                sale["customer_class"],
                sale["item_division"],
                quarter,
            )
            if key not in division_quarter_data:
                division_quarter_data[key] = {
                    "sales": 0.0,
                    "cost": 0.0,
                }
            division_quarter_data[key]["sales"] += sale["ext_sales"]
            division_quarter_data[key]["cost"] += sale["ext_cost"]

        # Calculate GP% for each division
        gp_by_division = {}
        for (
            group_key,
            customer_class,
            item_division,
            quarter,
        ), data in division_quarter_data.items():
            div_key = (group_key, customer_class, item_division)
            if div_key not in gp_by_division:
                gp_by_division[div_key] = {
                    "q1_sales": 0.0,
                    "q1_cost": 0.0,
                    "q2_sales": 0.0,
                    "q2_cost": 0.0,
                    "q3_sales": 0.0,
                    "q3_cost": 0.0,
                    "q4_sales": 0.0,
                    "q4_cost": 0.0,
                }

            gp_by_division[div_key][f"{quarter}_sales"] = data["sales"]
            gp_by_division[div_key][f"{quarter}_cost"] = data["cost"]

        # Calculate GP% for each division
        gp_percentages = {}
        for div_key, data in gp_by_division.items():
            total_sales = (
                data["q1_sales"]
                + data["q2_sales"]
                + data["q3_sales"]
                + data["q4_sales"]
            )
            total_cost = (
                data["q1_cost"] + data["q2_cost"] + data["q3_cost"] + data["q4_cost"]
            )

            # Calculate quarterly GP%
            q1_gp_percent = None
            if data["q1_sales"] > 0:
                q1_gp_percent = round(1 - (data["q1_cost"] / data["q1_sales"]), 6)
            elif total_sales > 0:
                q1_gp_percent = round(1 - (total_cost / total_sales), 6)

            q2_gp_percent = None
            if data["q2_sales"] > 0:
                q2_gp_percent = round(1 - (data["q2_cost"] / data["q2_sales"]), 6)
            elif total_sales > 0:
                q2_gp_percent = round(1 - (total_cost / total_sales), 6)

            q3_gp_percent = None
            if data["q3_sales"] > 0:
                q3_gp_percent = round(1 - (data["q3_cost"] / data["q3_sales"]), 6)
            elif total_sales > 0:
                q3_gp_percent = round(1 - (total_cost / total_sales), 6)

            q4_gp_percent = None
            if data["q4_sales"] > 0:
                q4_gp_percent = round(1 - (data["q4_cost"] / data["q4_sales"]), 6)
            elif total_sales > 0:
                q4_gp_percent = round(1 - (total_cost / total_sales), 6)

            # Full year GP%
            full_year_gp_percent = None
            if total_sales > 0:
                full_year_gp_percent = round(1 - (total_cost / total_sales), 6)

            gp_percentages[div_key] = {
                "q1_gp_percent": q1_gp_percent,
                "q2_gp_percent": q2_gp_percent,
                "q3_gp_percent": q3_gp_percent,
                "q4_gp_percent": q4_gp_percent,
                "full_year_gp_percent": full_year_gp_percent,
                # Also include quarterly sales for GP$ calculation
                "q1_sales": data["q1_sales"],
                "q2_sales": data["q2_sales"],
                "q3_sales": data["q3_sales"],
                "q4_sales": data["q4_sales"],
            }

        return gp_percentages

    def _get_ratio_overrides(self) -> Dict[tuple, float]:
        """
        Get custom ratio overrides
        Returns dict keyed by (salesperson_id, customer_class, group_key, item_division) -> custom_ratio
        """
        query = text(
            """
            SELECT salesperson_id, customer_class, group_key, item_division, custom_ratio
            FROM division_ratio_overrides
        """
        )
        result = self.db.exec(query)
        overrides = {}
        for row in result:
            key = (
                row.salesperson_id,
                row.customer_class,
                row.group_key,
                row.item_division,
            )
            overrides[key] = float(row.custom_ratio) if row.custom_ratio else 0.0
        return overrides

    def _get_sales_only_groups(
        self,
        grouped_sales: List[Dict[str, Any]],
        collapsed_budget: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Get sales groups that don't have budgets
        Returns list of dicts with: salesperson_id, salesperson_name, customer_class, group_key, brand
        """
        # Query to get sales groups with salesperson info that don't have budgets
        query = text(
            """
            SELECT DISTINCT
              s.salesperson AS salesperson_id,
              COALESCE(sp.salesman_name, CONCAT('Salesperson ', s.salesperson)) AS salesperson_name,
              s.derived_customer_class AS customer_class,
              CASE WHEN s.derived_customer_class LIKE 'Hospitality%'
                   THEN NULLIF(TRIM(s.flag),'')
                   ELSE NULLIF(TRIM(s.customer_name),'')
              END AS group_key,
              CASE WHEN s.derived_customer_class LIKE 'Hospitality%' THEN MAX(NULLIF(TRIM(s.brand),''))
                   ELSE NULL END AS brand
            FROM sales_budget_2026 s
            LEFT JOIN salesperson_masters sp ON sp.salesman_no = s.salesperson
            WHERE s.period >= '2025-01-01' AND s.period < '2026-01-01'
              AND s.salesperson IS NOT NULL
              AND (
                (s.derived_customer_class LIKE 'Hospitality%' AND s.flag IS NOT NULL AND s.flag<>'')
                OR (s.derived_customer_class NOT LIKE 'Hospitality%' AND s.customer_name IS NOT NULL AND s.customer_name<>'')
              )
              AND NOT EXISTS (
                SELECT 1 FROM dfm_dashboards.budget_2026 b
                WHERE b.salesperson_id = s.salesperson
                  AND b.customer_class = s.derived_customer_class
                  AND CASE WHEN b.customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(b.flag),'') ELSE NULLIF(TRIM(b.customer_name),'') END = 
                      CASE WHEN s.derived_customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(s.flag),'') ELSE NULLIF(TRIM(s.customer_name),'') END
              )
            GROUP BY s.salesperson, sp.salesman_name,
                     s.derived_customer_class,
                     CASE WHEN s.derived_customer_class LIKE 'Hospitality%' THEN NULLIF(TRIM(s.flag),'') ELSE NULLIF(TRIM(s.customer_name),'') END
        """
        )
        result = self.db.exec(query)
        return [
            {
                "salesperson_id": row.salesperson_id,
                "salesperson_name": row.salesperson_name,
                "customer_class": row.customer_class,
                "group_key": row.group_key,
                "brand": row.brand,
            }
            for row in result
        ]

    def get_division_allocations(self) -> List[Dict[str, Any]]:
        """
        Get division allocations with custom ratio overrides applied
        """
        # Step 1: Get normalized sales data
        sales_norm = self._get_sales_normalized()

        # Step 2: Group sales by group_key + division
        grouped_sales = self._get_grouped_sales(sales_norm)

        # Step 3: Calculate group totals
        group_totals = self._get_group_totals(grouped_sales)

        # Step 4: Calculate raw ratios
        ratios_raw = self._get_ratios_raw(grouped_sales, group_totals)

        # Step 5: Deduplicate ratios
        ratios = self._get_ratios_deduplicated(ratios_raw)

        # Step 6: Normalize ratios
        ratios_normalized = self._get_ratios_normalized(ratios)

        # Step 7: Get normalized budget data
        budget_norm = self._get_budget_normalized()

        # Step 8: Collapse budget per salesperson + group_key
        collapsed_budget = self._get_collapsed_budget(budget_norm)

        # Step 9: Get divisions
        divisions = self._get_divisions_deduplicated()

        # Step 10: Get overall division totals
        overall_division_totals = self._get_overall_division_totals(grouped_sales)

        # Step 11: Get default division ratios
        default_division_ratios = self._get_default_division_ratios(
            divisions, overall_division_totals
        )

        # Step 12: Get group historical totals
        group_historical_totals = self._get_group_historical_totals(grouped_sales)

        # Step 13: Get ratio overrides
        ratio_overrides = self._get_ratio_overrides()

        # Step 14: Get sales-only groups (groups with sales but no budget)
        sales_only_groups = self._get_sales_only_groups(grouped_sales, collapsed_budget)

        # Step 15: Get GP data by division
        gp_by_division = self._get_gp_by_division(sales_norm)

        # Create lookup dictionaries for efficient access
        ratios_lookup = {
            (r["group_key"], r["customer_class"], r["item_division"]): r[
                "division_ratio_2025"
            ]
            for r in ratios_normalized
        }

        grouped_sales_lookup = {
            (gs["group_key"], gs["customer_class"], gs["item_division"]): gs[
                "total_sales"
            ]
            for gs in grouped_sales
        }

        # Step 16: Combine all data (equivalent to the final SELECT with CROSS JOIN and LEFT JOINs)
        division_data = []
        # Track which (group_key, customer_class, item_division) combinations have already shown sales
        # to prevent double-counting when multiple salespeople have budgets for the same group
        sales_shown = set()

        # Process budget rows
        for budget in collapsed_budget:
            for division in divisions:
                # Get keys for lookups
                group_key = budget["group_key"]
                customer_class = budget["customer_class"]
                item_division = division["div_no"]
                salesperson_id = budget["salesperson_id"]

                # Get historical total for this group
                ght_key = (group_key, customer_class)
                group_total_sales = group_historical_totals.get(ght_key, 0.0)

                # Get ratio override if exists
                override_key = (
                    salesperson_id,
                    customer_class,
                    group_key,
                    item_division,
                )
                custom_ratio = ratio_overrides.get(override_key)

                # Determine effective ratio
                if custom_ratio is not None:
                    effective_ratio = custom_ratio
                    is_custom = True
                elif group_total_sales == 0:
                    effective_ratio = default_division_ratios.get(item_division, 0.0)
                    is_custom = False
                else:
                    ratio_key = (group_key, customer_class, item_division)
                    effective_ratio = ratios_lookup.get(ratio_key, 0.0)
                    is_custom = False

                # Calculate uses_default_ratios flag
                uses_default_ratios = (
                    1 if (group_total_sales == 0 and custom_ratio is None) else 0
                )

                # Get budget totals
                q1_total = budget["q1_total"]
                q2_total = budget["q2_total"]
                q3_total = budget["q3_total"]
                q4_total = budget["q4_total"]
                total_budget_total = q1_total + q2_total + q3_total + q4_total

                # Calculate allocated amounts
                q1_allocated = round(q1_total * effective_ratio, 2)
                q2_allocated = round(q2_total * effective_ratio, 2)
                q3_allocated = round(q3_total * effective_ratio, 2)
                q4_allocated = round(q4_total * effective_ratio, 2)
                total_allocated = round(total_budget_total * effective_ratio, 2)

                # Get division ratio 2025 (without override)
                if group_total_sales == 0:
                    division_ratio_2025 = default_division_ratios.get(
                        item_division, 0.0
                    )
                else:
                    ratio_key = (group_key, customer_class, item_division)
                    division_ratio_2025 = ratios_lookup.get(ratio_key, 0.0)

                # Get total 2025 sales - only show once per (group_key, customer_class, item_division)
                # to prevent double-counting when multiple salespeople have budgets for the same group
                sales_key = (group_key, customer_class, item_division)
                if sales_key in sales_shown:
                    # Don't duplicate sales for this group-division combination
                    total_2025_sales = 0.0
                    # Also don't duplicate GP values
                    q1_gp_value = 0.0
                    q2_gp_value = 0.0
                    q3_gp_value = 0.0
                    q4_gp_value = 0.0
                    total_gp_value = 0.0
                    gp_percent = None
                    # For duplicates, set quarterly data to 0/None
                    q1_sales_display = 0.0
                    q2_sales_display = 0.0
                    q3_sales_display = 0.0
                    q4_sales_display = 0.0
                    q1_gp_percent_display = None
                    q2_gp_percent_display = None
                    q3_gp_percent_display = None
                    q4_gp_percent_display = None
                else:
                    total_2025_sales = grouped_sales_lookup.get(sales_key, 0.0)
                    sales_shown.add(sales_key)

                    # Get GP data for this division
                    gp_data = gp_by_division.get(sales_key, {})
                    gp_percent = gp_data.get("full_year_gp_percent")

                    # Calculate GP$ from actual 2025 sales, not from allocated budget
                    # Get quarterly sales from GP data
                    q1_sales = gp_data.get("q1_sales", 0.0) if gp_data else 0.0
                    q2_sales = gp_data.get("q2_sales", 0.0) if gp_data else 0.0
                    q3_sales = gp_data.get("q3_sales", 0.0) if gp_data else 0.0
                    q4_sales = gp_data.get("q4_sales", 0.0) if gp_data else 0.0

                    # Use quarter-specific GP% if available, otherwise use full year
                    q1_gp_percent = gp_data.get("q1_gp_percent") or gp_percent
                    q2_gp_percent = gp_data.get("q2_gp_percent") or gp_percent
                    q3_gp_percent = gp_data.get("q3_gp_percent") or gp_percent
                    q4_gp_percent = gp_data.get("q4_gp_percent") or gp_percent

                    # Calculate GP$ from actual quarterly sales
                    q1_gp_value = (
                        round(q1_sales * (q1_gp_percent or 0), 2)
                        if q1_gp_percent and q1_sales > 0
                        else 0.0
                    )
                    q2_gp_value = (
                        round(q2_sales * (q2_gp_percent or 0), 2)
                        if q2_gp_percent and q2_sales > 0
                        else 0.0
                    )
                    q3_gp_value = (
                        round(q3_sales * (q3_gp_percent or 0), 2)
                        if q3_gp_percent and q3_sales > 0
                        else 0.0
                    )
                    q4_gp_value = (
                        round(q4_sales * (q4_gp_percent or 0), 2)
                        if q4_gp_percent and q4_sales > 0
                        else 0.0
                    )
                    # Total GP$ from actual total sales
                    total_gp_value = (
                        round(total_2025_sales * (gp_percent or 0), 2)
                        if gp_percent and total_2025_sales > 0
                        else 0.0
                    )

                    # Get quarterly sales and GP% for display
                    q1_sales_display = q1_sales
                    q2_sales_display = q2_sales
                    q3_sales_display = q3_sales
                    q4_sales_display = q4_sales
                    q1_gp_percent_display = q1_gp_percent
                    q2_gp_percent_display = q2_gp_percent
                    q3_gp_percent_display = q3_gp_percent
                    q4_gp_percent_display = q4_gp_percent

                division_data.append(
                    {
                        "salesperson_id": salesperson_id,
                        "salesperson_name": budget["salesperson_name"],
                        "customer_class": customer_class,
                        "group_key": group_key,
                        "brand": budget["brand"],
                        "item_division": item_division,
                        "division_name": division["div_desc"],
                        "effective_ratio": effective_ratio,
                        "is_custom": bool(is_custom),
                        "uses_default_ratios": bool(uses_default_ratios),
                        "q1_budget_total": q1_total,
                        "q2_budget_total": q2_total,
                        "q3_budget_total": q3_total,
                        "q4_budget_total": q4_total,
                        "total_budget_total": total_budget_total,
                        "q1_allocated": q1_allocated,
                        "q2_allocated": q2_allocated,
                        "q3_allocated": q3_allocated,
                        "q4_allocated": q4_allocated,
                        "total_allocated": total_allocated,
                        "division_ratio_2025": division_ratio_2025,
                        "total_2025_sales": total_2025_sales,
                        "q1_sales": q1_sales_display,
                        "q2_sales": q2_sales_display,
                        "q3_sales": q3_sales_display,
                        "q4_sales": q4_sales_display,
                        "gp_percent": gp_percent,
                        "q1_gp_percent": q1_gp_percent_display,
                        "q2_gp_percent": q2_gp_percent_display,
                        "q3_gp_percent": q3_gp_percent_display,
                        "q4_gp_percent": q4_gp_percent_display,
                        "q1_gp_value": q1_gp_value,
                        "q2_gp_value": q2_gp_value,
                        "q3_gp_value": q3_gp_value,
                        "q4_gp_value": q4_gp_value,
                        "total_gp_value": total_gp_value,
                        "has_budget": True,
                    }
                )

        # Process sales-only rows (groups with sales but no budget)
        for sales_group in sales_only_groups:
            for division in divisions:
                # Get keys for lookups
                group_key = sales_group["group_key"]
                customer_class = sales_group["customer_class"]
                item_division = division["div_no"]
                salesperson_id = sales_group["salesperson_id"]

                # Get historical total for this group
                ght_key = (group_key, customer_class)
                group_total_sales = group_historical_totals.get(ght_key, 0.0)

                # No custom ratio overrides for sales-only rows
                custom_ratio = None

                # Determine effective ratio (no custom overrides for sales-only)
                if group_total_sales == 0:
                    effective_ratio = default_division_ratios.get(item_division, 0.0)
                else:
                    ratio_key = (group_key, customer_class, item_division)
                    effective_ratio = ratios_lookup.get(ratio_key, 0.0)

                is_custom = False
                uses_default_ratios = 1 if (group_total_sales == 0) else 0

                # Budget totals are 0 for sales-only rows
                q1_total = 0.0
                q2_total = 0.0
                q3_total = 0.0
                q4_total = 0.0
                total_budget_total = 0.0

                # Allocated amounts are 0 for sales-only rows
                q1_allocated = 0.0
                q2_allocated = 0.0
                q3_allocated = 0.0
                q4_allocated = 0.0
                total_allocated = 0.0

                # Get division ratio 2025 (without override)
                if group_total_sales == 0:
                    division_ratio_2025 = default_division_ratios.get(
                        item_division, 0.0
                    )
                else:
                    ratio_key = (group_key, customer_class, item_division)
                    division_ratio_2025 = ratios_lookup.get(ratio_key, 0.0)

                # Get total 2025 sales - only show once per (group_key, customer_class, item_division)
                sales_key = (group_key, customer_class, item_division)
                if sales_key in sales_shown:
                    total_2025_sales = 0.0
                    # Also don't duplicate GP values
                    q1_gp_value = 0.0
                    q2_gp_value = 0.0
                    q3_gp_value = 0.0
                    q4_gp_value = 0.0
                    total_gp_value = 0.0
                    gp_percent = None
                    # Set quarterly data to 0/None for duplicates
                    q1_sales_display = 0.0
                    q2_sales_display = 0.0
                    q3_sales_display = 0.0
                    q4_sales_display = 0.0
                    q1_gp_percent_display = None
                    q2_gp_percent_display = None
                    q3_gp_percent_display = None
                    q4_gp_percent_display = None
                else:
                    total_2025_sales = grouped_sales_lookup.get(sales_key, 0.0)
                    sales_shown.add(sales_key)

                    # Get GP data for this division
                    gp_data = gp_by_division.get(sales_key, {})
                    gp_percent = gp_data.get("full_year_gp_percent")

                    # Calculate GP$ from actual 2025 sales (not from allocated, which is 0 for sales-only)
                    # Get quarterly sales from GP data
                    q1_sales = gp_data.get("q1_sales", 0.0) if gp_data else 0.0
                    q2_sales = gp_data.get("q2_sales", 0.0) if gp_data else 0.0
                    q3_sales = gp_data.get("q3_sales", 0.0) if gp_data else 0.0
                    q4_sales = gp_data.get("q4_sales", 0.0) if gp_data else 0.0

                    # Use quarter-specific GP% if available, otherwise use full year
                    q1_gp_percent = gp_data.get("q1_gp_percent") or gp_percent
                    q2_gp_percent = gp_data.get("q2_gp_percent") or gp_percent
                    q3_gp_percent = gp_data.get("q3_gp_percent") or gp_percent
                    q4_gp_percent = gp_data.get("q4_gp_percent") or gp_percent

                    # Calculate GP$ from actual quarterly sales
                    q1_gp_value = (
                        round(q1_sales * (q1_gp_percent or 0), 2)
                        if q1_gp_percent and q1_sales > 0
                        else 0.0
                    )
                    q2_gp_value = (
                        round(q2_sales * (q2_gp_percent or 0), 2)
                        if q2_gp_percent and q2_sales > 0
                        else 0.0
                    )
                    q3_gp_value = (
                        round(q3_sales * (q3_gp_percent or 0), 2)
                        if q3_gp_percent and q3_sales > 0
                        else 0.0
                    )
                    q4_gp_value = (
                        round(q4_sales * (q4_gp_percent or 0), 2)
                        if q4_gp_percent and q4_sales > 0
                        else 0.0
                    )
                    # Total GP$ from actual total sales
                    total_gp_value = (
                        round(total_2025_sales * (gp_percent or 0), 2)
                        if gp_percent and total_2025_sales > 0
                        else 0.0
                    )

                    # Get quarterly sales and GP% for display
                    q1_sales_display = q1_sales
                    q2_sales_display = q2_sales
                    q3_sales_display = q3_sales
                    q4_sales_display = q4_sales
                    q1_gp_percent_display = q1_gp_percent
                    q2_gp_percent_display = q2_gp_percent
                    q3_gp_percent_display = q3_gp_percent
                    q4_gp_percent_display = q4_gp_percent

                division_data.append(
                    {
                        "salesperson_id": salesperson_id,
                        "salesperson_name": sales_group["salesperson_name"],
                        "customer_class": customer_class,
                        "group_key": group_key,
                        "brand": sales_group["brand"],
                        "item_division": item_division,
                        "division_name": division["div_desc"],
                        "effective_ratio": effective_ratio,
                        "is_custom": is_custom,
                        "uses_default_ratios": bool(uses_default_ratios),
                        "q1_budget_total": q1_total,
                        "q2_budget_total": q2_total,
                        "q3_budget_total": q3_total,
                        "q4_budget_total": q4_total,
                        "total_budget_total": total_budget_total,
                        "q1_allocated": q1_allocated,
                        "q2_allocated": q2_allocated,
                        "q3_allocated": q3_allocated,
                        "q4_allocated": q4_allocated,
                        "total_allocated": total_allocated,
                        "division_ratio_2025": division_ratio_2025,
                        "total_2025_sales": total_2025_sales,
                        "q1_sales": q1_sales_display,
                        "q2_sales": q2_sales_display,
                        "q3_sales": q3_sales_display,
                        "q4_sales": q4_sales_display,
                        "gp_percent": gp_percent,
                        "q1_gp_percent": q1_gp_percent_display,
                        "q2_gp_percent": q2_gp_percent_display,
                        "q3_gp_percent": q3_gp_percent_display,
                        "q4_gp_percent": q4_gp_percent_display,
                        "q1_gp_value": q1_gp_value,
                        "q2_gp_value": q2_gp_value,
                        "q3_gp_value": q3_gp_value,
                        "q4_gp_value": q4_gp_value,
                        "total_gp_value": total_gp_value,
                        "has_budget": False,
                    }
                )

        # Sort by customer_class, salesperson_name, group_key, item_division
        division_data.sort(
            key=lambda x: (
                x["customer_class"],
                x["salesperson_name"],
                x["group_key"] or "",
                x["item_division"],
            )
        )

        return division_data

    def save_ratio_overrides(self, overrides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save custom ratio overrides for divisions
        """
        try:
            saved_count = 0
            updated_count = 0

            for override in overrides:
                # Check if override already exists
                existing = self.db.exec(
                    select(DivisionRatioOverride).where(
                        DivisionRatioOverride.salesperson_id
                        == override["salesperson_id"],
                        DivisionRatioOverride.customer_class
                        == override["customer_class"],
                        DivisionRatioOverride.group_key == override["group_key"],
                        DivisionRatioOverride.item_division
                        == override["item_division"],
                    )
                ).first()

                if existing:
                    # Update existing override
                    existing.custom_ratio = override["custom_ratio"]
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new override
                    new_override = DivisionRatioOverride(
                        salesperson_id=override["salesperson_id"],
                        salesperson_name=override["salesperson_name"],
                        customer_class=override["customer_class"],
                        group_key=override["group_key"],
                        item_division=override["item_division"],
                        custom_ratio=override["custom_ratio"],
                    )
                    self.db.add(new_override)
                    saved_count += 1

            self.db.commit()

            return {
                "success": True,
                "saved_count": saved_count,
                "updated_count": updated_count,
                "total_processed": len(overrides),
            }

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_ratio_override(
        self,
        salesperson_id: int,
        customer_class: str,
        group_key: str,
        item_division: int,
    ) -> bool:
        """
        Delete a custom ratio override (reset to default)
        """
        try:
            override = self.db.exec(
                select(DivisionRatioOverride).where(
                    DivisionRatioOverride.salesperson_id == salesperson_id,
                    DivisionRatioOverride.customer_class == customer_class,
                    DivisionRatioOverride.group_key == group_key,
                    DivisionRatioOverride.item_division == item_division,
                )
            ).first()

            if override:
                self.db.delete(override)
                self.db.commit()
                return True
            return False

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_group_overrides(
        self, salesperson_id: int, customer_class: str, group_key: str
    ) -> int:
        """
        Delete all custom ratio overrides for a specific group
        """
        try:
            result = self.db.exec(
                text(
                    """
                    DELETE FROM division_ratio_overrides 
                    WHERE salesperson_id = :salesperson_id 
                    AND customer_class = :customer_class 
                    AND group_key = :group_key
                """
                ).bindparams(
                    salesperson_id=salesperson_id,
                    customer_class=customer_class,
                    group_key=group_key,
                )
            )
            self.db.commit()
            return result.rowcount

        except Exception as e:
            self.db.rollback()
            raise e

    def get_division_allocations_for_group(
        self, salesperson_id: int, customer_class: str, group_key: str
    ) -> List[Dict[str, Any]]:
        """
        Get allocations for a single group (filtered)
        """
        # Step 1: Get normalized sales data
        sales_norm = self._get_sales_normalized()

        # Step 2: Group sales by group_key + division
        grouped_sales = self._get_grouped_sales(sales_norm)

        # Step 3: Calculate group totals
        group_totals = self._get_group_totals(grouped_sales)

        # Step 4: Calculate raw ratios
        ratios_raw = self._get_ratios_raw(grouped_sales, group_totals)

        # Step 5: Deduplicate ratios
        ratios = self._get_ratios_deduplicated(ratios_raw)

        # Step 6: Normalize ratios
        ratios_normalized = self._get_ratios_normalized(ratios)

        # Step 7: Get normalized budget data
        budget_norm = self._get_budget_normalized()

        # Step 8: Collapse budget per salesperson + group_key
        collapsed_budget = self._get_collapsed_budget(budget_norm)

        # Step 9: Get divisions
        divisions = self._get_divisions_deduplicated()

        # Step 10: Get overall division totals
        overall_division_totals = self._get_overall_division_totals(grouped_sales)

        # Step 11: Get default division ratios
        default_division_ratios = self._get_default_division_ratios(
            divisions, overall_division_totals
        )

        # Step 12: Get group historical totals
        group_historical_totals = self._get_group_historical_totals(grouped_sales)

        # Step 13: Get ratio overrides
        ratio_overrides = self._get_ratio_overrides()

        # Step 14: Get GP data by division
        gp_by_division = self._get_gp_by_division(sales_norm)

        # Create lookup dictionaries for efficient access
        ratios_lookup = {
            (r["group_key"], r["customer_class"], r["item_division"]): r[
                "division_ratio_2025"
            ]
            for r in ratios_normalized
        }

        grouped_sales_lookup = {
            (gs["group_key"], gs["customer_class"], gs["item_division"]): gs[
                "total_sales"
            ]
            for gs in grouped_sales
        }

        # Step 15: Filter collapsed_budget to only the requested group
        filtered_budgets = [
            b
            for b in collapsed_budget
            if b["salesperson_id"] == salesperson_id
            and b["customer_class"] == customer_class
            and b["group_key"] == group_key
        ]

        # Step 16: Combine all data (equivalent to the final SELECT with CROSS JOIN and LEFT JOINs)
        division_data = []
        # Track which (group_key, customer_class, item_division) combinations have already shown sales
        # to prevent double-counting when multiple salespeople have budgets for the same group
        sales_shown = set()

        for budget in filtered_budgets:
            for division in divisions:
                # Get keys for lookups
                group_key_val = budget["group_key"]
                customer_class_val = budget["customer_class"]
                item_division = division["div_no"]
                salesperson_id_val = budget["salesperson_id"]

                # Get historical total for this group
                ght_key = (group_key_val, customer_class_val)
                group_total_sales = group_historical_totals.get(ght_key, 0.0)

                # Get ratio override if exists
                override_key = (
                    salesperson_id_val,
                    customer_class_val,
                    group_key_val,
                    item_division,
                )
                custom_ratio = ratio_overrides.get(override_key)

                # Determine effective ratio
                if custom_ratio is not None:
                    effective_ratio = custom_ratio
                    is_custom = True
                elif group_total_sales == 0:
                    effective_ratio = default_division_ratios.get(item_division, 0.0)
                    is_custom = False
                else:
                    ratio_key = (group_key_val, customer_class_val, item_division)
                    effective_ratio = ratios_lookup.get(ratio_key, 0.0)
                    is_custom = False

                # Calculate uses_default_ratios flag
                uses_default_ratios = (
                    1 if (group_total_sales == 0 and custom_ratio is None) else 0
                )

                # Get budget totals
                q1_total = budget["q1_total"]
                q2_total = budget["q2_total"]
                q3_total = budget["q3_total"]
                q4_total = budget["q4_total"]
                total_budget_total = q1_total + q2_total + q3_total + q4_total

                # Calculate allocated amounts
                q1_allocated = round(q1_total * effective_ratio, 2)
                q2_allocated = round(q2_total * effective_ratio, 2)
                q3_allocated = round(q3_total * effective_ratio, 2)
                q4_allocated = round(q4_total * effective_ratio, 2)
                total_allocated = round(total_budget_total * effective_ratio, 2)

                # Get division ratio 2025 (without override)
                if group_total_sales == 0:
                    division_ratio_2025 = default_division_ratios.get(
                        item_division, 0.0
                    )
                else:
                    ratio_key = (group_key_val, customer_class_val, item_division)
                    division_ratio_2025 = ratios_lookup.get(ratio_key, 0.0)

                # Get total 2025 sales - only show once per (group_key, customer_class, item_division)
                # to prevent double-counting when multiple salespeople have budgets for the same group
                sales_key = (group_key_val, customer_class_val, item_division)
                if sales_key in sales_shown:
                    # Don't duplicate sales for this group-division combination
                    total_2025_sales = 0.0
                    # Also don't duplicate GP values
                    q1_gp_value = 0.0
                    q2_gp_value = 0.0
                    q3_gp_value = 0.0
                    q4_gp_value = 0.0
                    total_gp_value = 0.0
                    gp_percent = None
                    # Set quarterly data to 0/None for duplicates
                    q1_sales_display = 0.0
                    q2_sales_display = 0.0
                    q3_sales_display = 0.0
                    q4_sales_display = 0.0
                    q1_gp_percent_display = None
                    q2_gp_percent_display = None
                    q3_gp_percent_display = None
                    q4_gp_percent_display = None
                else:
                    total_2025_sales = grouped_sales_lookup.get(sales_key, 0.0)
                    sales_shown.add(sales_key)

                    # Get GP data for this division
                    gp_data = gp_by_division.get(sales_key, {})
                    gp_percent = gp_data.get("full_year_gp_percent")

                    # Calculate GP$ from actual 2025 sales, not from allocated budget
                    # Get quarterly sales from GP data
                    q1_sales = gp_data.get("q1_sales", 0.0) if gp_data else 0.0
                    q2_sales = gp_data.get("q2_sales", 0.0) if gp_data else 0.0
                    q3_sales = gp_data.get("q3_sales", 0.0) if gp_data else 0.0
                    q4_sales = gp_data.get("q4_sales", 0.0) if gp_data else 0.0

                    # Use quarter-specific GP% if available, otherwise use full year
                    q1_gp_percent = gp_data.get("q1_gp_percent") or gp_percent
                    q2_gp_percent = gp_data.get("q2_gp_percent") or gp_percent
                    q3_gp_percent = gp_data.get("q3_gp_percent") or gp_percent
                    q4_gp_percent = gp_data.get("q4_gp_percent") or gp_percent

                    # Calculate GP$ from actual quarterly sales
                    q1_gp_value = (
                        round(q1_sales * (q1_gp_percent or 0), 2)
                        if q1_gp_percent and q1_sales > 0
                        else 0.0
                    )
                    q2_gp_value = (
                        round(q2_sales * (q2_gp_percent or 0), 2)
                        if q2_gp_percent and q2_sales > 0
                        else 0.0
                    )
                    q3_gp_value = (
                        round(q3_sales * (q3_gp_percent or 0), 2)
                        if q3_gp_percent and q3_sales > 0
                        else 0.0
                    )
                    q4_gp_value = (
                        round(q4_sales * (q4_gp_percent or 0), 2)
                        if q4_gp_percent and q4_sales > 0
                        else 0.0
                    )
                    # Total GP$ from actual total sales
                    total_gp_value = (
                        round(total_2025_sales * (gp_percent or 0), 2)
                        if gp_percent and total_2025_sales > 0
                        else 0.0
                    )

                    # Get quarterly sales and GP% for display
                    q1_sales_display = q1_sales
                    q2_sales_display = q2_sales
                    q3_sales_display = q3_sales
                    q4_sales_display = q4_sales
                    q1_gp_percent_display = q1_gp_percent
                    q2_gp_percent_display = q2_gp_percent
                    q3_gp_percent_display = q3_gp_percent
                    q4_gp_percent_display = q4_gp_percent

            division_data.append(
                {
                    "salesperson_id": salesperson_id_val,
                    "salesperson_name": budget["salesperson_name"],
                    "customer_class": customer_class_val,
                    "group_key": group_key_val,
                    "brand": budget["brand"],
                    "item_division": item_division,
                    "division_name": division["div_desc"],
                    "effective_ratio": effective_ratio,
                    "is_custom": bool(is_custom),
                    "uses_default_ratios": bool(uses_default_ratios),
                    "q1_budget_total": q1_total,
                    "q2_budget_total": q2_total,
                    "q3_budget_total": q3_total,
                    "q4_budget_total": q4_total,
                    "total_budget_total": total_budget_total,
                    "q1_allocated": q1_allocated,
                    "q2_allocated": q2_allocated,
                    "q3_allocated": q3_allocated,
                    "q4_allocated": q4_allocated,
                    "total_allocated": total_allocated,
                    "division_ratio_2025": division_ratio_2025,
                    "total_2025_sales": total_2025_sales,
                    "q1_sales": q1_sales_display,
                    "q2_sales": q2_sales_display,
                    "q3_sales": q3_sales_display,
                    "q4_sales": q4_sales_display,
                    "gp_percent": gp_percent,
                    "q1_gp_percent": q1_gp_percent_display,
                    "q2_gp_percent": q2_gp_percent_display,
                    "q3_gp_percent": q3_gp_percent_display,
                    "q4_gp_percent": q4_gp_percent_display,
                    "q1_gp_value": q1_gp_value,
                    "q2_gp_value": q2_gp_value,
                    "q3_gp_value": q3_gp_value,
                    "q4_gp_value": q4_gp_value,
                    "total_gp_value": total_gp_value,
                    "has_budget": True,
                }
            )

        # Sort by item_division
        division_data.sort(key=lambda x: x["item_division"])

        return division_data

    def reset_all_overrides(self) -> int:
        """
        Reset all custom ratio overrides
        """
        try:
            result = self.db.exec(text("DELETE FROM division_ratio_overrides"))
            self.db.commit()
            return result.rowcount

        except Exception as e:
            self.db.rollback()
            raise e
