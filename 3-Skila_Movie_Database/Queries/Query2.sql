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
    ),

    t_customer_film_category AS (
      SELECT r.customer_id AS customer_id,
             ca.name AS category,
             SUM(amount) AS cat_payment,
             MAX(SUM(amount)) OVER (PARTITION BY r.customer_id ORDER BY SUM(amount) DESC) AS max
        FROM payment p
        JOIN rental r
        ON p.rental_id = r.rental_id
        JOIN inventory i
        ON r.inventory_id = i.inventory_id
        JOIN film_category fc
        ON i.film_id = fc.film_id
        JOIN category ca
        ON fc.category_id = ca.category_id
        GROUP BY 1, 2
    )

SELECT id,
       first_name || ' ' || last_name AS customer_name,
       total_payment,
       RANK() OVER (ORDER BY total_payment DESC) AS total_payment_rank,
       category AS most_paid_category
  FROM t_customer_level t1
  JOIN t_total_payment t2
  ON t1.id = t2.customer_id
  JOIN customer cu
  ON t2.customer_id = cu.customer_id
  JOIN t_customer_film_category t3
  ON cu.customer_id = t3.customer_id
  WHERE customer_level = 'VVIP' AND cat_payment = max;
