CREATE TABLE IF NOT EXISTS Business (
    business_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    address         TEXT,
    state           TEXT,
    city            TEXT,
    zipcode         TEXT,
    stars           FLOAT DEFAULT 0.0,
    num_reviews     INTEGER DEFAULT 0,
    num_checkins    INTEGER DEFAULT 0,
    is_open         BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Review (
    review_id       TEXT,
    business_id     TEXT,
    stars           FLOAT DEFAULT 0,
    text            TEXT,
    PRIMARY KEY (review_id, business_id),
    FOREIGN KEY (business_id) REFERENCES Business (business_id)
);

CREATE TABLE IF NOT EXISTS CheckIn (
    business_id     TEXT,
    day             TEXT,
    time            TIME,
    num_checkins    INTEGER,
    PRIMARY KEY (business_id, day, time),
    FOREIGN KEY (business_id) REFERENCES Business (business_id)
);

CREATE TABLE IF NOT EXISTS YelpUser (
    user_id       TEXT PRIMARY KEY,
    review_count  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Category (
    category_id   SERIAL PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS ZipcodeStats (
    zipcode VARCHAR(5) PRIMARY KEY,
    medianIncome INT,
    meanIncome INT,
    population INT
);


CREATE TABLE IF NOT EXISTS BusinessCategory (
    business_id    TEXT NOT NULL,
    category_id    INTEGER NOT NULL,
    PRIMARY KEY (business_id, category_id),
    FOREIGN KEY (business_id) REFERENCES Business (business_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Category (category_id) ON DELETE CASCADE
);


-- Example: Filtering businesses in a specific city and category
SELECT 
    b.business_id,
    b.name,
    b.address,
    b.city,
    b.state,
    b.zipcode,
    b.stars,
    b.num_reviews,
    b.num_checkins,
    c.name AS category_name
FROM 
    Business b
JOIN 
    BusinessCategory bc ON b.business_id = bc.business_id
JOIN 
    Category c ON bc.category_id = c.category_id
WHERE
    b.city = 'Las Vegas' AND c.name = 'Restaurants'
ORDER BY 
    b.business_id, c.name;
