# Konfiguracja deploymentu

## Struktura użytkowników

- **Użytkownik deploy**: Używany przez GitHub Actions do automatycznego deploymentu
- **Inni użytkownicy**: Dodani do grupy `deploy` dla dostępu do projektu

## Krok 1: Konfiguracja katalogu projektu

Projekt powinien być przechowywany w katalogu użytkownika (np. `~/apps/ops-monitor`).

```bash
# Utwórz katalog aplikacji
sudo mkdir -p ~/apps/ops-monitor
sudo chown deploy:deploy ~/apps/ops-monitor
sudo chmod 2775 ~/apps/ops-monitor  # setgid - nowe pliki dziedziczą grupę

# Sklonuj projekt
sudo -u deploy git clone <repo-url> ~/apps/ops-monitor
```

## Krok 2: Dodaj innych użytkowników do grupy deploy

Jeśli chcesz, aby inni użytkownicy mieli dostęp do projektu:

```bash
# Dodaj użytkownika do grupy deploy
sudo usermod -aG deploy <username>

# Ustaw uprawnienia dla istniejących plików
sudo chown -R deploy:deploy ~/apps/ops-monitor
sudo chmod -R g+w ~/apps/ops-monitor
sudo find ~/apps/ops-monitor -type d -exec chmod g+s {} \;
```

**Ważne**: Po dodaniu do grupy, użytkownik musi się wylogować i zalogować ponownie.

## Krok 3: Konfiguracja uprawnień do /var/www/ops-monitor

### Opcja A: Grupa Caddy (zalecane)

```bash
# Dodaj użytkownika deploy do grupy caddy
sudo usermod -aG caddy deploy

# Ustaw właściciela i grupę
sudo chown -R caddy:caddy /var/www/ops-monitor

# Ustaw uprawnienia: właściciel i grupa mogą zapisywać, inni tylko czytać
sudo chmod -R 775 /var/www/ops-monitor

# Ustaw setgid bit, aby nowe pliki dziedziczyły grupę
sudo chmod g+s /var/www/ops-monitor
```

### Opcja B: Sudo bez hasła (alternatywa)

Jeśli powyższe nie działa, skonfiguruj sudoers:

```bash
sudo visudo
```

Dodaj linię:
```
deploy ALL=(ALL) NOPASSWD: /usr/bin/rsync, /usr/bin/mkdir
```

## Krok 4: Uprawnienia Docker (jeśli backend używa Docker)

```bash
# Dodaj użytkownika deploy do grupy docker
sudo usermod -aG docker deploy
```

## Weryfikacja

### Sprawdź uprawnienia do projektu:

```bash
# Jako użytkownik deploy lub użytkownik w grupie deploy
cd ~/apps/ops-monitor
ls -la  # Powinno działać bez błędów
```

### Sprawdź uprawnienia do /var/www/ops-monitor:

```bash
# Jako użytkownik deploy
touch /var/www/ops-monitor/test.txt
rm /var/www/ops-monitor/test.txt
```

Jeśli działa bez sudo, konfiguracja jest poprawna.

### Sprawdź członkostwo w grupach:

```bash
# Sprawdź grupy użytkownika
groups deploy
# Powinno pokazać: deploy caddy docker (lub podobne)

# Dla innych użytkowników
groups <username>
# Powinno pokazać grupę deploy
```

## Uwagi

- Po zmianie grup, użytkownicy muszą się wylogować i zalogować ponownie
- Skrypt `deploy.sh` automatycznie wykrywa, czy może zapisywać bez sudo
- GitHub Actions używa domyślnie `~/apps/ops-monitor` (czyli `~/apps/ops-monitor`)

