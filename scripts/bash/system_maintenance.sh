#!/bin/bash
# System Maintenance Script for Linux/macOS
# Performs system cleanup and updates

echo "🔧 OmniTasker System Maintenance"
echo "================================"

# Update package lists (requires sudo)
echo "📦 Updating package lists..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
elif command -v yum &> /dev/null; then
    sudo yum check-update
elif command -v brew &> /dev/null; then
    brew update
fi

# Clean temporary files
echo "🧹 Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Clean old logs
echo "📋 Cleaning old logs..."
find /var/log -type f -name "*.log" -mtime +30 -delete 2>/dev/null || true

# Disk usage report
echo "💾 Disk Usage Report:"
df -h | grep -E '^/dev/'

echo "✅ System maintenance completed!"
