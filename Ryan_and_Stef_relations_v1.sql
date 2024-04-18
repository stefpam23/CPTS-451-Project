CREATE DATABASE YelpData;
CREATE TABLE IF NOT EXISTS Business (
    business_name   TEXT NOT NULL,
    business_id     TEXT PRIMARY KEY,
    isOpen          BOOLEAN NOT NULL,
    category        TEXT[],
    address         TEXT,
    city            TEXT,
    state           TEXT
);

CREATE TABLE IF NOT EXISTS YelpUser (
    user_id         TEXT PRIMARY KEY,
    review_count    INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS Review (
    review_id       TEXT,
    user_id         TEXT,
    business_id     TEXT,
    rating          FLOAT NOT NULL,
    PRIMARY KEY (review_id, user_id, business_id)
    FOREIGN KEY (business_id)   REFERENCES Business (business_id),
    FOREIGN KEY (user_id)       REFERENCES YelpUser (user_id)
);

CREATE TABLE CheckIn (
    business_id     TEXT,
    day             TEXT,
    hour            TIME,
    num_checkins    INTEGER
    PRIMARY KEY (business_id)
    FOREIGN KEY (business_id)   REFERENCES Business (business_id)
);