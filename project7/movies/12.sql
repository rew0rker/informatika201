SELECT title FROM stars
JOIN movies ON stars.movie_id = movies.id
JOIN people ON stars.person_id = people.id WHERE 
name IN ('Johnny Depp', 'Helena Bonham Carter')
GROUP BY movies.title HAVING COUNT(movies.title) = 2;