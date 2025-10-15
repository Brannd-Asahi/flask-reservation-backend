-- Crear BD (si no existe)
CREATE DATABASE IF NOT EXISTS hostal_tucan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hostal_tucan;

-- Tabla perfil
CREATE TABLE IF NOT EXISTS perfil (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla usuario
CREATE TABLE IF NOT EXISTS usuario (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  correo VARCHAR(150) NOT NULL UNIQUE,
  clave VARCHAR(255) NOT NULL,
  perfil_id INT,
  FOREIGN KEY (perfil_id) REFERENCES perfil(ID) ON DELETE SET NULL
);

-- Tabla cliente (simple)
CREATE TABLE IF NOT EXISTS cliente (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);

-- Tabla supervisor (simple)
CREATE TABLE IF NOT EXISTS supervisor (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);

-- Tabla reserva
CREATE TABLE IF NOT EXISTS reserva (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  fecha DATE NOT NULL,
  cliente_id INT NOT NULL,
  supervisor_id INT DEFAULT NULL,
  FOREIGN KEY (cliente_id) REFERENCES cliente(ID) ON DELETE CASCADE,
  FOREIGN KEY (supervisor_id) REFERENCES supervisor(ID) ON DELETE SET NULL
);

-- Insertar perfiles iniciales (IDs conocidos: 1 admin, 2 supervisor, 3 empleado, 4 cliente)
INSERT IGNORE INTO perfil (ID, nombre) VALUES
(1, 'Administrador'), (2, 'Supervisor'), (3, 'Empleado'), (4, 'Cliente');
