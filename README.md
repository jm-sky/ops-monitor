# ops-monitor

**Lightweight, self-hosted monitoring system for servers, services, and applications.**

---

## 🎯 Cel projektu
Agent to lekka aplikacja uruchamiana na każdej maszynie wirtualnej (VM), której zadaniem jest zbieranie i udostępnianie informacji o stanie systemu, usług i kontenerów. Dane te będą cyklicznie pobierane przez centralny **Dashboard** i prezentowane w formie wizualnego panelu.

---

## 🧩 Architektura

### Komponenty

#### 1. Agent (na każdej VM)
- Implementacja: **FastAPI (Python)**
- Wystawia endpointy HTTP:
  - `/health` → ogólny stan VM (`OK`, `Degraded`, `Down`)
  - `/metrics` → szczegółowe dane systemowe, serwisy, kontenery, aktualizacje, restart
  - `/apps` (opcjonalnie) → metryki i statusy aplikacji działających na tej VM

#### 2. Dashboard (centralny)
- Backend: **FastAPI**
- Frontend: **Vue.js 3**
- Zadania:
  - Odpytuje agentów (polling co X sekund)
  - Gromadzi dane o VM, usługach, kontenerach, aplikacjach
  - Udostępnia dane przez REST API i WebSocket/SSE
  - Prezentuje statusy, alerty i metryki

---

## ⚙️ Zakres danych zwracanych przez Agenta

### Endpoint `/metrics` — przykład danych
```json
{
  "vm": {
    "hostname": "api-01",
    "status": "OK",
    "uptime": 182340,
    "cpu_usage": 23.5,
    "ram_usage": 61.2,
    "disk_free_gb": 124.7,
    "is_restart_needed": true,
    "security_updates_available": 3
  },
  "services": [
    {"name": "JIRA-Importer", "status": "active", "uptime_seconds": 56200},
    {"name": "Cleanup-Service", "status": "active", "uptime_seconds": 89200}
  ],
  "containers": [
    {"name": "SaasBase", "status": "running", "image": "php:latest", "uptime_seconds": 23400}
  ],
  "apps": [
    {
      "name": "DEV Made IT",
      "health_url": "https://dev-made.it/api/health",
      "status": "OK",
      "metrics": {"errors_last_8h": 12}
    }
  ]
}
```

---

## 🧠 Logika pozyskiwania danych

### System
- CPU, RAM, dysk: `psutil`
- Uptime: `/proc/uptime`
- Restart required: plik `/var/run/reboot-required`
- Security updates:
  ```bash
  apt list --upgradable 2>/dev/null | grep -c security
  ```
- Status VM: `OK` / `Degraded` / `Down` (na podstawie metryk)

### Services
- Typy: `systemd` lub `docker`
- Status:
  - `systemctl is-active <name>`
  - `docker inspect -f '{{.State.Status}}' <container>`

### Applications
- Health check: `GET <health_url>` → status `OK`/`Unhealthy`/`Down`
- Metryki: opcjonalne endpointy `/metrics`

---

## 🗄️ Proponowany model danych (Dashboard side)

### VM
- `id`
- `name`
- `hostname`
- `agent_url`
- `status` (OK / Down / Degraded)
- `cpu_usage`
- `ram_usage`
- `disk_free_gb`
- `is_restart_needed`
- `security_updates_available`
- `last_seen_at`

### Service
- `id`
- `vm_id`
- `name`
- `type` (systemd | docker)
- `status`
- `uptime_seconds`

### Container
- `id`
- `vm_id`
- `name`
- `image`
- `status`
- `uptime_seconds`

### Application
- `id`
- `name`
- `vm_id` (nullable)
- `health_url`
- `status`
- `metrics` (JSON)
- `last_checked_at`

---

## 🚦 Status logiczny

| Warunek | Status |
|----------|---------|
| Odpowiedź OK, metryki w normie | `OK` |
| Agent działa, ale np. `is_restart_needed = true` lub `security_updates_available > 0` | `Degraded` |
| Brak odpowiedzi lub timeout | `Down` |

---

## 🔐 Przyszłe rozszerzenia
- Autoryzacja komunikacji agent ↔ dashboard (np. JWT / API key)
- Historia metryk (InfluxDB lub PostgreSQL + retention)
- Alerty (e-mail, Slack, Teams, Webhook)
- Konfiguracja agentów z poziomu Dashboardu (push)
- Auto-discovery kontenerów i usług

---

## 🗂️ Przykładowa konfiguracja agenta (YAML)
```yaml
services:
  - name: "JIRA Integration"
    systemd: "jira-integration.service"
containers:
  - name: "SaasBase"
    container_name: "saasbase-app"
apps:
  - name: "DEV Made IT"
    health_url: "https://dev-made.it/api/health"
    metrics_url: "https://dev-made.it/api/metrics"
```

---

**Stack:** FastAPI, Python, psutil, systemctl, Docker SDK, Vue.js 3  
**Cel:** Lightweight, self-hosted monitoring for internal services
