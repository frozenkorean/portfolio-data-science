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

     customer_actor AS (
       SELECT r.customer_id AS customer_id,
              ac.actor_id AS actor_id,
              ac.first_name || ' ' || ac.last_name AS actor_name
         FROM rental r
         JOIN inventory i
         ON r.inventory_id = i.inventory_id
         JOIN film f
         ON i.film_id = f.film_id
         JOIN film_actor fa
         ON f.film_id = fa.film_id
         JOIN actor ac
         ON fa.actor_id = ac.actor_id
     ),

     country_actor AS (
       SELECT tc.country_id,
              customer_country,
              actor_id,
              actor_name,
              COUNT(*) actor_count,
              MAX(COUNT(*)) OVER (PARTITION BY customer_country) max_actor_count
        FROM top_countries tc
        JOIN city ci
        ON tc.country_id = ci.country_id
        JOIN address a
        ON ci.city_id = a.city_id
        JOIN customer cu
        ON a.address_id = cu.address_id
        JOIN customer_actor ca
        ON cu.customer_id = ca.customer_id
        GROUP BY 1, 2, 3, 4
        ORDER BY 2, 5 DESC
     )

SELECT customer_country,
       actor_id,
       actor_name
  FROM country_actor
  WHERE actor_count = max_actor_count;
