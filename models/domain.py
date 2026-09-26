from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    username: str
    rol: str
    activo: int | str
    id: Optional[int] = None

@dataclass
class Alumno:
    matricula: str
    nombre: str
    correo: str
    grupo: str
    activo: int | str = 1
    id: Optional[int] = None

@dataclass
class Materia:
    clave: str
    nombre: str
    creditos: int
    activo: int | str = 1
    id: Optional[int] = None

@dataclass
class Calificacion:
    alumno_id: int
    materia_id: int
    periodo: str
    nota: float
    id: Optional[int] = None
