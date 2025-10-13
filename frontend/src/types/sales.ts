export interface Sale {
    id?: number;
    brand: string;
    flag: string;
    customer_name: string;
    derived_customer_class: string;
    q1_sales: number;
    q2_sales: number;
    q3_sales: number;
    q4_sales: number;
    zero_perc_sales_total: number;
    total_sales: number;
    zero_perc_sales_percent: number;
}

export interface Budget {
    id?: number;
    salesperson_id: string;
    salesperson_name: string;
    brand: string;
    flag: string;
    customer_name: string;
    customer_class: string;
    quarter_1_sales: number;
    quarter_2_sales: number;
    quarter_3_sales: number;
    quarter_4_sales: number;
}


export interface User {
    username: string;
    id?: number;
}

export interface Salesperson {
    salesman_no: string;
    salesman_name: string;
    role: string;
}
