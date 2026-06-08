SET GLOBAL validate_password.policy=LOW;
SET GLOBAL validate_password.length=4;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
