UPDATE Business
SET num_checkins = COALESCE((
    SELECT SUM(num_checkins)
    FROM CheckIn
    WHERE CheckIn.business_id = Business.business_id
), 0);

UPDATE Business
SET num_reviews = COALESCE((
    SELECT COUNT(*)
    FROM Review
    WHERE Review.business_id = Business.business_id
), 0),
stars = COALESCE((
    SELECT AVG(stars)
    FROM Review
    WHERE Review.business_id = Business.business_id
), 0);