DELIMITER //
DROP PROCEDURE IF EXISTS addPassenger //

CREATE PROCEDURE addPassenger(rID INT, uName varchar(50))
BEGIN
  INSERT INTO ride_passenger(rideID, userName)
    VALUES (rID, uName);
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getRidePassengers //

CREATE PROCEDURE getRidePassengers(rID INT)
BEGIN
  SELECT users.userName, users.name, ride_passenger.rideID FROM users
    INNER JOIN ride_passenger
      ON users.userName = ride_passenger.userName
        AND ride_passenger.rideID = rID;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getSpecificPassenger //

CREATE PROCEDURE getSpecificPassenger(uName varchar(50), rID INT)
BEGIN
  SELECT users.userName, users.name, ride_passenger.rideID FROM users
    INNER JOIN ride_passenger
      ON users.userName = ride_passenger.userName
        AND ride_passenger.rideID = rID WHERE ride_passenger.userName = uName;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS deleteSpecificPassenger //

CREATE PROCEDURE deleteSpecificPassenger(uName varchar(50), rID INT)
BEGIN
  DELETE FROM ride_passenger WHERE userName = uName AND rideId = rID;
END //
DELIMITER ;
