CREATE TABLE IF NOT EXISTS Business (
    business_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    address         TEXT,
    state           TEXT,
    city            TEXT,
    zipcode         TEXT,
    caegories       TEXT,
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
    FOREIGN KEY (business_id)   REFERENCES Business (business_id)
);

CREATE TABLE CheckIn (
    business_id     TEXT,
    day             TEXT,
    time            TIME,
    num_checkins    INTEGER,
    FOREIGN KEY (business_id) REFERENCES Business (business_id),
    PRIMARY KEY (business_id, day, time)
);


CREATE TABLE IF NOT EXISTS YelpUser (
    user_id       TEXT PRIMARY KEY,
    review_count  INTEGER DEFAULT 0
);

CREATE TABLE Category (
    category_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- CREATE TABLE BusinessCategory (
--     business_id TEXT,
--     category_id INT,
--     PRIMARY KEY (business_id, category_id),
--     FOREIGN KEY (business_id) REFERENCES Business(business_id),
--     FOREIGN KEY (category_id) REFERENCES Category(category_id)
-- );

CREATE TABLE BusinessCategoryZip (
    category_id INT,
    zipcode TEXT,
    PRIMARY KEY (category_id, zipcode),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);
