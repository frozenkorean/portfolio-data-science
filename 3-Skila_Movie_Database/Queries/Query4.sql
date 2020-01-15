WITH top_countries AS (
      SELECT c.country_id AS country_id,
             c.country AS customer_country,
             COUNT(cu.customer_id)
        FROM country c
        JOIN city ci
        ON c.country_id = ci.country_id
        JOIN address a
        ON ci.city_id = a.city_id
        JOIN customer cu
        ON a.address_id = cu.address_id
        GROUP BY 1
        HAVING COUNT(*) >= 20
     ),

     country_payment AS (
       SELECT customer_country,
              cu.customer_id,
              DATE_PART('year', payment_date) AS payment_year,
              DATE_PART('month', payment_date) AS payment_month,
              amount
        FROM top_countries tc
        JOIN city ci
        ON tc.country_id = ci.country_id
        JOIN address a
        ON ci.city_id = a.city_id
        JOIN customer cu
        ON a.address_id = cu.address_id
        JOIN payment p
        ON cu.customer_id = p.customer_id
     )

SELECT customer_country,
       payment_year,
       payment_month,
       SUM(amount) AS total_payment,
       SUM(amount) - LAG(SUM(amount)) OVER (PARTITION BY customer_country) AS incr_from_prev_month
  FROM country_payment
  GROUP BY 1, 2, 3
  ORDER BY 1, 2, 3;
