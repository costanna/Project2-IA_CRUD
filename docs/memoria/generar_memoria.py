"""Genera docs/memoria/memoria.pdf: memoria del proyecto en Arial 12.

Uso (desde la raiz del repo):
    pip install reportlab
    python docs/memoria/generar_memoria.py

Todo el texto usa Arial 12 pt (titulos en Arial negrita 12 pt) y cada
elemento (parrafos, tablas, bloques de codigo) se ajusta al ancho util
de la pagina para que nada se salga de los margenes.
"""

import os
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

OUT = Path(__file__).with_name("memoria.pdf")
FONT_DIR = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

MARGIN = 2.5 * cm
PAGE_W, PAGE_H = A4
# Ancho util: pagina menos margenes y el padding interno (6 pt) del Frame.
FRAME_W = PAGE_W - 2 * MARGIN - 12
# Espacio reservado dentro del margen inferior para el pie de pagina.
FOOTER_H = 1.2 * cm
SIZE = 12
LEADING = 16

ACCENT = colors.HexColor("#1F4E79")
GRID = colors.HexColor("#9DB3C8")
HEAD_BG = colors.HexColor("#DCE6F0")
CODE_BG = colors.HexColor("#F2F2F2")


def register_arial():
    for name, file in [
        ("Arial", "arial.ttf"),
        ("Arial-Bold", "arialbd.ttf"),
        ("Arial-Italic", "ariali.ttf"),
        ("Arial-BoldItalic", "arialbi.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
    pdfmetrics.registerFontFamily(
        "Arial",
        normal="Arial",
        bold="Arial-Bold",
        italic="Arial-Italic",
        boldItalic="Arial-BoldItalic",
    )


register_arial()

BASE = dict(fontName="Arial", fontSize=SIZE, leading=LEADING)
S = {
    "body": ParagraphStyle("body", alignment=TA_JUSTIFY, spaceAfter=8, **BASE),
    "cell": ParagraphStyle("cell", alignment=TA_LEFT, **BASE),
    "cell_code": ParagraphStyle("cell_code", alignment=TA_LEFT, wordWrap="CJK", **BASE),
    "cell_head": ParagraphStyle(
        "cell_head", alignment=TA_LEFT, **{**BASE, "fontName": "Arial-Bold"}
    ),
    "code": ParagraphStyle(
        "code", alignment=TA_LEFT, wordWrap="CJK", backColor=CODE_BG,
        borderPadding=6, leftIndent=6, rightIndent=6, spaceBefore=6,
        spaceAfter=12, **BASE,
    ),
    "h1": ParagraphStyle(
        "h1", textColor=ACCENT, spaceBefore=6, spaceAfter=10,
        **{**BASE, "fontName": "Arial-Bold"},
    ),
    "h2": ParagraphStyle(
        "h2", textColor=ACCENT, spaceBefore=10, spaceAfter=6,
        **{**BASE, "fontName": "Arial-Bold"},
    ),
    "center": ParagraphStyle("center", alignment=TA_CENTER, **BASE),
    "center_bold": ParagraphStyle(
        "center_bold", alignment=TA_CENTER, textColor=ACCENT,
        **{**BASE, "fontName": "Arial-Bold"},
    ),
    "toc1": ParagraphStyle("toc1", leftIndent=0, **BASE),
    "toc2": ParagraphStyle("toc2", leftIndent=18, **BASE),
}


class MemoriaDoc(SimpleDocTemplate):
    """Registra los titulos en el indice."""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h2"):
            level = 0 if flowable.style.name == "h1" else 1
            text = flowable.getPlainText()
            key = f"h{id(flowable)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level)
            self.notify("TOCEntry", (level, text, self.page, key))


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Arial", SIZE)
    canvas.setStrokeColor(GRID)
    canvas.line(MARGIN, MARGIN + 0.8 * cm, PAGE_W - MARGIN, MARGIN + 0.8 * cm)
    canvas.drawString(MARGIN, MARGIN + 0.1 * cm, "Academia F5 — Memoria del proyecto")
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN + 0.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


# ---------------------------------------------------------------- helpers
story = []


def h1(text):
    story.append(Paragraph(text, S["h1"]))


def h2(text):
    story.append(Paragraph(text, S["h2"]))


def p(text):
    story.append(Paragraph(text, S["body"]))


def code(text):
    html = (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace(" ", "&nbsp;").replace("\n", "<br/>")
    )
    story.append(Paragraph(html, S["code"]))


def bullets(items):
    story.append(
        ListFlowable(
            [ListItem(Paragraph(i, S["body"]), leftIndent=18) for i in items],
            bulletType="bullet", bulletFontName="Arial", bulletFontSize=SIZE,
            leftIndent=18, start="•",
        )
    )


def table(header, rows, widths, code_cols=()):
    """Tabla con anchos relativos que suman exactamente el ancho util."""
    total = sum(widths)
    col_w = [FRAME_W * w / total for w in widths]
    data = [[Paragraph(h, S["cell_head"]) for h in header]]
    for row in rows:
        data.append(
            [
                Paragraph(c, S["cell_code"] if i in code_cols else S["cell"])
                for i, c in enumerate(row)
            ]
        )
    t = Table(data, colWidths=col_w, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 10))


# ---------------------------------------------------------------- portada
story += [
    Spacer(1, 6 * cm),
    Paragraph("ACADEMIA F5", S["center_bold"]),
    Spacer(1, 8),
    Paragraph("Sistema de Gestión Académica", S["center_bold"]),
    Spacer(1, 24),
    Paragraph("Memoria del proyecto", S["center"]),
    Spacer(1, 8),
    Paragraph("API REST (FastAPI + PostgreSQL) y frontend web (React + TypeScript)",
              S["center"]),
    Spacer(1, 5 * cm),
    Paragraph("Factoría F5 — Bootcamp de Inteligencia Artificial", S["center"]),
    Spacer(1, 6),
    Paragraph("Proyecto del Módulo 1: IA-Project-CRUD", S["center"]),
    Spacer(1, 6),
    Paragraph("Autoría: costanna", S["center"]),
    Spacer(1, 6),
    Paragraph(date.today().strftime("%d/%m/%Y"), S["center"]),
    PageBreak(),
]

# ---------------------------------------------------------------- indice
h_idx = Paragraph("Índice", S["center_bold"])
story.append(h_idx)
story.append(Spacer(1, 12))
toc = TableOfContents()
toc.levelStyles = [S["toc1"], S["toc2"]]
toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ---------------------------------------------------------------- 1
h1("1. Introducción")
p(
    "Este documento es la memoria técnica del proyecto <b>Academia F5</b>. El "
    "planteamiento parte de un encargo realista: un equipo de desarrollo de una "
    "consultora tecnológica especializada en pymes recibe la petición de un centro "
    "educativo que necesita digitalizar y optimizar la gestión de estudiantes, "
    "profesores, cursos, matrículas y notas, sustituyendo las hojas de cálculo "
    "manuales con las que trabaja hoy."
)
p(
    "La solución desarrollada consta de una <b>API REST</b> construida con FastAPI "
    "sobre una base de datos relacional PostgreSQL y de un <b>frontend web</b> (SPA "
    "en React con TypeScript) que permite el uso diario del sistema sin depender de "
    "Swagger. El proyecto se ha planificado con Scrum en dos sprints de una semana, "
    "más un sprint corto de cierre tras la primera demo."
)

h1("2. Objetivos")
p(
    "El objetivo general es desarrollar una API REST y una base de datos SQL que "
    "permitan gestionar eficientemente la academia, preparando el sistema para "
    "crecer en número de cursos, usuarios y funcionalidades. De él se derivan los "
    "siguientes objetivos específicos:"
)
bullets(
    [
        "Diseñar un modelo relacional de al menos cinco tablas con relaciones "
        "1:1, 1:N y N:M e integridad referencial.",
        "Ofrecer un CRUD completo de todos los recursos, con paginación, filtros, "
        "exportación a CSV y errores HTTP semánticos.",
        "Proteger la API con autenticación JWT y control de acceso por rol "
        "(administrador, profesor y estudiante) y por propiedad de los datos.",
        "Añadir funcionalidades avanzadas: caché, notificaciones en tiempo real "
        "con WebSocket e integración con un servicio externo de email.",
        "Garantizar la calidad con una suite de tests automatizada, linters y un "
        "pipeline de integración continua.",
        "Contenerizar la aplicación con Docker y desplegarla en la nube.",
    ]
)

# ---------------------------------------------------------------- 3
h1("3. Tecnologías utilizadas")
table(
    ["Capa", "Tecnología"],
    [
        ["Backend", "Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic"],
        ["Base de datos", "PostgreSQL (producción) y SQLite (tests)"],
        ["Autenticación", "JWT (python-jose) y roles admin, teacher y student"],
        ["Tiempo real", "WebSockets (notificación de notas nuevas)"],
        ["Servicios externos", "Resend (email al estudiante cuando recibe una nota)"],
        ["Frontend", "React 18, TypeScript, Vite y React Router"],
        ["Tests", "pytest (unitarios e integración), Vitest + Testing Library, "
                  "Playwright (end-to-end)"],
        ["Calidad de código", "black, isort, flake8 y pre-commit"],
        ["CI/CD", "GitHub Actions: lint y tests con PostgreSQL real, build del "
                  "frontend y tests end-to-end"],
        ["Contenerización", "Docker y docker-compose (base de datos, backend y frontend)"],
        ["Nube", "Neon (PostgreSQL), Render (API) y Vercel (frontend)"],
    ],
    [1, 2.6],
)

# ---------------------------------------------------------------- 4
h1("4. Arquitectura del sistema")
h2("4.1. Visión general")
p(
    "El sistema sigue una arquitectura cliente-servidor. El navegador ejecuta la "
    "SPA de React, que consume la API REST mediante peticiones HTTP autenticadas "
    "con un token JWT y mantiene abierto un canal WebSocket para recibir "
    "notificaciones. La API accede a PostgreSQL a través de SQLAlchemy y, al "
    "registrar una nota, envía en segundo plano un email mediante Resend."
)
h2("4.2. Arquitectura en capas (ADR 0001)")
p(
    "El backend se organiza en cuatro capas con una única dirección de "
    "dependencia, de arriba hacia abajo:"
)
table(
    ["Capa", "Responsabilidad"],
    [
        ["routers/", "Capa HTTP: lectura de la petición, códigos de estado y "
                     "autorización por endpoint."],
        ["services/", "Lógica de negocio y orquestación: valida reglas y dispara "
                      "notificaciones."],
        ["repositories/", "Acceso a datos con el patrón Repository sobre SQLAlchemy."],
        ["models/ y schemas/", "Entidades ORM (SQLAlchemy) y DTOs de entrada y "
                               "salida (Pydantic)."],
    ],
    [1.2, 2.8],
    code_cols=(0,),
)
p(
    "Los routers nunca consultan la base de datos directamente y los servicios "
    "nunca construyen consultas a mano: usan un <i>BaseRepository</i> genérico con "
    "operaciones get, list, create, update y delete, ampliado con métodos "
    "específicos cuando es necesario. Las excepciones de dominio (NotFoundError, "
    "ConflictError, etc.) se lanzan en los servicios y se traducen a códigos HTTP "
    "en un único punto (app/exceptions.py y app/main.py)."
)
p(
    "Se descartó escribir toda la lógica en el router, porque obligaría a probarlo "
    "todo mediante tests de integración, y también el patrón Active Record, porque "
    "SQLAlchemy 2.0 favorece el patrón Data Mapper. El coste aceptado es algo más "
    "de código repetitivo a cambio de piezas pequeñas, previsibles y fáciles de "
    "testear de forma aislada."
)
h2("4.3. Estructura del repositorio")
code(
    "backend/     API REST (FastAPI)\n"
    "  app/core/          configuración, JWT, caché, logging\n"
    "  app/models/        entidades SQLAlchemy (7 tablas)\n"
    "  app/schemas/       DTOs Pydantic\n"
    "  app/repositories/  acceso a datos\n"
    "  app/services/      lógica de negocio\n"
    "  app/routers/       endpoints REST y WebSocket\n"
    "  alembic/           migraciones\n"
    "  tests/             unit/ e integration/\n"
    "frontend/    SPA React + Vite (e2e/ con Playwright)\n"
    "docs/        diagrama ER, API, Kanban, retrospectiva, ADR\n"
    ".github/workflows/ci.yml   pipeline de CI\n"
    "docker-compose.yml         stack completo con un comando"
)

# ---------------------------------------------------------------- 5
h1("5. Modelo de datos")
p(
    "La base de datos tiene siete tablas relacionadas. Existen relaciones 1:1 "
    "(User con Student y User con Teacher), 1:N (Teacher con Course, Course con "
    "Schedule y Enrollment con Grade) y una relación N:M entre Student y Course "
    "resuelta mediante la tabla Enrollment."
)
table(
    ["Tabla", "Campos principales", "Relaciones"],
    [
        ["users", "id, email (único), hashed_password, role, is_active, created_at",
         "1:1 con students y teachers"],
        ["students", "id, user_id, first_name, last_name, birth_date, phone, "
                     "enrollment_date", "1:N con enrollments"],
        ["teachers", "id, user_id, first_name, last_name, specialty, hire_date",
         "1:N con courses"],
        ["courses", "id, name, description, credits, teacher_id (opcional)",
         "1:N con schedules y enrollments"],
        ["schedules", "id, course_id, day_of_week, start_time, end_time, classroom",
         "N:1 con courses"],
        ["enrollments", "id, student_id, course_id, enrollment_date, status",
         "Tabla puente N:M; 1:N con grades"],
        ["grades", "id, enrollment_id, evaluation_name, score, date",
         "N:1 con enrollments"],
    ],
    [1, 2.2, 1.5],
)
h2("5.1. Decisiones de diseño")
bullets(
    [
        "<b>Enrollment</b> no es solo una tabla técnica: guarda también el estado "
        "de la matrícula (activa, completada o abandonada).",
        "La restricción <b>UNIQUE(student_id, course_id)</b> impide matrículas "
        "duplicadas a nivel de base de datos, no solo en la aplicación.",
        "<b>teacher_id</b> en courses admite nulos con <b>ON DELETE SET NULL</b>: si "
        "se borra un profesor, sus cursos quedan sin profesor asignado.",
        "El resto de claves foráneas usan <b>ON DELETE CASCADE</b>, porque no tiene "
        "sentido conservar horarios, matrículas o notas huérfanas.",
        "Los modelos usan tipos SQL estándar, por lo que el mismo esquema funciona "
        "en PostgreSQL (producción) y en SQLite (tests).",
        "Las migraciones se versionan con Alembic y se han verificado contra "
        "PostgreSQL real, tanto en local como en Neon.",
    ]
)

# ---------------------------------------------------------------- 6
h1("6. API REST")
p(
    "La API expone 33 endpoints REST bajo el prefijo /api/v1 y un canal WebSocket. "
    "FastAPI genera automáticamente la documentación interactiva en /docs (Swagger "
    "UI) y /redoc. Todos los endpoints, salvo /health, /auth/register y "
    "/auth/login, requieren la cabecera Authorization: Bearer &lt;token&gt;."
)
h2("6.1. Resumen de endpoints")
table(
    ["Recurso", "Método y ruta", "Roles permitidos"],
    [
        ["Auth", "POST /auth/register", "Público (student); admin para crear admin "
                                        "o teacher, salvo la primera cuenta"],
        ["Auth", "POST /auth/login", "Público; devuelve un JWT"],
        ["Auth", "GET /auth/me", "Cualquier usuario autenticado"],
        ["Estudiantes", "GET /students, GET /students/{id}", "admin, teacher"],
        ["Estudiantes", "GET /students/me", "student (perfil propio)"],
        ["Estudiantes", "GET /students/export", "admin, teacher (CSV)"],
        ["Estudiantes", "POST, PUT, DELETE /students", "admin"],
        ["Profesores", "GET /teachers", "Cualquier usuario autenticado"],
        ["Profesores", "GET /teachers/me", "teacher (perfil propio)"],
        ["Profesores", "POST, PUT, DELETE /teachers", "admin"],
        ["Cursos", "GET /courses", "Cualquier usuario autenticado; filtro "
                                   "teacher_id; respuesta cacheada"],
        ["Cursos", "GET /courses/export", "admin (CSV)"],
        ["Cursos", "POST, PUT, DELETE /courses", "admin (invalida la caché)"],
        ["Horarios", "GET /schedules", "Cualquier usuario autenticado; filtro "
                                       "course_id"],
        ["Horarios", "POST, DELETE /schedules", "admin"],
        ["Matrículas", "GET /enrollments", "Todos; cada estudiante ve las suyas y "
                                           "cada profesor, las de sus cursos"],
        ["Matrículas", "POST /enrollments", "admin; teacher en sus cursos; student "
                                            "solo a sí mismo"],
        ["Matrículas", "PUT, DELETE /enrollments/{id}", "admin; teacher en sus cursos"],
        ["Notas", "GET /grades", "Todos; filtrado por propiedad como en matrículas"],
        ["Notas", "POST /grades", "admin; teacher en sus cursos. Avisa por "
                                  "WebSocket y email"],
        ["Notas", "PUT, DELETE /grades/{id}", "admin; teacher en sus cursos"],
        ["WebSocket", "WS /ws/notifications?token=...", "Cualquier usuario "
                                                        "autenticado"],
        ["Salud", "GET /health", "Público"],
    ],
    [1.1, 1.9, 2.2],
    code_cols=(1,),
)
h2("6.2. Códigos de error")
p(
    "Todas las respuestas de error siguen el formato {\"detail\": \"mensaje\"} y "
    "usan códigos HTTP semánticos:"
)
table(
    ["Código", "Significado"],
    [
        ["401", "Token ausente o inválido, o credenciales incorrectas."],
        ["403", "Usuario autenticado sin permiso: rol incorrecto, estudiante que "
                "actúa sobre datos ajenos o profesor sobre un curso que no imparte."],
        ["404", "Recurso no encontrado."],
        ["409", "Conflicto: email o matrícula duplicados."],
        ["422", "Error de validación del cuerpo de la petición."],
        ["500", "Error inesperado del servidor (queda registrado en el log)."],
    ],
    [0.6, 4],
)

# ---------------------------------------------------------------- 7
h1("7. Seguridad: autenticación y autorización")
p(
    "La autenticación se basa en <b>JWT firmados con HS256</b> (ADR 0002). El token "
    "se emite en POST /auth/login con el flujo estándar OAuth2PasswordBearer de "
    "FastAPI e incluye como claims el email del usuario y su rol. Al no depender de "
    "sesiones en el servidor, la API puede escalar horizontalmente. Las contraseñas "
    "se guardan con hash bcrypt."
)
p(
    "La autorización por rol es declarativa: la dependencia "
    "<i>require_roles(*roles)</i> de app/deps.py se añade en la firma de cada ruta, "
    "de modo que se ve de un vistazo quién puede llamarla. El mismo JWT se reutiliza "
    "en el WebSocket, pasándolo como parámetro de la URL, ya que los navegadores no "
    "permiten enviar la cabecera Authorization en ese canal."
)
p(
    "En el tercer sprint se detectó que comprobar solo el rol dejaba huecos, así que "
    "se añadieron comprobaciones de <b>propiedad</b> de los datos:"
)
bullets(
    [
        "El registro público solo crea cuentas de estudiante; las cuentas de "
        "administrador y profesor las crea un administrador (salvo la primera).",
        "Un estudiante solo puede matricularse a sí mismo y solo ve sus propias "
        "matrículas y notas.",
        "Un profesor solo gestiona las matrículas y notas de los cursos que imparte.",
    ]
)
p(
    "Como contrapartida aceptada, un token no se puede revocar antes de que expire; "
    "por eso la expiración es corta (60 minutos por defecto, configurable). Las "
    "claves y credenciales se leen de variables de entorno con pydantic-settings y "
    "el archivo .env está excluido del control de versiones."
)

# ---------------------------------------------------------------- 8
h1("8. Funcionalidades avanzadas")
h2("8.1. Paginación, filtros y exportación a CSV")
p(
    "Los listados admiten los parámetros skip y limit y filtros por teacher_id, "
    "course_id, student_id y enrollment_id. Los estudiantes y los cursos pueden "
    "exportarse a CSV para informes externos, tanto desde la API como con un botón "
    "del frontend."
)
h2("8.2. Caché en memoria")
p(
    "El listado de cursos se guarda en una caché en memoria (TTLCache) que se "
    "invalida explícitamente al crear, editar o borrar un curso. Resultó más simple "
    "y suficiente que montar Redis para el alcance del proyecto, y está aislada en "
    "app/core/cache.py para poder sustituirla si hace falta escalar a varias "
    "instancias."
)
h2("8.3. Notificaciones en tiempo real")
p(
    "Cuando un profesor registra una nota, el estudiante conectado recibe al "
    "instante un mensaje new_grade por el WebSocket /ws/notifications. El frontend "
    "reconecta el canal automáticamente si se pierde la conexión."
)
h2("8.4. Integración con un servicio externo: Resend")
p(
    "Al registrar una nota, el estudiante recibe también un email enviado con "
    "Resend. El envío se hace en segundo plano (BackgroundTasks) después de "
    "responder, y un fallo del proveedor solo se registra en el log, sin afectar a "
    "la petición. Si no se configura RESEND_API_KEY, el envío queda desactivado. El "
    "servicio (EmailService) recibe el transporte por inyección, lo que permite "
    "testearlo sin red."
)
h2("8.5. Logging y manejo de excepciones")
p(
    "La aplicación configura un logging básico centralizado y un manejador global "
    "de excepciones que traduce los errores de dominio a respuestas HTTP coherentes "
    "y registra los errores inesperados."
)

# ---------------------------------------------------------------- 9
h1("9. Interfaz de usuario")
p(
    "El frontend es una SPA en React 18 con TypeScript, construida con Vite y React "
    "Router. Sus principales características son:"
)
bullets(
    [
        "Inicio de sesión y rutas protegidas según el rol del usuario.",
        "Panel de inicio (dashboard) con las últimas notas y las notificaciones en "
        "tiempo real.",
        "Páginas de estudiantes, profesores, cursos, horarios, matrículas y notas con "
        "CRUD completo y edición en línea en todas las tablas.",
        "Relaciones mostradas por nombre (profesor de un curso, estudiante y curso "
        "de una matrícula) en lugar de identificadores.",
        "Paginación, filtros y exportación a CSV.",
    ]
)

# ---------------------------------------------------------------- 10
h1("10. Calidad y pruebas")
table(
    ["Nivel", "Herramienta", "Alcance"],
    [
        ["Backend", "pytest", "84 tests unitarios y de integración, 97 % de "
                              "cobertura; incluye tests de permisos y del servicio "
                              "de email con transporte simulado."],
        ["Frontend", "Vitest y Testing Library", "13 tests de componentes (login y "
                                                 "CRUD)."],
        ["End-to-end", "Playwright", "3 escenarios en navegador real: login, flujo "
                                     "profesor → curso → estudiante → matrícula → "
                                     "nota, y bloqueo por rol."],
    ],
    [1, 1.3, 3],
)
p(
    "El código del backend se formatea con black e isort y se revisa con flake8. "
    "Los hooks de pre-commit ejecutan estas herramientas antes de cada commit, y el "
    "repositorio incluye .editorconfig y configuración de VS Code para mantener un "
    "estilo homogéneo."
)
p(
    "Los tests encontraron errores reales durante el desarrollo, por ejemplo una "
    "incompatibilidad entre passlib y las versiones recientes de bcrypt, o un "
    "interceptor de axios que recargaba la página de login e impedía ver el mensaje "
    "de credenciales incorrectas."
)

# ---------------------------------------------------------------- 11
h1("11. Integración continua y despliegue")
h2("11.1. Pipeline de GitHub Actions")
p("Cada push y cada pull request ejecuta tres trabajos:")
bullets(
    [
        "<b>Backend</b>: flake8, comprobación de formato con black e isort, y tests "
        "contra un PostgreSQL real.",
        "<b>Frontend</b>: lint, tests unitarios y compilación con comprobación de "
        "tipos.",
        "<b>End-to-end</b>: levanta la API y el frontend y los recorre con Playwright "
        "en Chromium.",
    ]
)
p(
    "Desde la migración del tablero a GitHub Projects, cada cambio se desarrolla en "
    "su propia rama y se integra en main mediante una pull request con el CI en "
    "verde."
)
h2("11.2. Docker")
p(
    "El archivo docker-compose.yml levanta todo el stack con un solo comando: "
    "PostgreSQL, el backend (que aplica las migraciones al arrancar) y el frontend "
    "servido como estático."
)
code("cp .env.example .env\ndocker compose up --build")
h2("11.3. Despliegue en la nube")
p(
    "Para la demo, la aplicación se desplegó con servicios gratuitos: <b>Neon</b> "
    "para PostgreSQL (con conexión agrupada), <b>Render</b> para la API a partir de "
    "la imagen Docker y un blueprint render.yaml, y <b>Vercel</b> para el frontend. "
    "El backend normaliza automáticamente la cadena de conexión de Neon y los "
    "orígenes CORS permitidos se configuran por variable de entorno. La guía "
    "completa está en docs/deployment.md."
)

# ---------------------------------------------------------------- 12
h1("12. Gestión del proyecto")
h2("12.1. Metodología y roles")
p(
    "El proyecto se ha desarrollado con una única persona como responsable técnica, "
    "pero organizado como si lo ejecutara un equipo pequeño, asumiendo "
    "explícitamente los roles de Scrum:"
)
table(
    ["Rol", "Responsabilidad"],
    [
        ["Product Owner", "Prioriza el backlog, decide qué entra en cada sprint y "
                          "acepta las historias frente a sus criterios."],
        ["Scrum Master", "Vela por el timebox, elimina bloqueos y facilita la "
                         "retrospectiva."],
        ["Desarrollo backend", "Modelo de datos, API REST, autenticación y tests."],
        ["Desarrollo frontend", "SPA en React, consumo de la API y experiencia de "
                                "usuario."],
        ["Asistente de IA", "Claude Code como pair programmer para acelerar el "
                            "scaffolding, sugerir correcciones y generar "
                            "documentación base. Toda sugerencia se revisa, se "
                            "ejecuta y se valida: el criterio final es humano."],
    ],
    [1.3, 3],
)
p(
    "Las ceremonias fueron planning al inicio de cada sprint, seguimiento diario, "
    "review contra los criterios de aceptación y retrospectiva al cierre. La "
    "definición de hecho de cada historia es: endpoint implementado, tests en verde "
    "y documentación actualizada. Las decisiones de arquitectura quedan registradas "
    "como ADR en docs/adr/."
)
h2("12.2. Sprints e historias de usuario")
table(
    ["Sprint", "Contenido", "Historias"],
    [
        ["1. Fundación", "Modelo de datos, autenticación, CRUD básico, tests y "
                         "variables de entorno.", "HU-01 a HU-06"],
        ["2. Funcionalidad avanzada", "Matrícula desde la web, notas con "
                                      "WebSocket, CSV, paginación, caché, CI, SPA y "
                                      "Docker.", "HU-07 a HU-14"],
        ["3. Cierre tras la demo", "Edición en la web, asignación de profesores, "
                                   "permisos por propiedad, email con Resend, tests "
                                   "end-to-end y horarios.", "HU-18 a HU-24"],
        ["Backlog", "Edición de horarios por el profesor, panel de estadísticas y "
                    "recuperación de contraseña.", "HU-15 a HU-17"],
    ],
    [1.4, 3, 1.1],
)
p(
    "Se completaron 21 de las 24 historias de usuario. El tablero Kanban se mantuvo "
    "en docs/kanban.md durante los sprints y después se migró a GitHub Projects, "
    "con un issue por historia."
)

# ---------------------------------------------------------------- 13
h1("13. Retrospectiva")
h2("13.1. Qué funcionó bien")
bullets(
    [
        "Definir el modelo de datos antes de escribir endpoints evitó retrabajo.",
        "La arquitectura en capas hizo que añadir endpoints fuera mecánico y fácil "
        "de testear.",
        "Escribir los tests junto con cada endpoint detectó errores reales de forma "
        "temprana.",
        "Desplegar pronto y probar la aplicación como usuario real destapó carencias "
        "que los tests no veían.",
    ]
)
h2("13.2. Qué no funcionó tan bien")
bullets(
    [
        "No fijar versiones de dependencias transitivas (bcrypt) costó una tarde de "
        "depuración.",
        "No prever el endpoint /students/me bloqueó temporalmente la matrícula de "
        "los propios estudiantes; además, el orden de declaración de rutas en "
        "FastAPI provocó errores 422 difíciles de diagnosticar.",
        "Revisar los permisos solo por rol dejó huecos de acceso a datos ajenos.",
        "El frontend se construyó inicialmente solo para el camino feliz (crear y "
        "listar) y se quedó corto frente al CRUD de la API.",
        "Configurar CORS a mano en Render requirió varias iteraciones.",
    ]
)
h2("13.3. Acciones de mejora")
bullets(
    [
        "Añadir a cada historia un criterio de aceptación de permisos: qué pasa si "
        "lo intenta otro rol u otro usuario.",
        "Decidir desde el diseño qué acciones necesita el propio usuario sobre sí "
        "mismo (/me).",
        "Mantener una lista de comprobación API frente a UI para no dejar endpoints "
        "sin pantalla.",
        "Registrar en el arranque la configuración crítica, como los orígenes CORS.",
    ]
)

# ---------------------------------------------------------------- 14
h1("14. Resultados y conclusiones")
table(
    ["Métrica", "Valor"],
    [
        ["Tablas de base de datos", "7, con migraciones versionadas en Alembic"],
        ["Endpoints", "33 REST y 1 canal WebSocket"],
        ["Tests", "84 de backend (97 % de cobertura), 13 de frontend y 3 "
                  "escenarios end-to-end"],
        ["Servicios externos", "Resend (email de notas)"],
        ["Historias completadas", "21 de 24"],
    ],
    [1.5, 3],
)
p(
    "El proyecto cubre los cuatro niveles de entrega planteados: el esencial (siete "
    "tablas relacionadas, CRUD completo, tests, Kanban, variables de entorno, "
    "logging y excepciones), el medio (Swagger, errores semánticos, CSV, paginación "
    "y filtros), el avanzado (JWT con roles y control de propiedad, caché y "
    "WebSocket) y el experto (Docker, interfaz de usuario, despliegue real en la "
    "nube e integración con un servicio externo)."
)
p(
    "Como aprendizaje principal, el despliegue temprano y los tests end-to-end "
    "resultaron tan valiosos como los tests unitarios: fueron los que revelaron que "
    "la seguridad debía comprobar la propiedad de los datos y no solo el rol, y que "
    "la interfaz debía cubrir todo lo que ofrecía la API."
)
h2("14.1. Líneas futuras")
bullets(
    [
        "Permitir a cada profesor editar los horarios de sus propios cursos.",
        "Panel de estadísticas con notas medias y ocupación de los cursos.",
        "Recuperación de contraseña por email, aprovechando la integración con "
        "Resend.",
        "Sustituir la caché en memoria por Redis si se escala a varias instancias, "
        "y añadir una lista de revocación de tokens.",
    ]
)

# ---------------------------------------------------------------- anexo
h1("Anexo. Puesta en marcha en local")
h2("Backend")
code(
    "cd backend\n"
    "python -m venv .venv\n"
    ".venv\\Scripts\\activate\n"
    "pip install -r requirements.txt\n"
    "cp .env.example .env\n"
    "alembic upgrade head\n"
    "uvicorn app.main:app --reload"
)
h2("Frontend")
code("cd frontend\nnpm install\ncp .env.example .env\nnpm run dev")
h2("Tests")
code(
    "cd backend && pip install -r requirements-dev.txt && pytest\n"
    "cd frontend && npm run test\n"
    "cd frontend && npx playwright install chromium && npm run test:e2e"
)
p(
    "Con el servidor en marcha, la documentación interactiva está en "
    "http://localhost:8000/docs. La primera cuenta del sistema puede registrarse "
    "como administrador; las siguientes cuentas de administrador o profesor las "
    "crea un administrador."
)


def build():
    doc = MemoriaDoc(
        str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN + FOOTER_H,
        title="Academia F5 — Memoria del proyecto", author="costanna",
    )
    doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF generado en {OUT}")


if __name__ == "__main__":
    build()
