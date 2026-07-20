# Zepsuty endpoint tworzenia użytkownika + martwy, równoległy stos obsługi wyjątków

| Pole | Wartość |
|---|---|
| **ID** | `012` |
| **Data** | 2026-07-20 |
| **Status** | `done` |
| **Moduł** | `backend/app/modules/users`, `backend/app/exceptions` |
| **Source** | [Code quality review](../reviews/2026-07-20-code-quality.md) |
| **Severity** | High |

## Opis zadania

Dwa niepowiązane, ale oba "High", znaleziska z code-quality review:

**1. `POST /api/users/` zawsze zwraca 500.** (`modules/users/router.py:39-51` + `modules/users/repositories.py:70-81`) — endpoint wywołuje `UserRepository.create_user()`, który bezwarunkowo rzuca `NotImplementedError` ("must be done through auth module endpoints"). Endpoint jest udokumentowany i zarejestrowany, ale zawsze 500'uje. Brak testu, który by to wyłapał.

**2. Martwy, drugi stos obsługi wyjątków.** `app/exceptions/exception_handler.py` + `custom_exceptions.py` (`AppException`/`BadRequestError`/`UnauthorizedError`/`ForbiddenError`/`NotFoundError`/`ConflictError` + ich handler) są eksportowane z `app/exceptions/__init__.py`, ale nigdy nie są zarejestrowane na aplikacji FastAPI i nigdy nie są rzucane przez żaden moduł (każdy moduł ma własną hierarchię `Exception`). Aplikacja realnie używa innego zestawu handlerów zdefiniowanych inline w `app_factory.register_exception_handlers()`. Dwie równoległe, rozjeżdżające się polityki obsługi błędów — tylko jedna jest żywa.

## Checklist

- [ ] Endpoint create user: usunąć (wraz ze schematem `UserCreate`) albo podłączyć do `auth.repositories.UserRepository.create_user` + flow hasła/zaproszenia
- [ ] Dodać test, który wyłapałby ten 500
- [ ] Usunąć osierocone `app/exceptions/exception_handler.py` + `custom_exceptions.py` (albo podłączyć je i usunąć duplikat inline w `app_factory.py`)
- [ ] Ustalić jedną bazową klasę wyjątków per moduł na przyszłość (nota w `CLAUDE.md`/`SHARED_CORE.md`)

## Weryfikacja

`POST /api/users/` albo nie istnieje, albo zwraca poprawną odpowiedź (nie 500). `grep -r "app.exceptions" backend/app/` nie zwraca odwołań do usuniętego martwego kodu.
