DELIMITER //
DROP PROCEDURE IF EXISTS createUser //

CREATE PROCEDURE createUser(uName varchar(50), n varchar(50))
BEGIN
  INSERT INTO users (userName, name) VALUES
  (uName, n);
  SELECT LAST_INSERT_ID();
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getUsers //

CREATE PROCEDURE getUsers()
BEGIN
  SELECT *
    FROM users;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getUser //

CREATE PROCEDURE getUser(uName varchar(50))
BEGIN
  SELECT *
    FROM users WHERE userName = uName;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS deleteUser //

CREATE PROCEDURE deleteUser(uName varchar(50))
BEGIN
  DELETE
    FROM users WHERE userName = uName;
END //
DELIMITER ;
