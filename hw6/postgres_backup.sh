#!/bin/bash

# Конфигурация
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="postgres"
DATABASES=("app_db" "auth_db" "postgre")  # Список баз данных для бэкапа

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка подключения к PostgreSQL
check_postgres_connection() {
    if ! pg_isready -h $PG_HOST -p $PG_PORT -U $PG_USER > /dev/null 2>&1; then
        log "ERROR: Невозможно подключиться к PostgreSQL"
        exit 1
    fi
}

# Бэкап всех баз данных
backup_all_databases() {
    log "Начало резервного копирования PostgreSQL"
    
    for DB in "${DATABASES[@]}"; do
        BACKUP_FILE="$BACKUP_DIR/${DB}_${DATE}.dump"
        log "Бэкап базы данных: $DB"
        
        if pg_dump -h $PG_HOST -p $PG_PORT -U $PG_USER -F c -b -v -f "$BACKUP_FILE" "$DB"; then
            log "Успешно создан бэкап: $BACKUP_FILE"
            
            # Сжатие бэкапа
            gzip "$BACKUP_FILE"
            log "Бэкап сжат: ${BACKUP_FILE}.gz"
            
            # Проверка целостности
            if gzip -t "${BACKUP_FILE}.gz"; then
                log "Целостность бэкапа проверена"
            else
                log "ERROR: Бэкап поврежден"
            fi
        else
            log "ERROR: Ошибка при создании бэкапа для $DB"
        fi
    done
}

# Очистка старых бэкапов
clean_old_backups() {
    log "Очистка бэкапов старше $RETENTION_DAYS дней"
    find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete
    log "Очистка завершена"
}

# Основная функция
main() {
    log "=== Запуск скрипта бэкапа PostgreSQL ==="
    check_postgres_connection
    backup_all_databases
    clean_old_backups
    log "=== Завершение скрипта бэкапа ==="
}

# Запуск основной функции
main 2>&1 | tee -a "$BACKUP_DIR/backup.log"
