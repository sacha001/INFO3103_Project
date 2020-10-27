DELIMITER //
DROP PROCEDURE IF EXISTS getRides //

CREATE PROCEDURE getRides()
BEGIN
  SELECT *
    FROM rides;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getUserRides //

CREATE PROCEDURE getUserRides(uID varchar(50))
BEGIN
  SELECT *
    FROM rides
      WHERE userName = uID;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getUserRideByID //

CREATE PROCEDURE getUserRideByID(uID varchar(50), rID INT)
BEGIN
  SELECT *
    FROM rides
      WHERE userName = uID AND rideID = rID;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS createUserRide //

CREATE PROCEDURE createUserRide(uName varchar(50), sLoc varchar(256), dTime varchar(256), dest varchar(256), seats INT, WorF INT)
BEGIN
  INSERT INTO rides (userName, startLocation, departureTime, destination, seats, wantedOrAvaialbeFlag) VALUES
  (uName, sLoc, dTime, dest, seats, WorF);
  SELECT LAST_INSERT_ID();
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS updateStartLocation //

CREATE PROCEDURE updateStartLocation(sLoc varchar(256), id INT)
BEGIN
  UPDATE rides
    SET startLocation = sLoc WHERE rideID = id;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS updateDepartureTime //

CREATE PROCEDURE updateDepartureTime(dTime varchar(256), id INT)
BEGIN
  UPDATE rides
    SET departureTime = dTime WHERE rideID = id;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS updateDestination //

CREATE PROCEDURE updateDestination(dest varchar(256), id INT)
BEGIN
  UPDATE rides
    SET destination = dest WHERE rideID = id;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS updateSeats //

CREATE PROCEDURE updateSeats(sNum INT, id INT)
BEGIN
  UPDATE rides
    SET seats = sNum WHERE rideID = id;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS removeUserRide //

CREATE PROCEDURE removeUserRide(rID INT)
BEGIN
  DELETE
    FROM rides
      WHERE rideId = rID;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getRidesByFlag //

CREATE PROCEDURE getRidesByFlag(flag INT)
BEGIN
  SELECT *
    FROM rides
      WHERE wantedOrAvaialbeFlag = flag;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getRidesByDepartFrom //

CREATE PROCEDURE getRidesByDepartFrom(departFrom varchar(256))
BEGIN
  SELECT *
    FROM rides
      WHERE startLocation = departFrom;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getRidesByDestination //

CREATE PROCEDURE getRidesByDestination(dest varchar(256))
BEGIN
  SELECT *
    FROM rides
      WHERE destination = dest;
END //
DELIMITER ;
