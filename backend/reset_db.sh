#!/bin/sh
set -e

echo "Stopping all services and removing volumes..."
docker compose down -v

echo "Clearing uploads directory..."
rm -rf uploads/*
mkdir -p uploads

echo "Recreating services..."
docker compose up -d postgres qdrant

echo "Waiting for databases to be ready..."
sleep 10

echo "Running Alembic migrations..."
alembic upgrade head

echo "Reset complete!" 