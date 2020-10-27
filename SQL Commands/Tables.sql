DROP TABLE IF EXISTS rides;
CREATE TABLE rides (
  rideId  INT NOT NULL AUTO_INCREMENT,
  userName  varchar(50) NOT NULL,
  startLocation varchar(256) NOT NULL,
  departureTime varchar(256)  NOT NULL,
  destination varchar(256)   NULL NULL,
  seats INT NOT NULL,
  wantedOrAvaialbeFlag INT NOT NULL,
  PRIMARY KEY (rideId)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userName varchar(50) NOT NULL,
  name varchar(50) NOT NULL,
  PRIMARY KEY (userName)
);

DROP TABLE IF EXISTS ride_passenger;
CREATE TABLE ride_passenger (
  userName varchar(50) NOT NULL,
  rideId INT NOT NULL
);
