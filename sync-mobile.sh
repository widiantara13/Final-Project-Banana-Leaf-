#!/bin/bash
# Script praktis untuk menyalin update Mobile dari Windows Desktop ke WSL
echo "Menyinkronkan file Mobile dari Windows Desktop ke WSL..."
rsync -av \
  --exclude "build/" \
  --exclude ".dart_tool/" \
  --exclude ".idea/" \
  --exclude "*.log" \
  --exclude "windows/flutter/ephemeral/" \
  "/mnt/c/Users/Yoga Widiantara/Desktop/Mobile/" "/home/yoga/Final Project/Mobile/"

rm -rf "/home/yoga/Final Project/Mobile/windows/flutter/ephemeral"
echo "✅ Sinkronisasi selesai! Siap untuk git commit & git push."

