# Diagrama Entidad-Relación — Academia F5

7 tablas, con relaciones 1:1 (`User`↔`Student`, `User`↔`Teacher`), 1:N
(`Teacher`→`Course`, `Course`→`Schedule`, `Enrollment`→`Grade`) y N:M
(`Student`↔`Course` a traves de `Enrollment`).

```mermaid
erDiagram
    USER ||--o| STUDENT : "tiene perfil"
    USER ||--o| TEACHER : "tiene perfil"
    TEACHER ||--o{ COURSE : imparte
    COURSE ||--o{ SCHEDULE : tiene
    STUDENT ||--o{ ENROLLMENT : se_matricula
    COURSE ||--o{ ENROLLMENT : recibe
    ENROLLMENT ||--o{ GRADE : acumula

    USER {
        int id PK
        string email UK
        string hashed_password
        enum role "admin | teacher | student"
        bool is_active
        datetime created_at
    }

    STUDENT {
        int id PK
        int user_id FK
        string first_name
        string last_name
        date birth_date
        string phone
        datetime enrollment_date
    }

    TEACHER {
        int id PK
        int user_id FK
        string first_name
        string last_name
        string specialty
        datetime hire_date
    }

    COURSE {
        int id PK
        string name
        string description
        int credits
        int teacher_id FK "nullable"
    }

    SCHEDULE {
        int id PK
        int course_id FK
        enum day_of_week
        time start_time
        time end_time
        string classroom
    }

    ENROLLMENT {
        int id PK
        int student_id FK
        int course_id FK
        datetime enrollment_date
        enum status "active | completed | dropped"
    }

    GRADE {
        int id PK
        int enrollment_id FK
        string evaluation_name
        float score
        datetime date
    }
```

## Notas de diseno

- **`Enrollment` es la tabla puente** de la relacion N:M entre `Student` y
  `Course`; ademas guarda el `status` de la matricula (activa, completada,
  abandonada), asi que modela tambien un caso de negocio, no solo una
  relacion tecnica.
- Restriccion `UNIQUE(student_id, course_id)` en `enrollments` evita
  matriculas duplicadas a nivel de base de datos (no solo en la capa de
  aplicacion).
- `teacher_id` en `courses` es nullable con `ON DELETE SET NULL`: si se
  borra un profesor, sus cursos no desaparecen, quedan "sin profesor
  asignado".
- El resto de claves foraneas usan `ON DELETE CASCADE` porque no tiene
  sentido conservar horarios, matriculas o notas huerfanas.
- Los modelos (`backend/app/models/`) usan tipos SQL estandar (no
  especificos de PostgreSQL), por lo que el mismo esquema es valido tanto
  en PostgreSQL (produccion) como en SQLite (tests).
