WITH t_num_rentals AS (
      SELECT customer_id,
             COUNT(*) num_rentals
        FROM rental
        GROUP BY customer_id
    ),

     t_num_no_returns AS (
      SELECT customer_id,
             COUNT(*) num_no_returns
        FROM rental
        WHERE return_date IS NULL
        GROUP BY customer_id
    ),

    t_total_payment AS (
      SELECT customer_id,
             SUM(amount) total_payment
        FROM payment
        GROUP BY customer_id
    ),

    t_customer_score AS (
      SELECT t1.customer_id AS id,
             num_rentals,
             NTILE(5) OVER (ORDER BY num_rentals) AS rental_quintiles,
             total_payment,
             NTILE(5) OVER (ORDER BY total_payment) AS payment_quintiles,
             num_no_returns,
             NTILE(5) OVER (ORDER BY num_rentals) + NTILE(5) OVER (ORDER BY total_payment) - num_no_returns + 1 AS customer_score
        FROM  t_num_rentals t1
        JOIN  t_total_payment t2
        ON t1.customer_id = t2.customer_id
        LEFT JOIN  t_num_no_returns t3
        ON t2.customer_id = t3.customer_id
    ),

    t_customer_level AS (
      SELECT id,
             CASE WHEN customer_score = 10 THEN 'VVIP'
                  WHEN customer_score = 9 THEN 'VIP'
                  WHEN customer_score >= 7 AND customer_score < 9 THEN 'Gold'
                  WHEN customer_score >= 4 AND customer_score < 6 THEN 'Silver'
                  ELSE 'Bronze' END AS customer_level
        FROM t_customer_score
    )

SELECT customer_level,
       COUNT(*) AS number_of_customers
  FROM t_customer_level
  GROUP BY 1
  ORDER BY 1;
